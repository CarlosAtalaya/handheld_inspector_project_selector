'''
Module to handle timestamp operations.
'''
import time

from handheld.constants import CT_TIMESTAMP_FORMAT, CT_DATE_FORMAT


def generate_timestamp(raw_timestamp):
    '''
    Converts given raw timestamp to a defined format.

    Args:
        raw_timestamp(str): The image URL containing '?t=<timestamp>'.

    Returns:
        str or None: A formatted timestamp string
        (e.g., '2025-05-13-17-45-20'),
                     or None if the 't' parameter is not found.
    '''
    timestamp = None
    # Seconds from Epoch to gmt
    gmt_time = time.gmtime(raw_timestamp)
    # Convert to defined format
    timestamp = time.strftime(CT_TIMESTAMP_FORMAT, gmt_time)

    return timestamp


def get_current_date():
    '''
    Returns the current date in the defined format.

    Returns:
    - current_date (str): A formatted date string
      (e.g., '2025-05-19').
    '''
    # Get current time in local timezone
    current_time = time.localtime()
    # Format according to date format
    current_date = time.strftime(CT_DATE_FORMAT, current_time)
    return current_date
