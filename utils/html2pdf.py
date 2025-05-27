'''
    html2pdf.py module

    Write pdf from html file.

    NOTE: chrome REQUIRED. The html report should be in 'jec25/UI/reports/'
    path to ensure all modules, images and styles are imported correctly.
'''
import subprocess


def html2pdf(htmlpath, pdfpath):
    '''
    Generate pdf from HTML file.
    Args:
    - htmlpath, pdfpath (str)
    '''

    command = [
        'google-chrome',
        '--headless',
        '--disable-gpu',
        f'--print-to-pdf={pdfpath}.pdf',
        '--no-margins',
        htmlpath
    ]

    try:
        subprocess.run(command, check=True)
    except Exception as e:
        print(f'Chrome Subprocess error: {e}')
