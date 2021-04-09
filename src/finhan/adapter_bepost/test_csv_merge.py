from datetime import datetime
from functools import reduce
from pathlib import Path

import pytest

from .csv_merge import target_files, cooked
from .csv_transactions import from_lines
from ..transaction import Transaction
import pytest

SAMPLES = (
    """Rekeningnummer :;BE0123456789;b.compact rekening
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
""",
    """Rekeningnummer :;BE0123456789;b.compact rekening
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
""",
)


@pytest.fixture
def sample():
    return SAMPLES


ACCOUNT_IDS = ("BE123456789", "BE789456123", "BE321321654654")


def test_files_for_same_account_come_together():
    names = (
        "BE123456789EURdAAAAA.csv",
        "BE123456789EURdBBBBB.csv",
        "BE987654321EURdAAAAA.csv",
        "BE987654321EURdBBBBB.csv",
    )

    mappings = tuple(target_files(map(Path, names)))

    assert set(m.target for m in mappings) == {
        Path("BE123456789.csv"),
        Path("BE987654321.csv"),
    }


def test_duplicates_are_removed(tmpdir):
    sample_paths = tuple(_write_samples("BE123456789EURd", SAMPLES))
    results = tuple(cooked(sample_paths))
    assert len(results) == 1
    assert results[0] == Path("BE123456789.csv")

    result_transactions = set(_read_csv(results[0]))

    sample_transactions = map(_read_csv, sample_paths)
    assert result_transactions == reduce(set.union, sample_transactions, set())


def _read_csv(sample_file):
    with sample_file.open() as f:
        result_transactions, _ = from_lines(f.readlines())
    return result_transactions


def _write_samples(account_id, samples):
    source_files = {
        (Path(f"{account_id}{i}.csv"), sample)
        for i, sample in enumerate(samples)
    }
    for path, sample in source_files:
        with open(path, "w") as f:
            f.write(sample)
        yield path
