## About
steamCLI is a command line interface tool that allows a user to search steam 
for information about the game/app straight form command line. 

## Installation
- Pull the project.
- Install required packages in requirements.txt.
- Get an API key for Is There Any Deal (if you want to see the historical 
low). For that, you need register your app and request an API key. You can do
 it [here](https://isthereanydeal.com/apps/new/). Additional documentation 
 available [here](http://docs.itad.apiary.io/#introduction/your-apps).
- Open up [resources.ini](../../tree/master/steamCLI/resources.ini), give 
  value to _api_key_ in **_IsThereAnyDealAPI_** section. 
 
## Future
At the moment, the bulk of features that I have planned are functional. 
However, there is still much room for improvement:

**Code-wise:**
 - Creating more tests to ensure everything works properly.
 - Refactoring the code to reduce code duplication and increase maintainability.
 - Introducing parallel requests (most likely candidate: do scraping and 
 lowest historical price search at the same time) to reduce waiting.
 - Figuring out what ITAD uses to process titles so that non-latin letters 
 can be represented properly (e.g., Russian alphabet).

**Functionality:**
 - Showing whether the game has co-op, multi-player, controller support.
 - Showing whether the user has the game or not.
 - ...aggregating and showing other useful information from variety of sources.
 
**Misc**
 - Setting up _setup.py_ so that the steamCLI could be installed through pip.
 - Writing up instructions on how to install steamCLI so that it could be 
 called up anywhere from the console by writing something like `>>> steam -t`
  or `>>>steamCLI -t`.

## Things Learned
The main goal of the project was to learn new programming techniques. The 
project allowed me to get exposure to:
 - _argparse_ module and creating CLI applications.
 - _unittest.mock_, mocking objects and methods, as well as general unit 
   testing and keeping your tests small and isolated.
 - _configparser_ and keeping your data outside the code.
 - APIs and how to work with them using _requests_.
 - Basics of webscraping with _BeautifulSoup_.
 - Working with JSON data.