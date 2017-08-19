from distutils.core import setup

setup(
    name='steamCLI',
    version='0.0.1',
    packages=['test', 'steamCLI'],
    url='https://github.com/vilisimo/steamCLI',
    license='MIT License',
    author='vilisimo',
    author_email='vilisimo@gmail.com',
    description='Find price information about games on Steam from the command line.',
    long_description='The app provides a simple to use command line interface '
                     'to check prices of  apps on Steam and compare them with '
                     'historical lows. For that, https://isthereanydeal.com/ '
                     'is used. To see a more in-depth and up-to-date description, '
                     'please see the provided GitHub page.'
)
