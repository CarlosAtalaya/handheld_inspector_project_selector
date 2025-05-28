import csv


class QualityCriteria():
    '''
    QualityCriteria class.
    Handles criteria generation based on given external data.
    '''
    def __init__(self, config):
        # Config
        self.config = config
        # Attributes
        self.raw = []
        self.headers = []
        # load data
        self._load_data()

    def _load_data(self):
        '''
        Load data. This is set up via config attribute.
        '''
        with open(
            self.config['csv']['path'], 'r', encoding='utf-8', newline=''
        ) as f:
            # Read file
            reader = csv.reader(f)
            raw_rows = list(reader)
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
        index = None
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
        return sorted(set(row[index].upper() for row in self.raw))

    def get_defects(self):
        '''
        Returns a set of defect types according to given quality criteria.
        '''
        index = self._get_index(self.config['csv']['defect_keyword'])
        return self._build_set(index)

    def get_quality(self):
        '''
        Returns a set of quality surface options according to given
        quality criteria.
        '''
        index = self._get_index(self.config['csv']['quality_keyword'])
        return self._build_set(index)

    def get_finish(self):
        '''
        Returns a set of finish types according to given quality criteria.
        '''
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
        founded_criteria = None

        defect_idx = self._get_index(self.config['csv']['defect_keyword'])
        quality_idx = self._get_index(self.config['csv']['quality_keyword'])
        finish_idx = self._get_index(self.config['csv']['finish_keyword'])
        criteria_idx = self._get_index(self.config['csv']['criteria_keyword'])

        if None not in (defect_idx, quality_idx, finish_idx, criteria_idx):
            matches = [
                row[criteria_idx]
                for row in self.raw
                if (row[defect_idx].strip().lower() == defect and
                    row[quality_idx].strip().lower() == quality and
                    row[finish_idx].strip().lower() == finish)
            ]

            # Make sure there's only 1 match
            if len(matches) == 1:
                founded_criteria = matches[0]

        return founded_criteria
