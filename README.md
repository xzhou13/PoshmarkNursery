# PoshmarkNursery
PoshmarkNursery is a bot that shares available items from one's own Poshmark closet to his/her followers on a schedule. It can also be configured to share back items from people who shared your items or share items from a given list of closets. <a href="https://www.poshmark.com">Poshmark</a> is an online reselling platform, and sharing one's own items helps to promote sales.

# Motivation
I started reselling some of my clothes on Poshmark in the summer of 2019 and have caught the reselling/downsizing bug. To promote sales, I quickly learned that sharing my own items on a regular basis was a good practice. The act of sharing is very tedious so I wrote this script for sharing. I've since added the option to share other poshers' closets if they share from mine, although I suspect it doesn't enhance sales as much as sharing your own does (I tried it for a few weeks and stopped since it didn't seem to increase likes or sales).

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

Default mode (self-share once every 60 min while checking for captcha, sharing in the same order as current closet, and not sharing back or following closets that shared your item):
```
python posh_nursery.py
```

# Advanced options
Five optional command line arguments:
```
python posh_nursery.py {Y|N} {Y|N} {integerNumberOfSeconds} {Y|N} {Y|N}
```

1. 'Y' or 'N' for checking for captcha while sharing. The default value is 'Y' for checking captcha. The 'N' option, or NOT checking for captcha while sharing is useful when for you are not available to monitor script closely, solve captcha and manually tell the script to go on. Read about captcha [Maintenance](#Maintenance) below. When the script is not checking for captcha, it will get caught by captcha, keep sharing but sharing will be unsuccessful. You can catch this by checking on your closet at your convinence, see the sharing time of the top item. If it looks longer than the wait time you gave, it is likely caught by captcha. You can get it out of the mode by opening a browser and logging in to your closet, then sharing an item and solving a captcha or two. After this, the script should proceed sharing successfully. Note this will likely mess up the order of the closet. I recommend preserving the a particular order using "order.txt" file (read more about the 4th optional parameter). 
To make it not check for captcha, run:
```
python posh_nursery.py N
```

2. 'Y' or 'N' for whether or not to share closets from the file "closetsToShare.txt". Default is 'N'. Note when you select 'Y', the program will only share closets in "closetsToShare.txt" before terminating. You can specify whether or not to check for captcha with the 1st parameter. It's recommended that you run it in checking for captcha mode if you're sharing large closets. Inside the "closetsToShare.txt" file, put the closet names you want to share and place each closet in a separate line. For example, to share other closets in "closetsToShare.txt" while checking for captcha, run:
```
python posh_nursery.py Y Y
```
An example "closetsToShare.txt" is the following if the two closets I want to share are "closet_name_1" and "closet_name_2":
```
closet_name_1
closet_name_2
```

3. Number of seconds to wait before sharing again. Default is set to an hour if you don't specify. For example, to self-share every 30 min while not checking for captcha, run:
```
python posh_nursery.py N N 1800
```

4. 'Y' or 'N' for preserving the order based on text file "order.txt". Default is 'N'. If the text file is empty, it will get the current order and preserve it. You can customize the item order by editing the text file. As a seller, I like to share my closet in a particular order to keep the more desirable items on top. When items are no longer available for sale or new items are added, before the next round of sharing, the "order.txt" file will be updated by removing items no longer available and adding new items to the top of the "order.txt" file. For example, to self-share every 30 min while checking for captcha and keeping order of items based on "order.txt" file, run:
```
python posh_nursery.py Y N 1800 Y
```

5. 'Y' or 'N' to share back after each round of self-share. Default is 'N'. In this mode, it will scroll your poshmark.com/news/share page 5 times, share 8 items from the closets that shared your items. It will also keep track of all the closets you shared and won't share the same closet again. For example, to self-share and share back and follow other closets every 30 min while checking for captcha and keeping order of items based on "order.txt" file, run:
```
python posh_nursery.py Y N 1800 Y Y
```

<p align="center">
  <img src="demo-image-01.gif">
</p>

Tip: Consider sharing in "headless" mode. This will eliminate the selenium driven chrome window from popping up. Uncomment these 2 lines in the "posh_nursery.py" file by removing the # in front of the 2 lines:
```
self.chrome_options.add_argument("--headless")
self.chrome_options.add_argument("--window-size=1920x1080")
```

# Maintenance
* Captcha: This will get caught by captcha. In the default mode, when this happens, the script detects it, enters into the debugger mode, pauses sharing, and waits for the user to manually solve the captcha. After solving the captcha, type 'c' or 'continue' in the debugger to continue the sharing. I recommend logging into your Poshmark account on a web browser (not the selenium driven chromedriver window), and then share an item there. This will reduce the number of captchas you'll have to solve. If you attempt to solve the captcha in the selenium driven window, you'll be prompted to solve multiple captcha. If it gets caught in the log in screen, re-enter the password, check "I'm not a robot", solve the capcha in the chromedriver window. After you log in, type 'c' or 'continue' in the debugger to continue. In the case that it gets caught in the log in window, consider running the script less frequently. If you're going to be away from your computer, you can run it with checking for captcha turned off (1st optional parameter, read more about optional parameters [here](#Advanced-options)). 
* If you continously see the message "Timed out while waiting for share modal to disappear..clicking second share again" on the stdout, that might mean you've hit a sharing threshold Poshmark set, which could prohibit you from sharing for a number of hours. Consider sharing less frequently in this case. I've only hit this limit when I shared with this script non-stop for a few hours. 
* chromedriver needs to be updated with the update of Chrome.
* Poshmark UI updates sometimes requires the pathes in "posh_nursery.py" to be updated accordingly.
* If you observe the script not being able to obtain same number of available items as that on the stats page, it's most likely having difficulty scrolling down to the very buttom of the page, consider incremeting the "srollWaitTime" variable. This should increase the wait time after each scroll.
