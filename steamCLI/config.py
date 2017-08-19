import configparser
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    """
    Responsible for actions on .ini files in which settings are stored.

    If only get_value() is ever used, class might be an overkill.
    """

    def __init__(self, package_folder: str=ROOT, *args: str):
        """
        :param package_folder: project root folder.
        :param *args: folders + file name needed to navigate to the .ini file.
        """

        package = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', package_folder))
        self.config = configparser.ConfigParser()
        self.path = os.path.join(package, *args)

        # If there was no config file, config class would be useless.
        if not os.path.isfile(self.path):
            raise FileNotFoundError("File does not exist.")

    def get_value(self, section: str, key: str) -> str:
        """
        Returns value given a section and a key.

        :param section: section of an .ini file that should be read.
        :param key: key which should be used to get the corresponding value.
        """

        self.config.read(self.path)

        return self.config[section][key]
