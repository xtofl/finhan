import csv
from datetime import datetime
from typing import Iterable, Sequence, Tuple

from finhan.transaction import Transaction


def bepost_format_choose(line, dirty, clean):
    if "ancontact" in line:
        return dirty

    return clean


def _account(row: Sequence[str]):
    return row[1]


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _regular_parser(account, header_row: Sequence[str]):
    def index_of(s):
        return next(i for i, n in enumerate(header_row) if n == s)

    def extract(convert, i):
        return lambda r: convert(r[i])

    target = extract(str, index_of("Rekening tegenpartij :"))
    amount = extract(_belgian_float, index_of("Bedrag van de verrichting"))
    date = extract(parse_date, index_of("Transactie datum"))
    message = extract(str, index_of("Mededeling"))

    def f(row: Sequence[str]):
        return Transaction(
            source=account,
            target=target(row),
            amount=amount(row),
            date=date(row),
            message=message(row),
        )

    return f


def _try_all(functions: dict):
    def combined(row: Sequence[str]):
        key = row[2]
        return functions[key](row)

    return combined


Account = str


def _transactions(
    lines: Iterable[str],
) -> Tuple[Iterable[Transaction], Account]:
    reader = csv.reader(lines, delimiter=";")
    it = iter(reader)
    account = _account(row=next(it))
    regular = _regular_parser(account, header_row=next(it))
    parser = _try_all(
        {
            "Uw doorlopende betalingsopdracht": regular,
            "Domiciliëring - opneming": regular,
            "Uw overschrijving": regular,
            "Overschrijving in uw voordeel": regular,
            "Instant overschr. te uwen gunste": regular,
            "Kosten- en interestberekening": regular,
            "Maestro-betaling": regular,
            "Rekeningverzekering": regular,
            "Overschr. (met getrouwheidspr.)": regular,
            "Opneming Bancontact": _parser_for_bancontact_opneming(account),
            "Bancontact-betaling": _parser_for_bancontact_betaling(account),
        }
    )
    return map(parser, filter(lambda n: len(n) > 2, reader)), account


def from_lines(lines: Iterable[str]) -> Tuple[Iterable[Transaction], Account]:
    return _transactions(lines)


def just(what):
    return lambda *args: what


def _parser_for_bancontact_opneming(account):
    def parse(row):
        if row[2] != "Opneming Bancontact":
            raise ValueError("Geen bancontact opneming")
        return Transaction(
            date=parse_date(row[1]),
            source=account,
            target=row[10],
            amount=_belgian_float(row[3]),
            message="bancontact geldopneming",
        )

    return parse


def _belgian_float(c):
    return float(c.replace(",", "."))


def _parser_for_bancontact_betaling(account):
    def parse(row):
        if row[2] != "Bancontact-betaling":
            raise ValueError("Geen bancontact betaling")

        return Transaction(
            date=parse_date(row[1]),
            source=account,
            target=row[10],
            amount=_belgian_float(row[3]),
            message=f"bancontact betaling",
        )

    return parse
