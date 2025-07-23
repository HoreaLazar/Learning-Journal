"""main.py
This script orchestrates the data pipeline for user and login data across multiple countries.
It loads configurations, processes data, validates it, and inserts it into a SQLite database.
"""
import sqlite3
import subprocess
from tests import validation
from pipeline.transform import transform_users
from pipeline.database import update_users_table, update_login_table
from pipeline.config_loader import load_json_config
from pipeline.load_data import load_user_data, load_login_data

def process_country(config):
    """Process user and login data for a specific country based on the provided configuration."""
    users = load_user_data(config.get('user_path'), encoding=config.get('encoding', 'utf-8'))
    logins = load_login_data(config.get('login_path'), config.get('timezone'))

    users = transform_users(users,
                            country_code=config.get('label'),
                            column_mapping=config.get('column_mapping'),
                            gender_mapping=config.get('gender_mapping'),
                            education_mapping=config.get('education_mapping'),
                            payment_period=config.get('payment_period', 1),
                            int_dial_code=config.get('int_dial_code', '44'),
                            currency=config.get('currency', 'GBP'))

    validation.validate_user_visits(users, logins)
    validation.check_duplicates(users,
                                subset=['email'],
                                label=f"{config.get('label')} users")
    validation.validate_email_uniqueness(users,
                                         label=f"{config.get('label')} users")
    validation.check_required_columns(logins,
                                      ['username', 'login_timestamp'],
                                      label=f"{config.get('label')} logins")

    return users, logins

def insert_all_to_db(conn, user_sets, login_sets):
    """Insert all user and login data into the database."""
    for df in user_sets:
        update_users_table(df, conn)
    for df in login_sets:
        update_login_table(df, conn)


def run_pipeline():
    """Run the entire data processing pipeline."""
    uk_config = load_json_config('mappings_uk.json')
    fr_config = load_json_config('mappings_fr.json')
    usa_config = load_json_config('mappings_usa.json')

    users_uk, logins_uk = process_country(uk_config)

    users_fr, logins_fr = process_country(fr_config)

    users_usa, logins_usa = process_country(usa_config)

    subprocess.run("sqlite3 customers.db < sql/create_database.sql", shell=True, check=True)
    conn = sqlite3.connect("customers.db")

    insert_all_to_db(conn,
                     user_sets=[users_uk, users_fr, users_usa],
                     login_sets=[logins_uk, logins_fr, logins_usa])

    conn.close()

if __name__ == "__main__":
    run_pipeline()
