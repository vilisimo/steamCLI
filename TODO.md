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