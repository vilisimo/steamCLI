## About
steamCLI is a command line tool that allows a user to search steam 
for information about the game/app straight from the command line. 
It supports overall and recent ratings, current prices on Steam, historical 
low price, different currencies and regions.

## Usage
You can see what you can do with the script by calling `>>> python main.py -h`.
Nevertheless, it currently has these options:

    -h, --help            show this help message and exit
    -t, --title           title of a game or an app on Steam
    -id val, --appid val  id of a game or an app on Steam
    -d, --description     include to see the app description
    -s, --scores          include to see user review scores
    -r val, --region val  which region the price should be shown for Available
                        values: au, br, ca, cn, eu1, eu2, ru, tr, uk, us
    -l, --historical_low  include to see historical low price

Hence, if you wanted to find out release date, price, discount and metacritic 
reviews for Borderlands, you'd simply have to call `>>> python main.py -t` and 
enter `borderlands` (title is case-insensitive). Example output:

                       *** Borderlands (26 Oct, 2009) ***                      
                          9.99 GBP (0% from 9.99 GBP)                          
                              Metacritic score: 81                             


## Installation
- Ensure you have [Python 3.6](https://www.python.org/downloads/) installed. 
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
 - Introducing async requests (most likely candidate: do scraping and 
 lowest historical price search at the same time) to reduce waiting.

**Misc**
 - Setting up _setup.py_ so that the steamCLI could be installed through _pip_.
 - Writing up instructions on how to install steamCLI so that it could be 
 called up anywhere from the console by writing something like `>>> steam -t`
  or `>>> steamcli -t`.
 - Figuring out what ITAD uses to process titles so that non-latin letters 
 can be represented properly (e.g., Russian alphabet). 
 - Figuring out their logic behind omitting some words (like 'the') but not the 
 others (like 'a', 'an').