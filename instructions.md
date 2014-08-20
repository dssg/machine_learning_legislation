This document outlines steps to follow to recreate building our earmark
classifier.

### Python Dependencies ###
- psycopg2
  - **Note:** In order to install psycopg2 with pip, you will also need to
    install the system packages libpq-dev and python-dev.
- beautifulsoup4
- numpy
- scipy
- mysql-connector-python
- requests
- nltk
- nose
- pandas

### Getting Data ###

Our data source includes plain text formats for congressional bills and
congressional reports.

#### Congressional Bills ####

Bills can be downloaded from [GovTrack.us](https://www.govtrack.us/). Text
versions of bills can be downloaded via `rsync` using directions at [this
location](https://www.govtrack.us/developers/data).

#### Congressional Reports ####

Congressional reports can be downloaded using the script found at
`src/python/bill_fetcher/congress_report_downloader.py`

#### OMB Earmark Data ####

The Office of Management and Budget collected data on earmarks for the years
2005, 2008, 2009, and 2010. We use this data to create positive examples for our
earmark classifier. CSV versions of this data can be downloaded at [the OMB
website](http://earmarks.omb.gov/earmarks-public/).

### Importing the Data ###

To create the databases, run the SQL script located at
`conf/create_db_tables.sql`.

#### Bills ####

To import bill data to the database, use the script
`src/python/data_importer/import_bills_to_db` passing it the `bills` argument
and the path to the bills.

Example: `python import_bills_to_db.py --bills --path
/mnt/data/sunlight/bills/110/bills/`

#### Reports ####

To import report data to the database, use the script
`src/python/data_importer/import_bills_to_db` passing it the `reports` argument
and the path to the reports.

Example: `python import_bills_to_db.py --reports --path
/mnt/data/sunlight/congress_reports/111/`

#### OMB Data ####

To import OMB data to the database, use the script
`src/python/data_import/import_omb_csv.py` passing it the path to the OMB csv
file and the year of the file.

Example: `python import_omb_csv.py --path
./2010-appropriations-earmark-extract.csv --year 2010`

#### Linking Reports and Bills ####

**TODO: This process could probably be cleaned up, and at the very least the
scripts should be cleaned up to accept parameters instead of hard coded
values.**

To link reports and bills:

1. Run the script `src/python/bill_fetcher/associate_reports_bills.py`. This
will generate a csv file linkins bill paths and report paths.
2. The script `src/python/data_importer/populate_bills_reports.py` uses the
above csv as an input and outputs another csv with linked report and bill id's.
3. This csv can be dumped into the `bill_reports` table.

### Classification ###

#### OMB Matching ####

Our goal is to create a classifier that classifies entities in tables as
earmarks or not. In order to create positive examples, we link entries from the
OMB database to table rows in documents. We also treat this as a classification
problem, first hand labeling several matches and using features of these matches
to identify the rest.

The script `src/python/matching/label_matches.py` can be used for hand labeling
examples.

For use in our classification pipeline, the labeled instances must be
serialized. Use the script `src/python/matching/prepare_matching_data` with the
serialize flag to create Python pickles.

The `src/python/matching/classifier.py` script can be used with the `build` flag
to create a serialized model of the matching classifier.

Finally, the `src/python/matching/ml_matching.py` script can be passed this
pickled classifier in order to match the rest of the rows.

#### Earmark Classification ####


