# Data-Project

A small end-to-end UK public legal data pipeline and explorer built as a starter project.

This repository demonstrates:
- ingesting legal data from a public source or a local sample dataset
- normalizing and storing it in SQLite
- querying and filtering the records in a simple Streamlit interface

## Project goals
- Build a working mini data pipeline around UK legal/public data
- Parse metadata such as case name, neutral citation, judge, court, and date
- Provide a lightweight search/filter UI

## Project structure

```text
Data-Project/
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   └── raw_cases.json
├── database/
│   └── schema.sql
├── scripts/
│   ├── ingest.py
│   ├── transform.py
│   └── load.py
└── web/
    └── app.py
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/ingest.py
python scripts/load.py
streamlit run web/app.py
```

## What the app does

- downloads court case data (or falls back to sample legal records if the public API is unavailable)
- stores the transformed case metadata in a local SQLite database
- lets the user filter by judge, court, and keyword

## Example filters
- judge: "Mellor"
- court: "High Court"
- keyword: "employment"

## Notes

This is a starter implementation designed to be extended. You can replace the sample data source with the National Archives Find Case Law API or Companies House API and expand the schema as needed.
