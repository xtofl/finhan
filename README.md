# finhan

[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=xtofl_finhan&metric=code_smells)](https://sonarcloud.io/dashboard?id=xtofl_finhan)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=xtofl_finhan&metric=coverage)](https://sonarcloud.io/dashboard?id=xtofl_finhan)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=xtofl_finhan&metric=security_rating)](https://sonarcloud.io/dashboard?id=xtofl_finhan)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=xtofl_finhan&metric=alert_status)](https://sonarcloud.io/dashboard?id=xtofl_finhan)

View the balance of some of your accounts over time.

![demo-data](tests_e2e/demo-data/grand-total.png)

## Installing

For now, clone this repo, run `poetry build` in it, and install the .whl file
from the `dist/` folder: `pip3 install dist/*.whl`.

## Usage

The main script is `finhan-view`.

### Bpost

1. make a directory to store your data in.  I call it '.private-bank-data'.
  Work from within that folder.
2. download the so-called 'csv-files' from your bepost account
3. move the files into the data folder:
  `mv ~/Downloads/BE*.csv .private-bank-data/`
4. create a file `balance.yaml` containing the current balance of your accounts.
    ```
    schema: "v1"
    last updated: 2021-04-05
    accounts:
            - id: BE123456789
              balance: 1157.82
            - id: BE987654321
              balance: 1782.03
    ```
   Also create a file to override the account names extracted from the data
    files.  This file has following format:
   ```
   schema: "v1"
   accounts:
   - id: BE55299487620844
     name: Onvoorziene
   - id: BE98299998030093
     name: Rekening Verzekering
   ```
   A skeleton for this file can be generated with the `finhan-bepost-names
    *.csv` script.
4. play:
   1. `finhan-view --format=bepost *.csv`
   2. `finhan-bepost-table --account BE123456789 *.csv`
   3. 'Good' shells will show the possible finhan commands when typing `finhan-`
      and pressing TAB TAB.

## Contributing

* Do install git pre-commit hooks, so your commits get automatically
  checked for simple style errors.
