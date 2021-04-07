from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Iterable, Sequence, Tuple, Callable, Dict, Any

from finhan.transaction import Transaction


def bepost_format_choose(line, dirty, clean):
    if "ancontact" in line:
        return dirty

    return clean


def _account(row: Sequence[str]):
    return row[1]


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _regular_parser(account, header_row: Sequence["BePostRow"]):

    target = extractor(str, header_row.index_of("Rekening tegenpartij :"))
    amount = extractor(
        _belgian_float, header_row.index_of("Bedrag van de verrichting")
    )
    date = extractor(parse_date, header_row.index_of("Transactie datum"))
    message = extractor(str, header_row.index_of("Mededeling"))

    def f(row: Sequence[str]):
        return Transaction(
            source=account,
            target=target(row),
            amount=amount(row),
            date=date(row),
            message=message(row),
        )

    return f


def _by_type(
    functions: Dict["BePostTransactionType", Callable[["BePostRow"], Any]]
) -> Callable[["BePostRow"], Any]:
    def combined(row: "BePostRow"):
        key = row.transaction_type()
        return functions[key](row)

    return combined


Account = str


def _transactions(
    lines: Iterable[str],
) -> Tuple[Iterable[Transaction], Account]:
    it = bepost_rows(lines)
    account = _account(row=next(it))
    regular = _regular_parser(account, header_row=next(it))
    bancontact_withdrawal = _parser_for_bancontact_opneming(account)
    bancontact_payment = _parser_for_bancontact_betaling(account)
    parser = _by_type(
        {
            BePostTransactionType.REGULAR: regular,
            BePostTransactionType.BANCONTACT_WITHDRAWAL: bancontact_withdrawal,
            BePostTransactionType.BANCONTACT_PAYMENT: bancontact_payment,
        }
    )
    return map(parser, filter(lambda n: len(n) > 2, it)), account


def from_lines(lines: Iterable[str]) -> Tuple[Iterable[Transaction], Account]:
    return _transactions(lines)


def just(what):
    return lambda *args: what


def _parser_for_bancontact_opneming(account):
    def parse(row: BePostRow):
        if (
            row.transaction_type()
            != BePostTransactionType.BANCONTACT_WITHDRAWAL
        ):
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
    def parse(row: BePostRow):
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


class BePostTransactionType(Enum):
    BANCONTACT_PAYMENT = 1
    BANCONTACT_WITHDRAWAL = 2
    REGULAR = 10


BePostTransactionType_MAP = {
    "Uw doorlopende betalingsopdracht": BePostTransactionType.REGULAR,
    "Domiciliëring - opneming": BePostTransactionType.REGULAR,
    "Uw overschrijving": BePostTransactionType.REGULAR,
    "Overschrijving in uw voordeel": BePostTransactionType.REGULAR,
    "Instant overschr. te uwen gunste": BePostTransactionType.REGULAR,
    "Kosten- en interestberekening": BePostTransactionType.REGULAR,
    "Maestro-betaling": BePostTransactionType.REGULAR,
    "Rekeningverzekering": BePostTransactionType.REGULAR,
    "Overschr. (met getrouwheidspr.)": BePostTransactionType.REGULAR,
    "Opneming Bancontact": BePostTransactionType.BANCONTACT_WITHDRAWAL,
    "Bancontact-betaling": BePostTransactionType.BANCONTACT_PAYMENT,
}


@dataclass
class BePostRow:
    cells: Tuple[str]

    def __getitem__(self, item: int) -> str:
        return self.cells[item]

    def __len__(self):
        return len(self.cells)

    def transaction_type(self) -> BePostTransactionType:
        return BePostTransactionType_MAP[self.cells[2]]

    @staticmethod
    def transaction_type_is(
        t: BePostTransactionType,
    ) -> Callable[["BePostRow"], bool]:
        def _equal(b: "BePostRow") -> bool:
            return b.transaction_type() == t

        return _equal

    def index_of(self, s: str) -> int:
        return next(i for i, n in enumerate(self.cells) if n == s)


def extractor(convert: Callable, i: int):
    return lambda r: convert(r[i])


def bepost_rows(lines: Iterable[str]) -> Iterable[BePostRow]:
    return (BePostRow(line.split(";")) for line in lines)
