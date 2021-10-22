from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from datetime import datetime, timedelta
import sys, random, pdb, time
import config
   
class Posh_Nursery:
   def __init__(self, username, password, slowMode = False, debug = False, checkCaptcha = True, toShareClosetsFromFile = False, timeToWait = 3600, maintainOrder = False, shareBack = False):
      self.username = username
      self.password = password
      self.numItemsToShareFromOtherClosets = 8
      self.timeOutSecs = 10
      self.scrollWaitTime = 5
      self.numTimesToScroll = 5
      self.chrome_options = Options()
      #self.chrome_options.add_argument("--headless")
      #self.chrome_options.add_argument("--window-size=1920x1080")
      self.driver = webdriver.Chrome(options = self.chrome_options)
      self.loginUrl = "https://poshmark.com/login"
      self.closetUrl = "https://poshmark.com/closet"
      self.shareNewsUrl = "https://poshmark.com/news/share"
      self.closetStatsUrl = "https://poshmark.com/users/self/closet_stats"
      self.statsXPath = "((//div[@class='stats-container__border stats__content'])[1]//h1[@class='posh-stats__value'])[1]"
      self.loginID = "login_form_username_email"
      self.loginXPath = "//input[@name='userHandle']"
      self.passwordID = "login_form_password"
      self.passwordXPath = "//input[@name='password']"
      self.firstShareXPath = "//i[@class='icon share-gray-large']"
      self.socialBarXPath = "//div[@class='social-action-bar tile__social-actions']"
      self.itemNameXPath = "//a[@class='tile__title tc--b']"
      self.secondShareXPath = "//i[@class='icon pm-logo-white']"
      self.shareModalTitleXPath = "//h5[@class='modal__title']"
      self.captchaModalTitleXPath = "//h5[@class='modal__title']"
      self.captchaXButtonXPath = "//button[@class='btn btn--close modal__close-btn simple-modal-close']"
      self.closetNameXPath = "//p[@class='wb--ww tc--g']//a" # used for sharing back
      self.followButtonXPath = "//button[@class='al--right btn follow__btn m--l--2 m--r--1 btn--primary']" # used to follow
      if maintainOrder: 
         self.orderTextFile = "order.txt"
      else:
         self.orderTextFile = ""
      self.closetsToShareFile = "closetsToShare.txt"
      self.availableUrl = self.getClosetAvailableUrl(self.username)
      self.hasUpdate = False # used when preserving closet order to keep track of newly added item
      self.closetSize = 0
      self.shareButtons = []
      self.orderedShareButtons = []
      self.itemNameElements = []
      self.itemNames = []
      self.closetOrder = []
      self.closetOrderDict = {}
      self.closetSharedBack = []
      self.checkCaptcha = checkCaptcha
      self.toShareClosetsFromFile = toShareClosetsFromFile
      self.debug = debug
      self.shareBack = shareBack
      self.slowMode = slowMode
      self.timeToWait = timeToWait
      self.driver.minimize_window()
   
   def clearsAndResets(self, sharingMine = True):
      if sharingMine:
         self.hasUpdate = False
         self.orderedShareButtons = []
         self.closetOrder = []
         self.closetOrderDict = {}
      self.closetSize = 0
      self.shareButtons = []
      self.itemNameElements = []
      self.itemNames = []
 
   def quit(self):   
      self.driver.quit()
   
   def getRandomSec(self):
      return random.randrange(1, 5, 1)

   def waitTillClickable(self, findByIdOrPath, idOrPath, timeOutSecs = 10):
      clickableElement = False
      if findByIdOrPath == 'id':
         try:
            clickableElement = WebDriverWait(self.driver, timeOutSecs).until(EC.element_to_be_clickable((By.ID, idOrPath)))
         except TimeoutException as e:
            print("Timed out at locating element by " + findByIdOrPath + " at " + str(idOrPath) + ": " + str(e))
            return False
      else:
         try:
            clickableElement = WebDriverWait(self.driver, timeOutSecs).until(EC.element_to_be_clickable((By.XPATH, idOrPath)))
         except TimeoutException as e:
            print("Timed out at locating element by " + findByIdOrPath + " at " + str(idOrPath) + ": " + str(e))
            return False
      return clickableElement

   def waitForAnElementByXPath(self, xpath, elementName):
      try:
         element = WebDriverWait(self.driver, self.timeOutSecs).until(EC.presence_of_element_located((By.XPATH, xpath)))
      except TimeoutException as e:
         print("Timed out while waiting for " + elementName + " to pop up..waiting again")
         print(e)
         return False
      return element

   def getLogInElement(self, elementID, elementXPath):
      element = self.waitTillClickable("id", elementID)
      if not element:
         print("Time out at locating ID: " + elementID)
         element = self.waitTillClickable("xpath", elementXPath)
         if not element:
            print("Timed out again with xpath")
            print("Please manually enter username/password, then type 'c' or 'continue'")
            pdb.set_trace()
      return element   

   def enterTxtSlowly(self, element, text):
      for char in text:
         element.send_keys(char)
         time.sleep(random.random())

   def enterUserName(self):
      userNameElement = self.getLogInElement(self.loginID, self.loginXPath)
      if not userNameElement:
         print("Username element not obtained from page, exiting...")
         self.quit()
         sys.exit() 
      self.enterTxtSlowly(userNameElement, self.username)

   def enterAndSubmitPassword(self):
      passwordElement = self.getLogInElement(self.passwordID, self.passwordXPath)
      if not passwordElement:
         print("Password element not obtained from page, exiting...")
         self.quit()
         sys.exit()
      self.enterTxtSlowly(passwordElement, self.password)
      passwordElement.submit()
             
   def login(self): 
      self.driver.get(self.loginUrl)      
      self.enterUserName()
      self.enterAndSubmitPassword()
      if self.debug:  
         print(self.driver.title)
      try:
         WebDriverWait(self.driver, self.timeOutSecs).until(EC.title_contains("Feed"))
      except Exception as e:
         print("ERROR: logging error{}".format(e))
         print("Please solve captcha and then type 'c' or 'continue'")
         self.driver.switch_to.window(self.driver.current_window_handle) 
         pdb.set_trace()
         self.driver.minimize_window()
      print("Logged into poshmark")

   def getClosetAvailableUrl(self, username):   
      availableUrl = "{}/{}{}".format(self.closetUrl, username, "?availability=available")
      return availableUrl 

   def scrollCloset(self):
      lastHeight = self.driver.execute_script("return document.body.scrollHeight")
      scrollMore = True
      print("Scrolling")
      while scrollMore:
         self.driver.switch_to.window(self.driver.current_window_handle) 
         self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
         time.sleep(self.scrollWaitTime)
         newHeight = self.driver.execute_script("return document.body.scrollHeight")
         if newHeight == lastHeight:
            scrollMore = False
         lastHeight = newHeight
   
   def scrollToTop(self):
      self.driver.switch_to.window(self.driver.current_window_handle)
      self.driver.execute_script("window.scrollTo(0, 0);")
  
   def readInClosetOrder(self):
      self.closetOrder = [line.rstrip('\n') for line in open(self.orderTextFile)]
      for n,sortedItem in enumerate(self.closetOrder):
         self.closetOrderDict[sortedItem] = n

   def checkItemInOrderTextFile(self, item):
      if item in self.closetOrderDict.keys():
         return True
      else:
         return False

   def checkItemInCloset(self, item):
      if item in self.itemNames:
         return True
      else:
         return False

   def updateOrderFile(self):
      for itemName in reversed(self.itemNames):
         # append to begining of order file
         if not self.checkItemInOrderTextFile(itemName):
            self.hasUpdate = True
            print(itemName + " not in order text file")
            print("Adding " + itemName)
            with open(self.orderTextFile, "r") as f:
               lines = f.readlines()
            with open(self.orderTextFile, "w") as f:
               f.write(itemName + "\n")
               for line in lines:
                  item = line.strip("\n")
                  if item != itemName:
                     f.write(line)

      for closetOrderItem in self.closetOrderDict.keys():
         if not self.checkItemInCloset(closetOrderItem):        
            self.hasUpdate = True
            # delete from order file
            print(closetOrderItem + " is not in closet anymore")
            print("Deleting " + closetOrderItem)
            with open(self.orderTextFile, "r") as f:
               lines = f.readlines()
            with open(self.orderTextFile, "w") as f:
               for line in lines:
                  item = line.strip("\n")
                  if item != closetOrderItem:
                     f.write(line)
 
   def arrangeClosetItemsForSharing(self):
      self.readInClosetOrder()      
      self.updateOrderFile() 
      if self.hasUpdate:
         self.closetOrderDict = {}
         self.readInClosetOrder()
         print("Updated order.txt")
      if self.debug: 
         print(self.closetOrderDict)
      self.orderedShareButtons = [None] * self.closetSize
      for itemName, item in zip(self.itemNames, self.shareButtons):
         self.orderedShareButtons[self.closetOrderDict[itemName]] = item
      count = 0
      for button in self.orderedShareButtons:
         if button == None:
            print(str(count) + " is None. Something went wrong. Exiting")
            self.quit()
            sys.exit()
         count += 1

   def getAndPrintItemNames(self):
      for count, itemName in enumerate(self.itemNameElements):
         itemNameTxt = itemName.text
         self.itemNames.append(itemNameTxt)
         if self.debug:
            print(str(count) + ": "  + itemNameTxt)

   def getItemNames(self, shareAFew = False):
      self.itemNameElements = self.driver.find_elements_by_xpath(self.itemNameXPath)
      if shareAFew:
         closetSize = len(self.itemNameElements)
         if closetSize > self.numItemsToShareFromOtherClosets:
            for i in range(0, closetSize - self.numItemsToShareFromOtherClosets):
               self.itemNameElements.pop()
      self.getAndPrintItemNames()

   def getShareButtons(self, shareAFew = False):      
      self.shareButtons = self.driver.find_elements_by_xpath(self.firstShareXPath)      
      self.closetSize = len(self.shareButtons)
      if shareAFew and self.closetSize > self.numItemsToShareFromOtherClosets:
         for i in range(0, self.closetSize - self.numItemsToShareFromOtherClosets):
            self.shareButtons.pop()
  
   def clickAButton(self, button):
      try:
         self.driver.execute_script("arguments[0].click();", button)
      except Exception as e:
         print("clicking button failed: " + str(e))
   
   def waitTillModalPopsUp(self, xpath):
      modalPopsUp = False
      while not modalPopsUp:
         modalPopsUp = self.waitForAnElementByXPath(xpath, "modal")

   def clickFirstShareButton(self, shareButton):
      self.clickAButton(shareButton)
      if self.debug:
         print("      Clicked 1st share")
      self.waitTillModalPopsUp(self.shareModalTitleXPath)
      if self.slowMode:
         time.sleep(self.getRandomSec())
   
   def waitTillShareModalIsGone(self, shareModal):
      try:
         shareModalIsGone = WebDriverWait(self.driver, self.timeOutSecs).until(EC.invisibility_of_element_located(shareModal)) #wait until the share modal is gone
      except TimeoutException as e:
         print("Timed out while waiting for share modal to disappear..clicking second share again")
         print(e)
         return False
      return True
   
   def closeCaptchaPopUp(self):
      try:
         captchaXButton = self.driver.find_element_by_xpath(self.captchaXButtonXPath)
         self.clickAButton(captchaXButton)
      except Exception as e:
         print("      Exception occured while closing captcha pop up, exiting: " + str(e))

   def retrySharingAnItem(self, firstShareButton):
      self.closeCaptchaPopUp()
      self.clickFirstShareButton(firstShareButton)
      shareToFollowers = self.waitTillClickable("xpath", self.secondShareXPath)
      shared = False
      while not shared:
         self.clickAButton(shareToFollowers)
         if self.debug:
            print("     Retrying sharing an item before captcha")
         if self.waitTillShareModalIsGone(shareToFollowers):
            shared = True
   
   def checkForCaptcha(self, modalTitleXPath):
      modalTitle = ""
      try:
         modalTitle = self.driver.find_element_by_xpath(modalTitleXPath).text
      except Exception as e:
         if self.debug:
            print("      No modal, no captcha")
      if modalTitle:
         if modalTitle == "Share this listing":
            if self.debug:
               print("      No captcha")
         elif modalTitle == "Oh the HUMAN-ity. Check the box if you're a real person.":
            print("      Captcha detected, please solve")
            return True
         else:
            print("      Modal title: " + modalTitle)      
      return False
   
   def checkAndWaitForCaptchaSolve(self, firstShareButton):
      if self.checkForCaptcha(self.captchaModalTitleXPath):
         self.driver.switch_to.window(self.driver.current_window_handle) 
         pdb.set_trace()
         self.driver.minimize_window()
         self.retrySharingAnItem(firstShareButton)
         self.checkAndWaitForCaptchaSolve(firstShareButton)

   def clickSecondShareButton(self, firstShareButton):
      shareToFollowers = self.waitTillClickable("xpath", self.secondShareXPath)
      if not shareToFollowers:
         print("time out exception occured clicking second share button")
         pdb.set_trace()
      shared = False
      while not shared:
         self.clickAButton(shareToFollowers)
         if self.debug:
            print("      Clicked 2nd share")
         if self.waitTillShareModalIsGone(shareToFollowers):
            shared = True

      if self.checkCaptcha: 
         self.checkAndWaitForCaptchaSolve(firstShareButton)
      
      self.waitTillClickable("xpath", self.socialBarXPath)
      
      if self.slowMode:
         time.sleep(self.getRandomSec())
   
   def shareCloset(self, orderList, shareButtonsList):
      for itemName, shareButton in zip(reversed(orderList), reversed(shareButtonsList)):
         if self.debug:
            print("   Sharing " + itemName)
         self.clickFirstShareButton(shareButton) 
         self.clickSecondShareButton(shareButton)
   
   def shareAllItems(self, sharingMine = True): # default is sharing all items from own closet
      self.driver.minimize_window()
      if self.slowMode:
         time.sleep(3)    
      now = datetime.now()
      print("Current date and time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
      if sharingMine:
         if self.orderTextFile:
            print("Sharing to order given by order.txt...")
            self.shareCloset(self.closetOrder, self.orderedShareButtons)
         else:
            print("No ordered text given, sharing in current closet order...")
            self.shareCloset(self.itemNames, self.shareButtons)
      else:
         self.shareCloset(self.itemNames, self.shareButtons)

   def getClosetSizeFromStatsPage(self):
      self.driver.get(self.closetStatsUrl)
      availableStats = None
      while not availableStats:
         availableStats = self.waitForAnElementByXPath(self.statsXPath, "available stats").text
      if self.debug:
         print("Available items from stats = " + str(availableStats))
      return int(availableStats)

   def share(self):
      if self.toShareClosetsFromFile:
         self.shareClosetsFromFile()
      else:
         while(1):
            closetSizeFromStatsPage = self.getClosetSizeFromStatsPage()
            self.driver.get(self.availableUrl)
            scroll = True
            numTimesToScroll = 4
            count = 0
            while scroll:
               self.scrollCloset()
               self.getShareButtons()
               print("Available items in the closet: {}".format(self.closetSize))
               if closetSizeFromStatsPage <= self.closetSize:
                  scroll = False
               else:
                  # check closet size from the stats page after trying scrolling 4 times and the size still don't add up
                  # this is for the case where something gets sold between the time it last checked the stats page and going to the closet
                  if count >= numTimesToScroll: 
                     closetSizeFromStatsPage = self.getClosetSizeFromStatsPage()
                     if closetSizeFromStatsPage <= self.closetSize:
                        print("Closet size matches now")
                        scroll = False
                     else:
                        print("Closet size doesn't match on stats page of " + str(closetSizeFromStatsPage) + ". Scrolling from begining...")
                        self.driver.get(self.availableUrl)
                        scroll = True
                  else:
                     print("Closet size doesn't match on stats page of " + str(closetSizeFromStatsPage) + ". Scroll more...")
                     scroll = True
               count += 1
            self.scrollToTop()  
            self.getItemNames()
            if self.orderTextFile:
               print("Keeping closet order based on " + self.orderTextFile)
               self.arrangeClosetItemsForSharing() 
            self.shareAllItems()
            self.clearsAndResets()

            if self.shareBack:
               self.shareBackAndFollowOtherClosets()
            print("Shared closet, will share again in " + str(timeToWait/60) + " mins at " + str(datetime.now() + timedelta(seconds=timeToWait))) 
            time.sleep(self.timeToWait)
   
   def shareAnotherCloset(self, closetName, sharingAFew = False): #default is sharing all items from another closet
      sharingMine = False
      closetUrl = self.getClosetAvailableUrl(closetName)
      self.driver.get(closetUrl)
      if not sharingAFew:
         self.scrollCloset()
      self.getShareButtons(sharingAFew)
      if not sharingAFew:
         self.scrollToTop() 
      self.getItemNames(sharingAFew)
      print("Available items in the closet: " + str(len(self.shareButtons)))
      self.shareAllItems(sharingMine)
      self.clearsAndResets(sharingMine)
   
   def scrollPageANumTimes(self):
      for n in range(0, self.numTimesToScroll):
         self.driver.switch_to.window(self.driver.current_window_handle)
         self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")   
         time.sleep(self.scrollWaitTime)
  
   # when given no param, it follows the closet on the page that's currently loaded 
   def followACloset(self, closetName=""):
      if closetName:
         closetUrl = self.getClosetAvailableUrl(closetName)
         self.driver.get(closetUrl)
      followButton = self.waitTillClickable("xpath", self.followButtonXPath, 1)
      if followButton:
         print("following this closet")
         self.clickAButton(followButton)
      else:
         print("already following")
 
   def shareBackAndFollowOtherClosets(self):
      print("sharing back")
      sharingAFew = True
      self.driver.get(self.shareNewsUrl)
      self.scrollPageANumTimes()
      self.waitForAnElementByXPath(self.closetNameXPath, "closetNameXPath")
      closetNames = self.driver.find_elements_by_xpath(self.closetNameXPath)
      closetNamesSet = set()
      for n in closetNames:
         closetNamesSet.add(n.text)
      print(closetNamesSet)
      
      for closet in closetNamesSet:
         if closet not in self.closetSharedBack:
            print("sharing " + closet)
            self.shareAnotherCloset(closet, sharingAFew)
            self.closetSharedBack.append(closet)
            self.followACloset()
   
   def getClosetsToShareFromFile(self):
      self.closetsToShare = []
      with open(self.closetsToShareFile, "r") as f:
         lines = f.readlines()
         for line in lines:
            closetName = line.strip()
            if closetName:
               self.closetsToShare.append(closetName)
      numClosets = len(self.closetsToShare)
      if numClosets == 0:
         print("No closets given in the file")
      return numClosets

   def shareClosetsFromFile(self):
      if self.getClosetsToShareFromFile():
         for closet in self.closetsToShare:
            print("Sharing " + closet)
            closetAvailableUrl = self.getClosetAvailableUrl(closet)
            self.shareAnotherCloset(closet) 
 
def checkBooleanInput(val):
   if val in ('y', 'yes', 't', 'true', '1'):
      return True, True
   elif val in ('n', 'no', 'f', 'false', '0'):
      return True, False
   else:
      return False, False

if __name__ == "__main__":
   totNumArgs = len(sys.argv)
   timeToWait = 3600 # default wait time is 1 hr
   debug = False
   slowMode = False
   maintainOrderBasedOnOrderFile = False
   checkCaptcha = True
   toShareClosetsFromFile = False
   shareBack = False
   if totNumArgs >= 2:
      goodFormat, checkCaptcha = checkBooleanInput(sys.argv[1].lower())
      if not goodFormat:
         print("1st parameter " + sys.argv[1] + " needs to be a boolean value Y|N for whether or not to check for captcha")
         print("Usage: python posh_nursery.py {Y|N} {Y|N} {integerNumberOfSeconds} {Y|N} {Y|N}")
         sys.exit()
   if totNumArgs >= 3:
      goodFormat, toShareClosetsFromFile = checkBooleanInput(sys.argv[2].lower())
      if not goodFormat:
         print("2nd parameter " + sys.argv[2] + " needs to be a boolean value Y|N for whether or not to share closets in closetsToShare.txt")
         print("Usage: python posh_nursery.py {Y|N} {Y|N} {integerNumberOfSeconds} {Y|N} {Y|N}")
         sys.exit()
   if totNumArgs >= 4:
      try:
         timeToWait = int(sys.argv[3])
      except ValueError as e:
         print("3rd parameter " + sys.argv[3] +" needs to be an integer number for the number of seconds to wait after one round of sharing")
         print("Usage: python posh_nursery.py {Y|N} {Y|N} {integerNumberOfSeconds} {Y|N} {Y|N}")
         sys.exit()
   if totNumArgs >= 5:
      goodFormat, maintainOrderBasedOnOrderFile = checkBooleanInput(sys.argv[4].lower())
      if not goodFormat:
         print("4th parameter " + sys.argv[4] + " needs to be a boolean value Y|N for whether or not to maintain closet order based on order file")
         print("Usage: python posh_nursery.py {Y|N} {Y|N} {integerNumberOfSeconds} {Y|N} {Y|N}")
         sys.exit()
   if totNumArgs >= 6:
      goodFormat, shareBack = checkBooleanInput(sys.argv[5].lower())
      if not goodFormat:
         print("5th parameter " + sys.argv[5] + " needs to be a boolean value Y|N for whether or not to share back")
         print("Usage: python posh_nursery.py {Y|N} {Y|N} {integerNumberOfSeconds} {Y|N} {Y|N}")
         sys.exit()   
   if totNumArgs >= 7:
      print("Too many parameters. This program only takes 5 optional parameters")
      print("Usage: python posh_nursery.py {Y|N} {Y|N} {integerNumberOfSeconds} {Y|N} {Y|N}")
      sys.exit()
   
   username = config.username
   password = config.password
   posh_nursery = Posh_Nursery(username, password, slowMode, debug, checkCaptcha, toShareClosetsFromFile, timeToWait, maintainOrderBasedOnOrderFile, shareBack)
   print("Logging in Poshmark as " + username + "...")
   posh_nursery.login()
   posh_nursery.share()
   posh_nursery.quit()   
