# PoshmarkNursery
PoshmarkNursery is a bot that shares available items from one's own Poshmark closet to his/her followers on a schedule. <a href="https://www.poshmark.com">Poshmark</a> is an online reselling platform, and sharing one's own items helps to promote sales.

# Motivation
I started reselling some of my clothes on Poshmark in the summer of 2019 and have caught the reselling/downsizing bug. To promote sales, I quickly learned that sharing my own items on a regular basis was a good practice. The act of sharing is very tedious so I wrote this script for sharing. 

# Prerequisites
* Python 3.7.3+
* Selenium 3.141.0+
* Chrome and compatible version of <a href="https://chromedriver.chromium.org">chromedriver</a>

# Setup
Clone the source locally:
```
git clone https://github.com/xzhou13/PoshmarkNursery
```

Modify the "config.py" file to contain your Poshmark login and password within the "". 
```
username = "username"
password = "password"
```

# To Run In Default Mode
Run in terminal with the following options:

Default mode (checks for captcha, waits one hour after sharing completes to share again, and shares in the same order as current closet):
```
python posh_nursery.py
```

# Advanced option
3 optional command line arguments:
1. 'Y' or 'N' for checking for captcha while sharing. The default value is 'Y' for checking captcha. To make it not check for captcha:
```
python posh_nursery.py N
```
This is useful when for you are not available to monitor script closely, solve captcha and manually tell the script to go on. Read about captcha [Maintenance](#Maintenance) below. When the script is not checking for captcha, it will get caught by captcha, keep sharing but sharing will be unsuccessful. You can catch this by checking on your closet at your convinence, see the sharing time of the top item. If it looks longer than the wait time you gave, it is likely caught by captcha. You can get it out of the mode by opening a browser and logging in to your closet, then sharing an item and solving a captcha or two. After this, the script should proceed sharing successfully. Note this will likely mess up the order of the closet. I recommend preserving the a particular order using "order.txt" file (read more about the 3rd optional parameter).
2. Number of seconds to wait before sharing again. 
3. 'Y' or 'N' for preserving the order based on text file "order.txt". If the text file is empty, it will get the current order and preserve it. You can customize the item order by editing the text file. As a seller, I like to share my closet in a particular order to keep the more desirable items on top. When items are no longer available for sale or new items are added, before the next round of sharing, the "order.txt" file will be updated by removing items no longer available and adding new items to the top of the "order.txt" file.
```
python posh_nursery.py {Y|N} {integerNumberOfSeconds} {Y|N}
```
For example, to share every 30 min while checking for captcha and keeping order of items based on "order.txt" file:
```
python posh_nursery.py Y 1800 Y
```

# Maintenance
* Captcha: This will get caught by captcha. In the default mode, when this happens, the script detects it, enters into the debugger mode, pauses sharing, and waits for the user to manually solve the captcha. After solving the captcha, type 'c' or 'continue' in the debugger to continue the sharing. I recommend logging into your Poshmark account on a web browser (not the selenium driven chromedriver window), and then share an item there. This will reduce the number of captchas you'll have to solve. If you attempt to solve the captcha in the selenium driven window, you'll be prompted to solve multiple captcha. When it gets caught in the log in screen, re-enter the password, check "I'm not a robot", solve the capcha in the chromedriver window. After you log in, type 'c' or 'continue' in the debugger to continue. In the case that it gets caught in the log in window, consider sharing less frequently. If you're going to be away from your computer, you can run it with checking for captcha turned off (1st optional parameter, read more about optional parameters [here](#Advanced-option)). 
* If you continously see the message "Timed out while waiting for share modal to disappear..clicking second share again" on the stdout, that might mean you've hit a sharing threshold Poshmark set, which could prohibit you from sharing for a number of hours. Consider sharing less frequently in this case.  
* chromedriver needs to be updated with the update of Chrome.
* Poshmark UI updates sometimes requires the pathes in "posh_nursery.py" to be updated accordingly.
