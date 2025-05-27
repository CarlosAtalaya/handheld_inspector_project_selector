'''
This module generates filenames in a defined format.
It serves as a support module for io/localoutput.
'''
import re

# IO
CT_LOCAL_OUTPUT_FILE_NAME_BASE = 'img'
CT_LOCAL_OUTPUT_FILE_NAME_EXTENSION = '.png'


def generate_defect_name(raw_defect_type, separator='-'):
    '''
    Builds defect name based on raw selected defect type-.
    Args:
    - raw_defect_type (str): raw selected defect type.
    Returns:
    - clean_defect_type (str): clean defect type.
    '''
    words = re.findall(r'[A-Za-z]+', raw_defect_type)
    return separator.join(words)


def generate_image_file_name(timestamp, defect_type):
    '''
    Generates an image file name based on current timestamp
    and defect type.
    Args:
    - timestamp (str): current image's timestamp.
    - defect_type (str): clean defect name.
    Returns:
    - file_name (str): filename for the image to be saved.
    '''
    file_name = (
        f'{CT_LOCAL_OUTPUT_FILE_NAME_BASE}'
        f'_{defect_type}'
        f'_{timestamp}'
        f'{CT_LOCAL_OUTPUT_FILE_NAME_EXTENSION}'
    )
    return file_name
