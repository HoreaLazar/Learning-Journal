#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
import re
import hashlib
import sqlite3
import logging
import subprocess
import pandas as pd

logging.basicConfig(level=logging.INFO)


# fix column names
def tidy_columns(df, mapping=None):
    df.columns = [x.lower().strip().replace(' ', '_') for x in df.columns]
    if mapping:
        df = df.rename(columns=mapping)
    return df


# fix DOB
def clean_dob(value, lim_year=25):
    if pd.isna(value):
        return None
    else:
        day, month, year = map(int, value.strip().split('/'))
        if year >= lim_year:
            year += 1900
        else:
            year += 2000
        return datetime(year, month, day)


def infer_dob(date, age):
    formats = ["%d/%m/%y", "%y-%m-%d"]
    for fmt in formats:
        try:
            dob = datetime.strptime(date.strip(), fmt)
            dob = dob.replace(year=datetime.now().year - int(age))
            return dob.date()
        except:
            continue
    return None


def load_user_data(filepath, encoding='utf-8'):
    logging.info(f"Loading data from {filepath}")
    df = pd.read_csv(filepath, encoding=encoding)
    return df


def hash_password(pw, encoding='utf-8'):
    if pd.isna(pw):
        return None
    else:
        return hashlib.sha256(pw.encode(encoding)).hexdigest()


def clean_gender(value, mapping=None):
    if pd.isna(value):
        return None
    elif mapping is None:
        return value
    else:
        try:
            new_value = mapping[value]
            return new_value
        except KeyError as e:
            logging.warning(f"Unknown gender value: {value}")
            return None
        except Exception as e:
            logging.error(f"Error cleaning gender value: {value}, {e}")
        return None


def add_education_column(df, mapping):
    if mapping is None:
        logging.warning("No mapping provided for education column.")
    elif 'education' in df.columns:
        logging.info(f"Add RFQ column")
        df['rqf'] = df['education'].apply(lambda x: mapping.get(str(x), None))
    elif 'rqf' in df.columns:
        df['education'] = df['rqf'].apply(lambda x: mapping.get(str(x), None))
    else:
        logging.warning("No education or RFQ column found in the DataFrame.")
    return df


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
    else:
        salary = round(int(re.sub(r"[^\d]", '', value))/100, 2)* period
        if salary < 0:
            logging.warning(f"Negative salary found: {value}")
        return salary


def clean_column(value):
    exclusions = ['BLANK', 'NA', 'NONE', '-', '{NULL}', 'VIDE', '']
    if isinstance(value, str) and value.strip().upper() in exclusions:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    else:
        return value


def transform_users(df, country_code,
                    column_mapping=None,
                    gender_mapping=None,
                    education_mapping=None,
                    payment_period=1,
                    int_dial_code='44',
                    currency='GBP'):
    logging.info("Transforming user data...")
    logging.info(f"Tidying columns")
    df = tidy_columns(df, column_mapping)
    logging.info(f"Cleaning DOB column")
    df['dob'] = df.apply(lambda row: infer_dob(row['dob'], row['age_last_birthday']), axis=1)
    logging.info(f"Hashing password")
    df['password'] = df['password'].apply(hash_password)
    logging.info(f"Cleaning string columns")
    for col in df.columns:
        if col not in ['password', 'dob']:
            df[col] = df[col].apply(clean_column)
    logging.info("Cleaning gender column")
    df['gender'] = df['gender'].apply(lambda row: clean_gender(row, gender_mapping))
    logging.info("Cleaning number columns")
    for col in ['phone', 'mobile']:
        df[col] = df[col].apply(clean_number)
    logging.info(f"Checking education column")
    df = add_education_column(df, education_mapping)
    logging.info("Cleaning salary column")
    df['salary'] = df['salary'].apply(lambda x: clean_salary(x, payment_period))
    logging.info("Setting International Dialing Code")
    df['dial_code'] = int_dial_code
    logging.info("Setting currency")
    df['currency'] = currency
    logging.info("Adding country code")
    df['country_code'] = country_code
    return df


def load_login_data(filepath, timezone):
    logging.info(f"Loading login data from {filepath}")
    df = pd.read_csv(filepath)
    df.columns = ['login_id', 'username', 'login_timestamp']
    logging.info(f"Tidying columns")
    tidy_columns(df)
    df.drop(columns=['login_id'], inplace=True)
    # convert timestamp to datetime
    df['login_timestamp'] = pd.to_datetime(df['login_timestamp'], unit='s', utc=False)
    df['login_timestamp'] = df['login_timestamp'].dt.tz_localize(timezone).dt.tz_convert('UTC')
    return df


def validate_user_visits(users_df:pd.DataFrame,
                         logins_df:pd.DataFrame) -> None:
    """
    Validate that the number of visits in the last 30 days matches the login count
    """
    # get number of logins per user
    login_count = logins_df\
            .groupby('username')\
            .count()\
            .reset_index()\
            .rename(columns={'username':'email',
                             'login_timestamp':'login_count'})
    # merge with users
    users_login_count = users_df.merge(login_count, on='email', how='left').fillna({'login_count': 0})
    # get total cound and count of matches
    total_n = len(users_login_count)
    count_match = (users_login_count['website_visits_last_30_days'] == users_login_count['login_count']).sum()
    if total_n == count_match:
        logging.info("All visits match login count")
    elif count_match == 0:
        logging.error("No visits match login count")
    else:
        logging.warning(f"{round(100*total_n/count_match):0.2f}% match of visits to login count")
    return


uk_education_mapping = {
    '1': 'Vocational Qualification Level 1',
    '2': 'Vocational Qualification Level 2',
    '3': 'A Level',
    '4': 'Higher National Certificate',
    '5': 'Higher National Diploma',
    '6': 'Bachelor’s Degree',
    '7': 'Master’s Degree',
    '8': 'Doctorate Degree'
}


users_uk = load_user_data('data/UK User Data.csv',
                          encoding='latin1')
users_uk = transform_users(users_uk, 'UK', education_mapping=uk_education_mapping, currency='GBP')
logins_uk = load_login_data('data/UK-User-LoginTS.csv', 'Europe/London')
validate_user_visits(users_uk, logins_uk)

french_to_english_columns = {
    'prénom': 'first_name',
    'nom_de_famille': 'surname',
    'ddn': 'dob',
    'âge_dernier_anniversaire': 'age_last_birthday',
    'couleur_préférée': 'favourite_colour',
    'animal_préféré': 'favourite_animal',
    'plat_préféré': 'favourite_food',
    'genre': 'gender',
    'mot_de_passe': 'password',
    'ville': 'city',
    'département': 'county',
    'code_postal': 'postcode',
    'adresse_électronique': 'email',
    'téléphone': 'phone',
    'portable': 'mobile',
    'bac+': 'education',
    'salaire': 'salary',
    'visites_du_site_web_au_cours_des_30_derniers_jours': 'website_visits_last_30_days'
}


french_to_uk_gender = {
    'M': 'Male',
    'F': 'Female',
    'NB': 'Non-Binary'
}


french_to_uk_education = {
    'Collège': '1',
    'Lycée': '2',
    'Baccalauréat': '3',
    'CFA': '5',
    'Licentiate': '6',
    'Master': '7',
    'Doctorat': '8'
}


users_fr = load_user_data('data/FR User Data.csv')
users_fr = transform_users(users_fr, country_code='FR',
                           column_mapping=french_to_english_columns,
                           gender_mapping=french_to_uk_gender,
                           education_mapping=french_to_uk_education,
                           payment_period=12,
                           currency='EUR',
                           int_dial_code='+33')
logins_fr = load_login_data('data/FR-User-LoginTS.csv', 'Europe/Paris')
validate_user_visits(users_fr, logins_fr)

usa_to_uk_columns = {
    'last_name': 'surname',
    'favorite_color': 'favourite_colour',
    'favorite_animal': 'favourite_animal',
    'favorite_food': 'favourite_food',
    'town/city': 'city',
    'state': 'county',
    'state_code': 'county_code',
    'zip_code': 'postcode',
    'landline': 'phone',
    'cell_phone': 'mobile',
}


usa_to_uk_gender = {
    1: 'Male',
    0: 'Female'
}


usa_to_uk_education = {
    'High School Diploma': '3',
    'Associate Degree': '4',
    'Foundation Degree': '5',
    'Bachelor Degree': '6',
    'Master’s': '7',
    'Doctorate': '8'
}


users_usa = load_user_data('data/USA User Data.csv')
users_usa = transform_users(users_usa, 'USA',
                            column_mapping=usa_to_uk_columns,
                            gender_mapping=usa_to_uk_gender,
                            education_mapping=usa_to_uk_education,
                            currency='USD',
                            int_dial_code='+1')
logins_usa = load_login_data('data/USA-User-LoginTS.csv', 'US/Eastern')
validate_user_visits(users_usa, logins_usa)

subprocess.run("sqlite3 customers.db < create_database.sql", shell=True, check=True)

conn = sqlite3.connect("customers.db")

def update_users_table(users_df, conn):
    try:
        new_count = users_df.to_sql('users', conn, if_exists='append', index=False)
        logging.info(f"Inserted {new_count} new records into users table")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        conn.rollback()
    finally:
        conn.commit()
    return


update_users_table(users_uk, conn)
update_users_table(users_fr, conn)
update_users_table(users_usa, conn)


def update_login_table(logins_df, conn):
    try:
        sql_str = """
        SELECT DISTINCT
        user_id, email
        FROM users
        order by user_id
        """
        key_lkp = pd.read_sql(sql_str, conn)
        logins_df_lkp = logins_df.merge(key_lkp, left_on='username', right_on='email', how='inner')
        logins_df_lkp = logins_df_lkp[['user_id', 'login_timestamp']]
        new_count = logins_df_lkp.to_sql('logins', conn, if_exists='append', index=False)
        logging.info(f"Inserted {new_count} new records into logins table")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        conn.rollback()
    finally:
        conn.commit()
    return


update_login_table(logins_uk, conn)
update_login_table(logins_fr, conn)
update_login_table(logins_usa, conn)


conn.close()
