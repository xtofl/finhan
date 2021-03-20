from datetime import datetime

import pytest

from .csv_transactions import from_lines
from ..transaction import Transaction

SAMPLE = """Rekeningnummer :;BE0123456789;b.compact rekening
Nummer van de verrichting;Transactie datum;Beschrijving;Bedrag van de verrichting;Munt;Valuta datum;Rekening tegenpartij :;Naam tegenpartij;Mededeling;Referentie van de verrichting
12;2021-01-18;Uw overschrijving;-99;EUR;18/01/2021;BE654987654321;ANOTHER PARTY;+++681/0352/57232+++ ;C1A18CWNSA7932EV;
57;2020-03-10;Bancontact-betaling;-33,15;EUR;10/03/2020; ;APOTHEEK BBBOOLL;20200310 14:03:44 ; Carte/Kaart : 0505050505050 ;TermID : 01946432;C0C10AG03V0002PW;
11;2021-01-18;Uw overschrijving;-70,48;EUR;18/01/2021;BE11405050461148;Party 1;+++149/8960/18071+++ ;C1A18CWLXF292MY6;
10;2021-01-18;Uw overschrijving;-160,95;EUR;18/01/2021;BE11405050461148;Party 1;+++150/1906/69214+++ ;C1A18CWKOG292AWN;
84;2020-04-29;Opneming Bancontact;-80;EUR;29/04/2020; ;B0456A78        WHEREEVER;20200429 12:39:48 ; Carte/Kaart : 0505050505050 ;TermID : B0456A78;C0D29AG03I0002NJ;
9;2021-01-18;Uw overschrijving;-126;EUR;18/01/2021;BE494979796464;Party 3;+++110/0031/58881+++ ;C1A18CWHBK991H7Q;
59;2020-03-16;Opneming Bancontact;-80;EUR;16/03/2020; ;B0456A78        WHEREEVER;20200314 12:10:08 ; Carte/Kaart : 0505050505050 ;TermID : B0456A78;C0C16AG0360002WZ;
8;2021-01-18;Uw overschrijving;-1700,07;EUR;18/01/2021;BE44664466446;Party 4;+++020/0132/05910+++ ;C1A18CWFY54917X7;
75;2020-04-06;Opneming Bancontact;-80;EUR;06/04/2020; ;B0456A78        WHEREEVER;20200404 14:59:04 ; Carte/Kaart : 0505050505050 ;TermID : B0456A78;C0D06AG03V0001VY;
"""


@pytest.fixture
def sample():
    return SAMPLE


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
    expected = (
        Transaction(
            date=datetime(year=2021, month=1, day=18),
            source="BE0123456789",
            target="BE11405050461148",
            amount=-70.48,
        ),
        Transaction(
            date=datetime(year=2021, month=1, day=18),
            source="BE0123456789",
            target="BE654987654321",
            amount=-99,
        ),
    )

    assert set(expected) < set(transactions)
