## About
steamCLI is a command line interface tool that allows a user to search steam 
for information about the game/app straight form command line. 

## Installation
- Clone the project: `git clone git@github.com:vilisimo/steamCLI.git`
- Install required packages in _requirements.txt_: `pip install -r 
requirements.txt`
- Get an API key for Is There Any Deal (if you want to see the historical 
low). For that, you need register your app and request an API key. You can do
 it [here](https://isthereanydeal.com/apps/new/). Additional documentation 
 available [here](http://docs.itad.apiary.io/#introduction/your-apps).
- Open up [resources.ini](../../tree/master/steamCLI/resources.ini), change 
  _api_key_ in **_IsThereAnyDealAPI_** section to your API key. 
 
## Future
**Code-wise:**
 - More tests to ensure everything works properly.
 - Refactoring the code to reduce code duplication and increase maintainability.
 - Introducing parallel requests (most likely candidate: do scraping and 
 lowest historical price search at the same time) to reduce waiting.
 - Figuring out what the hell ITAD uses to process titles so that non-latin letters 
 can be represented properly (e.g., Russian alphabet). Also, wrapping my head around 
 their logic of omitting some words (like 'the') but not the others (like 'a', 'an').
 - Add type-hints to simplify development and readability.
 - Refactor print statements out to specialized class _(in progress)_.

**Functionality:**
 - Showing whether the game has co-op, multi-player, controller support.
 - Showing whether the user has the game or not.
 - ...aggregating and showing other useful information from variety of sources.
 
**Misc**
 - Setting up _setup.py_ so that the steamCLI could be installed through _pip_.
 - Writing up instructions on how to install steamCLI so that it could be 
 called up anywhere from the console by writing something like `>>> steam -t`
  or `>>> steamCLI -t`.

