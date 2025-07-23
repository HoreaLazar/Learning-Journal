# L5-DE-Data-Pipelines-T4

This project develops and expands a user data pipeline for a growing international application. It integrates user metadata and login records from the UK, France, the US, and now Scotland! The pipeline is designed to standardise diverse data formats, enforce validation rules, and support scalable ingestion into a unified SQLite database. It also now modularises the code, and adds elements of testing.

## 🚀 Project Overview

Your objectives now are listed below:
   - Update and expand the database schema to support multi-country user data.
   - Clean, validate, and integrate data from UK, French, US, and SC sources.
   - Handle local formatting differences (e.g. salary, date, gender, encoding).
   - Maintain a shared schema with country-specific data pipelines.
   - Prepare for future global integrations with additional countries.


**Note: Collaborate with Your Instructor**  
 Your instructor will act as the stakeholder and Subject Matter Expert (SME). They will provide clarification on:
   - Schema requirements
   - Business rules for validation
   - Future data sources

---

## 🔄 Data Pipeline Enhancements
The pipeline should been updated to process UK, FR, US, and SC datasets:
- Config files allow defining of parameters spcific to each file type.
- Clean and normalise data fields (e.g., DoB formats, salary parsing, gender codes).
- Add the appropriate 'country_code' (e.g., 'UK', 'FR') for each user entry.
- Merge data into a shared 'users' and 'logins' table with consistent structure.

---

## 📦 Repository Structure

```plaintext
├── config/                         # JSON configs for mappings and exclusions
│   ├── exclusions.json
│   ├── mappings_uk.json
│   ├── mappings_fr.json
│   ├── mappings_usa.json
|   └── mappings_sc.json
│
├── data/                           # Raw CSV data files
│   ├── FR User Data.csv
│   ├── FR-User-LoginTS.csv
│   ├── SC User Data.csv
│   ├── SC-User-LoginTS.csv
│   ├── UK User Data.csv
│   ├── UK-User-LoginTS.csv
│   ├── USA User Data.csv
│   └── USA-User-LoginTS.csv
│
├── pipeline/                       # Python package for reusable pipeline code
│   ├── __init__.py                 # Empty file to make this a package
│   ├── config_loader.py
│   ├── data_utils.py               # utility functions (mostly for transforming data)
│   ├── database.py                 # Python code related to database management
│   └── transform.py                # workhorse of transformations
│
├── sql/                            # SQL schema script
│   └── create_database.sql
│
├── tests/                          # Test coverage
│   ├── test_pipeline.py            # testing for issues with code
│   └── validation.py               # validating data
│
├── data_pipeline.py                # Starting point for your script
├── main.py                         # Main orchestration script
├── requirements.txt                # Optional dependency list
├── README.md                       # Project documentation
```

You will work from `data_pipeline.py`, and create the modularised content in `config`, `data`, `pipeline`, `sql`, `tests` and `main.py`.

---

## 🧠 Remember

This setup uses **SQLite** for simplicity and local prototyping, but the same schema and logic should be portable to PostgreSQL or another RDBMS in a production environment. Keep modularity and maintainability in mind.

Happy coding!