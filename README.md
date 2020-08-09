# PoshmarkNursery
PoshmarkNursery is a bot that shares available items from one's own Poshmark closet to his/her followers on a schedule. <a href="https://www.poshmark.com">Poshmark</a> is an online reselling platform, and sharing one's own items helps to promote sales.

# Motivation
I started reselling some of my clothes on Poshmark in the summer of 2019 and have caught the reselling/downsizing bug. To promote sales, I quickly learned that sharing my own items on a regular basis was a good practice. The act of sharing is very tedious so I wrote this script for sharing. 

# Prerequisites
* Python 3.4+
* Selenium 3.141.0+
* Chrome and compatible version of <a href="https://chromedriver.chromium.org">chromedriver</a>

# Setup
Clone the source locally:
```
$ git clone https://github.com/xzhou13/PoshmarkNursery
```

Modify the "config.py" file to contain your Poshmark login and password within the "". 
```
username = "username"
password = "password"
```

# To Run
Run in terminal with the following options:

Default mode (wait one hour after sharing completes to share again, shares in the same order as current closet):
```
$ python3 posh_nursery.py
```

Advanced option takes 2 command line arguments:
1. Number of seconds to wait before sharing again. 
2. 'Y' or 'N' for preserving the order based on text file "order.txt". If the text file is empty, it will get the current order and preserve it. You can customize the item order by editing the text file. As a seller, I like to share my closet in a particular order to keep the more desirable items on top.
```
$ python3 posh_nursery.py <integerNumberOfSeconds> <Y/N>
```

# Maintenance
* Captcha: This will get caught by captcha, and when that happens, the script detects it, enters into the debugger mode and waits for the user to manually solve the captcha. After solving the captcha, type 'continue' in the debugger to continue the sharing. I recommend logging into your Poshmark account on a web browser (not the selenium driven chromedriver window), and then share an item there. This will reduce the number of captchas you'll have to solve. If you attempt to solve the captcha in the selenium driven window, you'll be prompted to solve multiple captcha. When it gets caught in the log in screen, check "I'm not a robot" and solve the capcha in the chromedriver window. In the case that it gets caught in the log in window, consider sharing less frequently.
* chromedriver needs to be updated with the update of Chrome.
* Poshmark UI updates sometimes requires the pathes in "posh_nursery.py" to be updated accordingly.
