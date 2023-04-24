# Crypt-TA

### Description

Crypt-TA Sentinel is a capstone project meant to showcase most of what I have learned to do with Python so far. It is meant to demonstrate the application of newly acquired skills using the REST api, flask, numpy, pandas, matplotlib, and the core Python libraries, all in one project. It is also meant to prove that I am capable of developing a fullstack webapp and deploying it on the internet. The app is the result of a continued journey through the world of Python which 
began with self-study, a bootcamp, coding books, and lots of googling.

### How to setup

This project is meant to be deployed as a webapp on a webserver using `gunicorn`.
It can also be run locally with the flask development server, though not for
production purposes. 

### Dependencies

##### Python version

The version of Python used for the project is. It is recommended to use this
exact version as other versions are untested and there may be problems with the
requirements on other versions.

`Python 3.8.14`


##### TA-lib

Most of the technical analysis indicators are generated with TA-lib library.
The Python TA-lib library is basically a wrapper for the underlying TA-lib module  
which is written in C. The C module powers the Python library.

As a result, the C module of TA-lib must be installed on the host machine before
proceeding with the steps below. 

This can be accomplished by coducting the following BEFORE proceeding with pip;

`wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz`  

`tar -xzf ta-lib-0.4.0-src.tar.gz`  

`cd ta-lib/`  

`./configure --prefix=/usr`  

`make`  

`sudo make install`  

`pip install numpy`
  
_Note: If using a venv (which is recommended) the above should be conducted from
within the venv and should be done BEFORE `pip install -r requirements.txt`  
  
  
For more info see the following:  
  
(https://ta-lib.github.io/ta-lib-python/install.html)  
(https://pypi.org/project/TA-Lib/)

##### Directories

Make sure the following directories exist in the root webapp folder
or the webapp will not start;

`datasets`

`txn_vol`

`descriptions`

`fiat_exch_rates`

`notcurrentlyupdated`


#### Installation 

After the above, to setup the project simply do:

`pip install -r requirements.txt`

`flask run`

Once this is done the webapp can be accessed through a browser at the url
provided by the debug server.

The app will run in the background until explicitly terminated. 
It will query the APIs every 20 minutes to update it's datasets.

#### Quirks  

During the late night hours of the UTZ, the APIs do not serve data and the app 
cannot update. This is normal and the web app has contingencies to keep it 
running during this time.  

### Disclaimer

All content provided herein on this website, hyperlinked sites, associated applications,
forums, blogs, social media accounts and other platforms or websites is for general information purposes only, procured from third party sources. 

I make no warranties of any kind in relation to this content, including but not limited to accuracy and up-to-date status. No part of the content provided on this website constitutes financial advice, legal advice or any other form of advice meant for your specific reliance for any purpose whatsoever.

Any use or reliance on the content of this website is solely at your own risk and discretion.
You should conduct your own research, review, analyse and verify any content before relying on it. Trading is a highly risky activity that can lead to major losses, please therefore consult your financial advisor before making any decision. No content on this site is meant to be a solicitation or offer. 

There is no partnership or affiliation of any kind between this site and any hyperlinked resources. There is no partnership or affiliation of any kind between this site and the data resources that power it.

