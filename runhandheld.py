'''
FlaskAppWrapper module
Wrapper for running a Flask application with a camera integration.
'''
from handheld.webbackend.flask_app import FlaskAppWrapper

if __name__ == '__main__':
    '''
    Creates an instance of FlaskAppWrapper and runs the app.
    This script serves as the starting point for launching the application
    that handles the integration of the camera with Flask.

    # Usage:
    pipenv run python -m handheld.runhandheld
    '''

    CT_CONFIG_FILE = 'handheld/config/config.yaml'

    # Create and run Flask Camera application
    app = FlaskAppWrapper('FlaskCameraApp', CT_CONFIG_FILE)
    app.run()
