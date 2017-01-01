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
At the moment, the project is in early stages. Key features that are planned
for the future are described below. Features under _Optional_ are those that 
can be enabled or disabled by passing different parameters when calling the 
steamCLI.

**Default:**
 - Getting game's price (current), average user rating, release date.
 - Getting information about the lowest recorded price of a particular game/app.
 - Getting information about where to find the best deal for an app.

**Optional:**
 - Showing whether the game has co-op, multi-player, controller support.

## Things Learned
The main goal of the project was to learn new techniques. The project allowed
 me to get exposure to:
 - _argparse_ module and creating CLI applications.
 - _unittest.mock_, mocking objects and methods, as well as general unit 
   testing and keeping your tests small and isolated.
 - _configparser_ and keeping your data outside the code.
 - APIs and how to work with them using _requests_.
 - Basics of webscraping with _BeautifulSoup_.
 - Working with JSON data.