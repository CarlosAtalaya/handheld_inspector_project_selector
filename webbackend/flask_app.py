import time
from flask import Flask, render_template, Response, jsonify, request

from ais.infrastructure.readconfig import read_yaml_file
from handheld.automation.handheldopsman import HandheldOpsManager

CT_STREAMER_MIMETYPE = 'multipart/x-mixed-replace; boundary=frame'
CT_CAPTURE_MIMETYPE = 'image/jpeg'

image_cache = {}


class FlaskAppWrapper:
    '''
    Flask app that serves as the wrapper for the inspection system.
    This app manages the HTTP server and handles requests to interact
    with the Handheld operations manager, which controls inspection processes.
    '''
    def __init__(self, name, config_file):
        '''
        Initialize the Flask application and the HandheldOpsManager instance.
        Args:
        - name (str): The name of the Flask application.
        Sets up the Flask app with necessary configurations and endpoints.
        '''
        # init
        self._cached_images = {}

        # Load config
        self.config = read_yaml_file(config_file)

        # Get frontend paths
        templates_dir = self.config['frontend']['templates']
        static_dir = self.config['frontend']['static']

        # App instance
        self.app = Flask(
            name,
            template_folder=templates_dir,
            static_folder=static_dir
        )

        # HandheldOpsManager instance
        self.handheld_ops_manager = HandheldOpsManager(self.config)
        self.selected_defect = ''

        # Define endpoints for various states and operations
        self.add_endpoint('/', 'index', self.index)
        self.add_endpoint('/get_image', 'get_image', self.get_image)
        self.add_endpoint('/video_feed', 'video_feed', self.video_feed)
        self.add_endpoint(
            '/states/project_state',
            'project_state',
            self.project_state, methods=['POST']
        )
        self.add_endpoint(
            '/states/standby_state',
            'standby_state',
            self.standby_state, methods=['POST']
        )
        self.add_endpoint(
            '/states/label_state',
            'label_state',
            self.label_state, methods=['POST']
        )
        self.add_endpoint(
            '/states/selection_state',
            'selection_state',
            self.selection_state, methods=['POST']
        )
        self.add_endpoint(
            '/states/criteria_state',
            'criteria_state',
            self.criteria_state, methods=['POST']
        )
        self.add_endpoint(
            '/states/context_state',
            'context_state',
            self.context_state, methods=['POST']
        )
        self.add_endpoint(
            '/states/detail_state',
            'detail_state',
            self.detail_state, methods=['POST']
        )
        self.add_endpoint(
            '/states/confirmation_state',
            'confirmation_state',
            self.confirmation_state, methods=['POST']
        )
        self.add_endpoint(
            '/states/end_state',
            'end_state',
            self.end_state, methods=['POST']
        )
        self.add_endpoint(
            '/get_image_cache/<cache_key>',
            'get_image_cache',
            self.get_image_cache
        )

    def add_endpoint(self, route, endpoint_name, handler, methods=['GET']):
        '''
        Adds a new endpoint to the Flask app.
        Args:
        - route (str): URL route for the endpoint.
        - endpoint_name (str): Name of the endpoint.
        - handler (function): Function to handle requests to the endpoint.
        - methods (list): HTTP methods supported by the endpoint
          (default is ['GET']).
        '''
        self.app.add_url_rule(route, endpoint_name, handler, methods=methods)

    def video_feed(self):
        '''
        Endpoint for video streaming.
        Returns:
        - Response: Video stream in multipart/x-mixed-replace format.
        '''
        streamer = self.handheld_ops_manager.video_encode_stream()
        response = Response(streamer, mimetype=CT_STREAMER_MIMETYPE)
        return response

    def get_image(self):
        '''
        Endpoint to return the latest captured image.
        '''
        image_bytes = self.handheld_ops_manager.video_capture_image()

        response = None
        if image_bytes is None:
            response = jsonify({"error": "No frames captured yet"}), 404
        else:
            response = Response(image_bytes, mimetype=CT_CAPTURE_MIMETYPE)
            response.headers['Cache-Control'] = (
                'no-store, no-cache, must-revalidate, max-age=0'
            )

        return response

    def get_image_cache(self, cache_key):
        '''
        Endpoint to return cached images.
        '''
        image_bytes = self._cached_images.get(cache_key)

        response = None
        if image_bytes is None:
            response = jsonify({"error": "No frames captured yet"}), 404
        else:
            response = Response(image_bytes, mimetype=CT_CAPTURE_MIMETYPE)
            response.headers['Cache-Control'] = (
                'no-store, no-cache, must-revalidate, max-age=0'
            )

        return response

    def _cache_busted_url(self, url):
        '''
        Cache busting. Add timestamp to url to force the browser to load the
        most recent version of the file.
        Args:
        - ulr (str)
        Returns:
        - url + timestamp (str)
        '''
        return f'{url}?t={time.time()}'

    def project_state(self):
        '''
        Handles the "project_state".
        '''
        data = request.get_json().get('data')
        project = data['project']
        inspector = data['inspector']

        next_state, n_inspection = self.handheld_ops_manager.project_state(
            project, inspector
        )

        response = {
            'nextState': next_state,
            'data': {
                'screen': '/video_feed',
                'report': {
                    'text': {
                        'project': project,
                        'inspector': inspector,
                        'page-number': n_inspection
                    }
                },
                'n_inspection': n_inspection
            }
        }
        return jsonify(response)

    def standby_state(self):
        '''
        Endpoint to handle the standby state.
        Processes form data and builds HTTP response.
        Returns:
        - JSON: Response including next state and additional data.
        '''
        data = request.get_json().get('data')

        next_state, n_inspection, current_date = (
            self.handheld_ops_manager.standby_state(
                data['inspected-part'],
                data['serial-number']
            )
        )
        data['date'] = current_date
        data['page-number'] = n_inspection

        response = {
            'nextState': next_state,
            'actions': {
                'report': {
                    'add_page': False,
                    'remove_page': False,
                    'update_page': True,
                    'page_number': n_inspection,
                }
            },
            'data': {
                'screen': '/video_feed',
                'report': {'text': data},
                'n_inspection': n_inspection
            }
        }
        return jsonify(response)

    def label_state(self):
        '''
        Handles the "label" state, where the system waits
        to capture the part's label photo.
        Returns:
        - JSON: Response including next state and additional data.
        '''
        next_state, n_inspection = (
            self.handheld_ops_manager.label_state()
        )

        response = {
            'nextState': next_state,
            'actions': {
                'report': {
                    'add_page': False,
                    'remove_page': False,
                    'update_page': True,
                    'page_number': n_inspection
                }
            },
            'data': {
                'screen': '/video_feed',
                'report': {
                    'images': {
                        'image-partid': self._cache_busted_url('get_image')
                    },
                    'text': {
                        'page-number': n_inspection
                    }
                },
                'n_inspection': n_inspection
            }
        }
        return jsonify(response)

    def selection_state(self):
        '''
        Handles the selection state for defect types.
        Processes user selections and builds HTTP response.
        Returns:
        - JSON: Response including next state and criteria data.
        '''
        data = request.get_json().get('data')
        defect_type = data.get('defect-type')
        surface_quality = data.get('surface-quality')
        finish = data.get('finish')
        defect_name = data.get('defect-name')

        (
            next_state,
            criteria_data,
            n_inspection
        ) = self.handheld_ops_manager.selection_state(
            defect_type,
            surface_quality,
            finish
        )

        report_data = {
            'criteria': criteria_data,
            'defect-name': defect_name,
            'page-number': n_inspection
        }

        response = {
            'nextState': next_state,
            'actions': {
                'report': {
                    'add_page': False,
                    'remove_page': False,
                    'update_page': True,
                    'page_number': n_inspection
                }
            },
            'data': {
                'screen': '/video_feed',
                'report': {'text': report_data},
                'ui-content': {
                    'defect-type': defect_type,
                    'surface-quality': surface_quality,
                    'finish': finish,
                    'criteria': criteria_data
                },
                'n_inspection': n_inspection
            }
        }
        return jsonify(response)

    def criteria_state(self):
        '''
        Handles the criteria state for defect evaluation.
        Processes user selection and builds appropriate HTTP response.
        Returns:
        - JSON: Response including next state and additional data.
        '''
        action = request.get_json().get('action')

        next_state, action, n_inspection = (
            self.handheld_ops_manager.criteria_state(action)
        )

        response = {
            'nextState': next_state,
            'actions': {
                'report': {
                    'add_page': False,
                    'remove_page': False,
                    'update_page': action == 'keep',
                    'page_number': n_inspection
                }
            },
            'data': {
                'screen': '/video_feed',
                'report': {
                    'text': {
                        'page-number': n_inspection
                    }
                },
                'n_inspection': n_inspection
            }
        }
        return jsonify(response)

    def context_state(self):
        '''
        Handles the "context" state, where the system waits
        to capture the context photo.
        Returns:
        - JSON: Response including next state and additional data.
        '''
        next_state, guideline_side, n_inspection = (
            self.handheld_ops_manager.context_state()
        )

        response = {
            'nextState': next_state,
            'actions': {
                'report': {
                    'add_page': False,
                    'remove_page': False,
                    'update_page': True,
                    'page_number': n_inspection
                }
            },
            'data': {
                'screen': '/video_feed',
                'guideline_side': guideline_side,
                'report': {
                    'images': {
                        'image-context': self._cache_busted_url('get_image')
                    },
                    'text': {
                        'page-number': n_inspection
                    }
                },
                'n_inspection': n_inspection
            }
        }
        return jsonify(response)

    def detail_state(self):
        '''
        Handles the "detail" state, where the system waits
        to capture the detail photo.
        Returns:
        - JSON: Response including next state and additional data.
        '''
        next_state, n_inspection = (
            self.handheld_ops_manager.detail_state()
        )

        response = {
            'nextState': next_state,
            'actions': {
                'report': {
                    'add_page': False,
                    'remove_page': False,
                    'update_page': True,
                    'page_number': n_inspection
                }
            },
            'data': {
                'screen': self._cache_busted_url('get_image'),
                'report': {
                    'images': {
                        'image-detail': self._cache_busted_url('get_image')
                    },
                    'text': {
                        'page-number': n_inspection
                    }
                },
                'n_inspection': n_inspection
            }
        }
        return jsonify(response)

    def confirmation_state(self):
        '''
        Handles the "confirmation" state, that is, keep, repeat or drop
        inspection.
        Returns:
        - JSON: Response including next state and additional data.
        '''
        front_action = request.json.get('action')

        next_state, n_inspection, action, cached_data, cached_images = (
            self.handheld_ops_manager.confirmation_state(front_action)
        )

        # Cache captured images for later retrieval via /get_image_cache
        self._cached_images = cached_images

        response = {
            'nextState': next_state,
            'actions': {
                'report': {
                    'add_page': action == 'repeat',
                    'remove_page': action != 'keep',
                    'update_page': action == 'repeat',
                    'page_number': n_inspection
                }
            },
            'data': {
                'screen': '/video_feed',
                'report': {
                    'text': {**cached_data, 'page-number': n_inspection},
                    'images': {k: f'/get_image_cache/{k}' for k in cached_images}  # noqa
                },
                'n_inspection': n_inspection
            }
        }

        return jsonify(response)

    def end_state(self):
        '''
        Handles end state of the inspection workflow.
        ...
        Returns:
        - JSON: Response including next state and appropriate data.
        '''
        front_action = request.json.get('action')
        raw_defect_type = request.get_json().get('selectedDefect')

        # Call the handheld_ops_manager to process the action
        (
            next_state,
            n_inspection,
            action,
            cached_data,
            cached_images
        ) = self.handheld_ops_manager.end_state(front_action, raw_defect_type)

        self._cached_images = cached_images

        # Build the response based on the state machine's output
        response = {
            'nextState': next_state,
            'actions': {
                'report': {
                    'add_page': action in ['more', 'new'],
                    'remove_page': False,
                    'update_page': action == 'more',
                    'page_number': n_inspection
                }
            },
            'data': {
                'screen': '/video_feed',
                'report': {
                    'text': {**cached_data, 'page-number': n_inspection},
                    'images': {k: f'/get_image_cache/{k}' for k in cached_images}  # noqa
                },
                'n_inspection': n_inspection,
            }
        }

        return jsonify(response)

    def index(self):
        '''
        Renders the main page (index.html).
        Returns:
        - Rendered template: Renders the 'index.html' template.
        '''
        return render_template(
            'index.html',
            defects=self.handheld_ops_manager.qc.get_defects(),
            quality=self.handheld_ops_manager.qc.get_quality(),
            finish=self.handheld_ops_manager.qc.get_finish()
        )

    def run(self):
        '''
        Starts the Flask server on host '0.0.0.0' and port 5001.
        The app runs in threaded mode to handle multiple requests
        simultaneously.
        '''
        self.app.run(
            host=self.config['flask']['host'],
            port=self.config['flask']['port'],
            threaded=self.config['flask']['threaded'],
            debug=self.config['flask']['debug']
        )
