import configparser
import os


class Config:
    """ Responsible for actions on .ini files in which settings are stored. """

    def __init__(self, path=None):
        """
        :param path: where the file containing various settings can be found.
        """

        self.config = configparser.ConfigParser()
        # If there was no config file, config class would be useless.
        if path and os.path.isfile(path):
            self.path = path
        else:
            raise FileNotFoundError("File does not exist.")

    def get_value(self, section, key):
        """
        Returns value given a section and a key.

        :param section: section of an .ini file that should be read.
        :param key: key which should be used to get the corresponding value.
        """

        self.config.read(self.path)

        return self.config[section][key]

