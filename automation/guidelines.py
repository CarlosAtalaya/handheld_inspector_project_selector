from handheld.constants import (
    CT_LIGHT_SIDE_GUIDELINE,
    CT_DARK_SIDE_GUIDELINE,
    CT_LIGHT_SIDE_DEFECTS
)


class GuidelineSelector:
    def __init__(self):
        self.light_defects = CT_LIGHT_SIDE_DEFECTS

    def choose_guideline_side(self, defect_type):
        '''
        Choose guideline to be displayed over video feed.
        Args:
        - defect_name (str): defect name, depending on defect guideline
        will be displayed in dark side or light side.
        Returns:
        - chosen_guideline_side (str): side where guideline will be shown.
        '''
        chosen_guideline_side = None
        if defect_type in self.light_defects:
            chosen_guideline_side = CT_LIGHT_SIDE_GUIDELINE
        else:
            chosen_guideline_side = CT_DARK_SIDE_GUIDELINE
        return chosen_guideline_side
