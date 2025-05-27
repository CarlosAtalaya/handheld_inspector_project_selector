import cv2
import time

from handheld.camera.camera import VideoCam
from handheld.automation.qualitycriteria import QualityCriteria
from handheld.automation.guidelines import GuidelineSelector
from handheld.io.localoutput import LocalOutput
from handheld.utils.timestamp import generate_timestamp, get_current_date
from handheld.utils.filenamebuilder import (
    generate_defect_name,
    generate_image_file_name
)


class HandheldOpsManager:
    '''
    Operations manager for Handheld inspection system.
    Handles the workflow for scanning QR codes,
    capturing context and detailed photos,
    detecting defects, and generating reports.
    '''
    def __init__(self, config):
        '''
        Initializes the HandheldOpsManager instance.
        '''
        self.config = config
        self._vc = VideoCam(config)
        self.qc = QualityCriteria(config)
        self.gs = GuidelineSelector()
        self.lo = LocalOutput(config)
        self.last_frame = None
        self.current_defect_data = {
            'defect_type': '',
            'surface_quality': '',
            'finish': '',
            'criteria': ''
        }
        self.n_inspection = 1
        self.current_date = ''

        self._available_projects = self.qc.discover_available_projects()

        self._cached_data = {}
        self._cached_images = {}

    def get_available_projects(self):
        '''
        Returns the list of available projects.
        Returns:
        - list: Available project names
        '''
        return self._available_projects

    def project_state(self, project, inspector):
        '''
        Process project and inspector data before starting inspection.
        Args:
        - project (str): Project name
        - inspector (str): Inspector name
        Returns:
        - next_state (str): Next state to transition to.
        - n_inspection (int): Current inspection number.
        '''
        next_state = 'standby_state'

        # Set the project in QualityCriteria to load corresponding CSV
        self.qc.set_project(project)

        # Reset inspection data for new project
        self.n_inspection = 1

        # Store project and inspector data
        self._cached_data['project'] = project.upper()
        self._cached_data['technician'] = inspector

        return next_state, self.n_inspection

    def standby_state(self, part_number, serial_number):
        '''
        Process part data before starting inspection.
        Args:
        ...
        ...
        Returns:
        - next_state (str): Next state to transition to.
        - self.n_inspection (int): Current inspection number.
        - current_date (str): A formatted date string
          (e.g., '2025-05-19').
        '''
        next_state = 'label_state'

        self.current_date = get_current_date()

        # Store invariant data to inspection
        self._cached_data['date'] = self.current_date
        self._cached_data['inspected-part'] = part_number
        self._cached_data['serial-number'] = serial_number

        return next_state, self.n_inspection, self.current_date

    def label_state(self):
        '''
        Handle part's label photo capture process.
        Returns:
        - next_state (str): Next state to transition to.
        - self.n_inspection (int): Current inspection number.
        '''
        next_state = 'selection_state'

        # Store invariant images to inspection
        self._cached_images['image-partid'] = self.video_capture_image()

        return next_state, self.n_inspection

    def selection_state(
            self,
            defect_type,
            surface_quality,
            finish
    ):
        '''
        Process defect selection criteria.
        Updates current defect data on each new selection.
        Args:
        - defect_type (str): User's selected defect type.
        - surface_quality (str): User's selected surface quality.
        - finish (str): User's selected finish.
        Returns:
        - next_state (str): Next state to transition to.
        - criteria_data (dict): Criteria data for the selected parameters.
        - self.n_inspection (int): Current inspection number.
        '''
        next_state = 'criteria_state'
        self.current_defect_data['defect_type'] = defect_type
        self.current_defect_data['surface_quality'] = surface_quality
        self.current_defect_data['finish'] = finish
        self.current_defect_data['criteria'] = self.qc.get_criteria(
            self.current_defect_data['defect_type'],
            self.current_defect_data['surface_quality'],
            self.current_defect_data['finish']
        )
        return (
            next_state,
            self.current_defect_data['criteria'],
            self.n_inspection
        )

    def criteria_state(self, front_action):
        '''
        Process criteria evaluation for the selected defect.
        Args:
        - defect_type (str): The selected defect type.
        - front_action (str): User's action.
            - 'yes': feature complies with defect criteria.
            - 'no': feature does not complie with defect criteria.
        Returns:
        - next_state (str): Next state to transition to.
        - action (str): 'keep' or 'repeat'
        - guideline_side (str): Guideline side to be displayed.
        - self.n_inspection (int): Current inspection number.
        '''
        next_state = 'context_state'
        action = 'keep'

        if front_action == 'no':
            next_state = 'selection_state'
            action = 'repeat'

        return next_state, action, self.n_inspection

    def context_state(self):
        '''
        Handle context photo capture process.
        Process guideline side to be shown at detail state.
        Returns:
        - next_state (str): next_state.
        - self.n_inspection (int): Current inspection number.
        - guideline_side (str): chosen guideline side.
        '''
        next_state = 'detail_state'
        # Calculate guideline side to be displayed according
        # to selected defect_type
        guideline_side = self.gs.choose_guideline_side(
            self.current_defect_data['defect_type']
        )

        return next_state, guideline_side, self.n_inspection

    def detail_state(self):
        '''
        Handle detail photo capture process.
        Returns:
        - next_state (str): Next state to transition to.
        - self.n_inspection (int): Current inspection number.
        '''
        next_state = 'confirmation_state'
        return next_state, self.n_inspection

    def confirmation_state(self, front_action):
        '''
        Confirmation state.
        Args:
        - front_action (str):
            - 'keep': keep inspection.
            - 'repeat': repeat inspection, new page with cached data.
            - 'drop': drop inspection, remove last report page.
        Returns:
        - next_state (str): Next state to transition to.
        - action (str): 'keep', 'repeat' or 'drop'.
        - cached_data (dict): invariant data to inspection.
        - cached_images (dict): invariant images to inspection.
        '''
        # Init defaults
        next_state = 'end_state'
        action = 'keep'
        cached_data, cached_images = {}, {}
        n_inspection = self.n_inspection

        if front_action == 'repeat':
            next_state = 'selection_state'
            action = 'repeat'
            cached_data = self._cached_data
            cached_images = self._cached_images

        elif front_action == 'drop':
            action = 'drop'
            self.n_inspection -= 1

        return next_state, n_inspection, action, cached_data, cached_images

    def end_state(self, front_action, raw_defect_type):
        '''
        Process end state logic.
        Args:
        - front_action (str):
            - 'more': start new inspection on the same part and report.
            - 'new-part': start new part (same project).
            - 'new-project': start completely new project.
            - 'print': print current report.
        - raw_defect_type (str): Selected defect type for file naming

        Returns:
        - next_state (str): Next state to transition to.
        - self.n_inspection (int): Current inspection number.
        - action (str): 'new-part', 'new-project', 'more' or 'print'.
        - cached_data (dict): invariant data to inspection.
        - cached_images (dict): invariant images to inspection.
        '''
        # Init defaults
        next_state = 'selection_state'
        action = 'more'
        cached_data, cached_images = {}, {}

        # IO localoutput
        # Generate formatted defect_type
        image_defect_type = generate_defect_name(raw_defect_type)
        # Get formatted ts
        timestamp = generate_timestamp(time.time())
        # Generate file name
        image_file_name = generate_image_file_name(
            timestamp,
            image_defect_type
        )
        # Generate local path
        image_local_path = self.lo.generate_local_path(image_file_name)
        # Save image
        self.lo.imwrite(self.last_frame, image_local_path)

        if front_action == 'more':
            # More inspections on same part
            cached_data = self._cached_data
            cached_images = self._cached_images
            self.n_inspection += 1

        elif front_action == 'print':
            next_state = 'end_state'
            action = 'print'

        elif front_action == 'new-part':
            # New part, same project - keep project and inspector data
            next_state = 'standby_state'
            action = 'new-part'
            self.n_inspection = 1

        elif front_action == 'new-project':
            # Completely new project - clear everything
            next_state = 'project_state'
            action = 'new-project'
            self.n_inspection = 1
            # Clear all cached data for new project
            self._cached_data = {}
            self._cached_images = {}

        return (
            next_state,
            self.n_inspection,
            action,
            cached_data,
            cached_images
        )

    def video_capture_image(self):
        '''
        Captures a frame through the VideoCam module and encodes
        the image to JPEG.
        Returns:
        - data (bytes): if not None, encoded frame.
        '''
        self.last_frame = self._vc.capture_image()
        data = None

        if self.last_frame is not None:
            enc_success, buffer = cv2.imencode(
                self.config['stream']['capture_encode'],
                self.last_frame
            )
            if enc_success:
                data = buffer.tobytes()

        return data

    def video_encode_stream(self):
        '''
        Gets an encoded video stream from the VideoCam module.
        Returns:
        - streamer: Frame generator for video streaming.
        '''
        streamer = self._vc.encoded_streamer()
        return streamer
