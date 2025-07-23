"""SQLite database logic for inserting users and logins."""
import logging
import pandas as pd
import sqlite3

logger = logging.getLogger(__name__)


def update_users_table(users_df: pd.DataFrame, conn: sqlite3.Connection):
    try:
        new_count = users_df.to_sql('users', conn, if_exists='append', index=False)
        logger.info("Inserted %d new records into users table", new_count)
    except Exception as e:
        logger.error("Unexpected error inserting users: %s", e)
        conn.rollback()
    finally:
        conn.commit()


def update_login_table(logins_df: pd.DataFrame, conn: sqlite3.Connection):
    try:
        sql_str = """
        SELECT DISTINCT
        user_id, email
        FROM users
        ORDER BY user_id
        """
        key_lkp = pd.read_sql(sql_str, conn)
        logins_df_lkp = logins_df.merge(key_lkp, left_on='username', right_on='email', how='inner')
        logins_df_lkp = logins_df_lkp[['user_id', 'login_timestamp']]
        new_count = logins_df_lkp.to_sql('logins', conn, if_exists='append', index=False)
        logger.info("Inserted %d new records into logins table", new_count)
    except Exception as e:
        logger.error("Unexpected error inserting logins: %s", e)
        conn.rollback()
    finally:
        conn.commit()