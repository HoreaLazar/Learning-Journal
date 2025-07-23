"""Data cleaning utilities."""
import re
import hashlib
import logging
import pandas as pd
from datetime import datetime
from pipeline.config_loader import load_json_config

logger = logging.getLogger(__name__)


EXCLUSIONS = set(load_json_config('exclusions.json'))

def tidy_columns(df, mapping=None):
    df.columns = [x.lower().strip().replace(' ', '_') for x in df.columns]
    if mapping:
        df = df.rename(columns=mapping)
    return df

def clean_column(value):
    if isinstance(value, str) and value.strip().upper() in EXCLUSIONS:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    return value

def clean_gender(value, mapping=None):
    if pd.isna(value):
        return None
    if mapping is None:
        return value
    try:
        return mapping[value]
    except KeyError:
        logger.warning("Unknown gender value: %s", value)
        return None
    except Exception as e:
        logger.error("Error cleaning gender value: %s, %s", value, e)
        return None

def clean_number(value):
    if pd.isna(value):
        return None
    else:
        number = re.sub(r"[^\d]", '', value)
        if number.startswith('0'):
            number = number[1:]
        return number

def clean_salary(value, period=1):
    if pd.isna(value):
        return None
    try:
        salary = round(int(re.sub(r"[^\d]", '', str(value))) / 100, 2) * period
        if salary < 0:
            logger.warning("Negative salary found: %s", value)
        return salary
    except Exception as e:
        logger.error("Failed to clean salary: %s", e)
        return None

def hash_password(pw, encoding='utf-8'):
    if pd.isna(pw):
        return None
    return hashlib.sha256(pw.encode(encoding)).hexdigest()

def clean_dob(value, lim_year=25):
    if pd.isna(value):
        return None
    try:
        day, month, year = map(int, value.strip().split('/'))
        year += 1900 if year >= lim_year else 2000
        return datetime(year, month, day)
    except Exception as e:
        logger.error("Failed to clean DOB: %s", e)
        return None

def infer_dob(date, age):
    formats = ["%d/%m/%y", "%y-%m-%d", "%m/%d/%y"]
    for fmt in formats:
        try:
            dob = datetime.strptime(date.strip(), fmt)
            dob = dob.replace(year=datetime.now().year - int(age))
            return dob.date()
        except Exception:
            continue
    return None