import csv
import os
import glob


class QualityCriteria():
    '''
    QualityCriteria class.
    Handles criteria generation based on given external data.
    Now supports project-specific CSV files.
    '''

    def __init__(self, config):
        # Config
        self.config = config
        # Attributes
        self.raw = []
        self.headers = []
        self.csv_base_path = config['csv']['path']
        self.current_project = None
        self.csv_path = None

    def discover_available_projects(self):
        '''
        Discover available projects based on CSV files in config directory.
        Returns:
        - list: Available project names based on CSV files
        '''
        projects = []

        if os.path.exists(self.csv_base_path):
            csv_pattern = os.path.join(self.csv_base_path, '*.csv')
            csv_files = glob.glob(csv_pattern)

            for csv_file in csv_files:
                filename = os.path.basename(csv_file)
                # Get project name: everything before the first '_'
                if '_' in filename:
                    project_name = filename.split('_')[0].upper()
                    if project_name not in projects:
                        projects.append(project_name)

            projects = sorted(projects)

        return projects

    def set_project(self, project_name):
        '''
        Set the current project and load its corresponding CSV data.
        Args:
        - project_name (str): Name of the project
        '''
        self.current_project = project_name.lower()

        # Find CSV file for this project
        csv_pattern = os.path.join(
            self.csv_base_path,
            f'{self.current_project}_*.csv'
        )
        csv_files = glob.glob(csv_pattern)

        if csv_files:
            # Take the first matching CSV file
            self.csv_path = csv_files[0]
            self._load_data()
        else:
            raise FileNotFoundError(
                f'No CSV file found for project: {project_name}'
            )

    def _load_data(self):
        '''
        Load data from the current CSV path.
        '''
        if not self.csv_path or not os.path.exists(self.csv_path):
            raise FileNotFoundError(f'CSV file not found: {self.csv_path}')

        with open(
            self.csv_path, 'r', encoding='utf-8', newline=''
        ) as f:
            # Read file
            reader = csv.reader(f)
            raw_rows = list(reader)

            if not raw_rows:
                raise ValueError(f'CSV file is empty: {self.csv_path}')

            # Save headers and all the other rows
            self.headers = raw_rows[0]
            self.raw = raw_rows[1:]

    def _get_index(self, keyword):
        '''
        Given a keyword (i.e. defect) it returns corresponding index, avoiding
        to hardcode it.
        Args:
        - keyword (str): keyword used to get index.
        '''
        if not self.headers:
            return None

        try:
            index = self.headers.index(keyword)
        except ValueError:
            index = None

        return index

    def _build_set(self, index):
        '''
        Build a set based on given index.
        Args:
        - index (int): column index to build set.
        '''
        if index is None or not self.raw:
            return []
        return sorted(
            set(row[index].upper() for row in self.raw if len(row) > index)
        )

    def get_defects(self):
        '''
        Returns a set of defect types according to given quality criteria.
        '''
        if not self.raw:
            return []
        index = self._get_index(self.config['csv']['defect_keyword'])
        return self._build_set(index)

    def get_quality(self):
        '''
        Returns a set of quality surface options according to given
        quality criteria.
        '''
        if not self.raw:
            return []
        index = self._get_index(self.config['csv']['quality_keyword'])
        return self._build_set(index)

    def get_finish(self):
        '''
        Returns a set of finish types according to given quality criteria.
        '''
        if not self.raw:
            return []
        index = self._get_index(self.config['csv']['finish_keyword'])
        return self._build_set(index)

    def get_criteria(self, defect, quality, finish):
        '''
        Given defect, quality and finish, finds the corresponding criteria
        from raw data.

        Args:
        - defect (str): defect name.
        - quality (str): surface quality type.
        - finish (str): finish type.

        Returns:
        - founded_criteria (str): corresponding criteria if found, else None.
        '''
        if not self.raw:
            return None

        founded_criteria = None

        defect_idx = self._get_index(self.config['csv']['defect_keyword'])
        quality_idx = self._get_index(self.config['csv']['quality_keyword'])
        finish_idx = self._get_index(self.config['csv']['finish_keyword'])
        criteria_idx = self._get_index(self.config['csv']['criteria_keyword'])

        if None not in (defect_idx, quality_idx, finish_idx, criteria_idx):
            matches = [
                row[criteria_idx]
                for row in self.raw
                if (
                    len(row) > max(
                        defect_idx,
                        quality_idx,
                        finish_idx,
                        criteria_idx
                    )
                    and row[defect_idx].strip().lower() == defect.lower()
                    and row[quality_idx].strip().lower() == quality.lower()
                    and row[finish_idx].strip().lower() == finish.lower()
                )
            ]

            if len(matches) >= 1:
                founded_criteria = matches[0]

        return founded_criteria
