from datetime import datetime

from .csv_transactions import from_lines
from ..transaction import Transaction


def test_bancontact_records_are_parsed_separately():
    preamble = [
        "Rekeningnummer :;account;b.compact rekening",
        "Nummer van de verrichting;Transactie datum;Beschrijving;Bedrag van de verrichting;Munt;Valuta datum;Rekening tegenpartij :;Naam tegenpartij;Mededeling;Referentie van de verrichting",
    ]
    bancontact_sample = "75;2020-04-06;Opneming Bancontact;-80;EUR;06/04/2020; ;B0456A78        WHEREEVER;20200404 14:59:04 ; Carte/Kaart : 0505050505050 ;TermID : B0456A78;C0D06AG03V0001VY;"
    lines = preamble + [bancontact_sample]
    bancontact_record: Transaction = next(from_lines(lines)[0])
    assert bancontact_record.source == "account"


def test_columns_are_well_read(sample):
    transactions, account = from_lines(sample.split("\n"))
    transactions = tuple(transactions)  # easier to debug
    expected = (
        Transaction(
            date=datetime(year=2021, month=1, day=18),
            source="BE0123456789",
            target="BE11405050461148",
            amount=-70.48,
            message="+++149/8960/18071+++ ",
        ),
        Transaction(
            date=datetime(year=2021, month=1, day=18),
            source="BE0123456789",
            target="BE654987654321",
            amount=-99,
            message="+++681/0352/57232+++ ",
        ),
    )

    assert set(expected) < set(transactions)
