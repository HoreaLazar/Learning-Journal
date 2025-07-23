"""Main pipeline execution script."""
import logging
import pandas as pd
from pipeline.data_utils import tidy_columns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_user_data(filepath, encoding='utf-8'):
    logger.info("Loading user data from %s", filepath)
    df = pd.read_csv(filepath, encoding=encoding)
    return df

def load_login_data(filepath, timezone):
    logger.info("Loading login data from %s", filepath)
    df = pd.read_csv(filepath)
    df.columns = ['login_id', 'username', 'login_timestamp']
    tidy_columns(df)
    df.drop(columns=['login_id'], inplace=True)
    df['login_timestamp'] = pd.to_datetime(df['login_timestamp'], unit='s', utc=False)
    df['login_timestamp'] = df['login_timestamp'].dt.tz_localize(timezone).dt.tz_convert('UTC')
    return df
