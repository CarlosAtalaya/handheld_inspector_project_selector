import cv2
import os


class LocalOutput:
    '''
    Handles local storage tasks.
    '''
    def __init__(self, config):
        self.config = config
        self.save_path = config['io']['local_save_path']

    def generate_local_path(self, file_name):
        '''
        Builds the full local path for saving the file.
        Args:
        - file_name (str): use file_name to generate localpath.
        Returns:
        - local_path (str): generated local_path to save file.
        '''
        local_path = os.path.join(self.save_path, file_name)

        return local_path

    def imwrite(self, image, output_path):
        '''
        Saves given image locally with a timestamped filename.
        Args:
        - image (np.array): image to be saved locally.
        - output_path (str): local path to save given image.
        '''
        cv2.imwrite(output_path, image)
