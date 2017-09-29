## About
`steamCLI` is a command line tool that allows you to search Steam for 
information about the game/app straight from the command line. It supports 
overall and recent ratings, current prices on Steam, historical low price, 
different currencies and regions.

## Installation
To use `steamCLI`, you need to have [Python 3.6+](https://www.python.org/downloads/). 
To check your version, issue the following command in the terminal:
~~~
python3 --version
~~~
Once you have correct version of Python installed, enter the following command:
~~~
pip3.6 install steamcli
~~~ 
This will download and install `steamCLI` and its dependencies for Python 3.6. 
If you use `pip install ...`, however, it will most likely be installed for 
Python 2.7, since most major OSes rely on it in one way or the other. The app
will not work on 2.7.

Once `pip` installs the app, you can already use it. However, you will not be 
able to access historical data (such as lowest prices). First, you need to get an API key 
for Is There Any Deal. You will need  to register your app (`steamCLI`) and 
request an API  key. You can do it [here](https://isthereanydeal.com/apps/new/). 
Additional documentation is available [here](http://docs.itad.apiary.io/#introduction/your-apps).

Export the key you have been given as environment variable:
~~~
export steamCLI=[your_API_key]
~~~
You can also set environment variable permanently: 
- [Mac](https://stackoverflow.com/questions/22502759/mac-os-x-10-9-setting-permanent-environment-variables)
- [Ubuntu](https://stackoverflow.com/questions/13046624/how-to-permanently-export-a-variable-in-linux)

Now you should be able to fully use the app.

## Usage
You can see what you can do with the script by calling:
~~~
steamcli -h
~~~
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
reviews for Borderlands, you'd simply have to call
~~~
steamcli -t
~~~
and enter `borderlands` (title is case-insensitive). Example output:

                       *** Borderlands (26 Oct, 2009) ***                      
                          9.99 GBP (0% from 9.99 GBP)                          
                              Metacritic score: 81 
                              
## Tests
If you have cloned the repository, you can run the tests from the Terminal. 
To do so, navigate to the root folder of `steamCLI` app and issue the following command:
~~~
python -m unittest discover
~~~ 

## Cloning the and Setting Up the Project
1. Ensure you have [Python 3.6](https://www.python.org/downloads/) installed:
~~~ 
python3 --version
~~~ 
2. Clone the project:
~~~
git clone git@github.com:vilisimo/steamCLI.git
~~~
3. __(Recommended)__ Ensure `virtualenvwrapper` is installed:
~~~
pip list | grep virtualenvwrapper
~~~ 
  * If it is not installed, enter:
~~~
pip install virtualenvwrapper
~~~
4. __(Recommended)__ Create virtual environment for the project: 
~~~
mkvirtualenv -p python3.6 steamCLI
~~~
5. Install required packages in _requirements.txt_:
~~~
pip install -r requirements.txt`
~~~
6. Update a `PYTHONPATH` environment variable: 
~~~
PYTHONPATH=$PYTHONPATH:/path/to/root/folder
~~~
  * If you're using `virtualenvwrapper`, you can write:
~~~
add2virtualenv /path/to/root/folder
~~~
7. Get an API key for Is There Any Deal (if you want to see the historical 
low). For that, you need register your app and request an API key. You can do
 it [here](https://isthereanydeal.com/apps/new/). Additional documentation 
 available [here](http://docs.itad.apiary.io/#introduction/your-apps).
8. Export the key as environment variable:
~~~
export steamCLI=[your_API_key]
~~~
  * You can also set environment variable permanently: 
    - [Mac](https://stackoverflow.com/questions/22502759/mac-os-x-10-9-setting-permanent-environment-variables)
    - [Ubuntu](https://stackoverflow.com/questions/13046624/how-to-permanently-export-a-variable-in-linux)
