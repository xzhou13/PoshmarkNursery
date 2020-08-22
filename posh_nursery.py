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
   def __init__(self, username, password, slowMode = False, maintainOrder = False, checkCaptcha = True, debug = False):
      self.username = username
      self.password = password
      self.timeOutSecs = 20
      self.chrome_options = Options()
      #self.chrome_options.add_argument("--headless")
      #self.chrome_options.add_argument("--window-size=1920x1080")
      self.driver = webdriver.Chrome(options = self.chrome_options)
      self.shareButtons = []
      self.orderedShareButtons = []
      self.closetSize = 0
      self.itemNameElements = []
      self.itemNames = []
      self.loginUrl = "https://poshmark.com/login"
      self.closetUrl = "https://poshmark.com/closet"
      self.loginID = "login_form_username_email"
      self.loginXPath = "//input[@name='userHandle']"
      self.passwordID = "login_form_password"
      self.passwordXPath = "//input[@name='password']"
      #self.socialBarXPath = "social-action-bar tile__social-actions"
      self.socialBarXPath = "//div[@class='social-info social-actions d-fl ai-c jc-c']"
      #self.socialXPath = "//*[@class='d--fl ai--c social-action-bar__action social-action-bar__share']"
      self.socialXPath = "//*[@class='share']"
      #self.itemNameXPath = "//*[@class='tile__title tc--b']"
      self.itemNameXPath = "//*[@class='title']"
      #self.cssShareClass = "div.share-wrapper__icon-container"
      self.cssShareClass = "div.icon-con"
      self.shareXPath = "//i[@class='icon pm-logo-white']"
      #self.modalTitleXPath = "//h5[@class='modal__title']"
      self.captchaModalTitleXPath = "//*[@id='captcha-popup']/div[1]/h5"
      self.shareModalTitleXPath = "//*[@id='share-popup']/div[1]/h5"
      #self.captchaXButtonXPath = "//button[@class='btn btn--close modal__close-btn simple-modal-close']"
      self.captchaXButtonXPath = "//*[@id='captcha-popup']/div[1]/button"
      if maintainOrder: 
         self.orderTextFile = "order.txt"
      else:
         self.orderTextFile = ""
      self.hasUpdate = False
      self.closetOrder = []
      self.closetOrderDict = {}
      self.checkCaptcha = checkCaptcha
      self.debug = debug
      self.slowMode = slowMode
      self.availableUrl = self.getClosetAvailableUrl(self.username)
      self.driver.minimize_window()
   
   def quit(self):   
      self.driver.quit()
   
   def getRandomSec(self):
      return random.randrange(1, 5, 1)

   def waitTillClickable(self, findByIdOrPath, idOrPath):
      clickableElement = False
      if findByIdOrPath == 'id':
         try:
            clickableElement = WebDriverWait(self.driver, self.timeOutSecs).until(EC.element_to_be_clickable((By.ID, idOrPath)))
         except TimeoutException as e:
            print("Timed out at locating element by " + findByIdOrPath + " at " + str(idOrPath) + ": " + str(e))
            return False
      else:
         try:
            clickableElement = WebDriverWait(self.driver, self.timeOutSecs).until(EC.element_to_be_clickable((By.XPATH, idOrPath)))
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

   def scrollCloset(self, waitTime = 2):
      waitTime = waitTime
      lastHeight = self.driver.execute_script("return document.body.scrollHeight")
      scrollMore = True
      print("Scrolling")
      while scrollMore:
         self.driver.switch_to.window(self.driver.current_window_handle) 
         self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
         time.sleep(waitTime)
         newHeight = self.driver.execute_script("return document.body.scrollHeight")
         if newHeight == lastHeight:
            scrollMore = False
         lastHeight = newHeight
         
   def readInClosetOrder(self):
      self.closetOrder = [line.rstrip('\n') for line in open(self.orderTextFile)]
      for n,sortedItem in enumerate(self.closetOrder):
         self.closetOrderDict[sortedItem] = n
      if self.debug:
         print("Initial closetOrderDict")
         print(self.closetOrderDict)

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
         if self.debug:
            print(itemName)
            print(self.closetOrderDict[itemName])
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

   def getItemNames(self):
      self.itemNameElements = self.driver.find_elements_by_xpath(self.itemNameXPath)
      self.getAndPrintItemNames()
   
   def getShareButtons(self):      
      self.shareButtons = self.driver.find_elements_by_xpath(self.socialXPath)      
      self.closetSize = len(self.shareButtons)
  
   def clickAButton(self, button):
      try:
         self.driver.execute_script("arguments[0].click();", button)
      except Exception as e:
         print("clicking button failed: " + str(e))
         #pdb.set_trace()
   
   def waitTillModalPopsUp(self, xpath):
      modalPopsUp = False
      while not modalPopsUp:
         modalPopsUp = self.waitForAnElementByXPath(xpath, "modal")

   def clickFirstShareButton(self, shareButton):
      self.clickAButton(shareButton)
      if self.debug:
         print("      Clicked 1st share")
      self.waitTillModalPopsUp(self.shareModalTitleXPath)
      self.waitTillClickable("xpath", self.shareXPath)
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
      shareToFollowers = self.waitTillClickable("xpath", self.shareXPath)
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
      shareToFollowers = self.waitTillClickable("xpath", self.shareXPath)
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
   
   def shareAllItems(self):
      self.driver.minimize_window()
      if self.slowMode:
         time.sleep(3)    
      now = datetime.now()
      print("Current date and time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
      if self.orderTextFile:
         print("Sharing now...")
         self.shareCloset(self.closetOrder, self.orderedShareButtons)
      else:
         print("No ordered text given, sharing in current closet order...")
         self.shareCloset(self.itemNames, self.shareButtons)
   
   def shareMyCloset(self):
      self.driver.get(self.availableUrl)
      self.scrollCloset()
      self.getShareButtons()
      print("Available items in the closet: {}".format(self.closetSize))
      self.getItemNames()
      if self.orderTextFile:
         print("Keeping closet order based on " + self.orderTextFile)
         self.arrangeClosetItemsForSharing()
      self.shareAllItems()

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
   if totNumArgs >= 2:
      goodFormat, checkCaptcha = checkBooleanInput(sys.argv[1].lower())
      if not goodFormat:
         print("1st parameter " + sys.argv[3] + " needs to be a boolean value Y|N for whether or not to check for captcha")
         print("Usage: python posh_nursery.py {Y|N} {integerNumberOfSeconds} {Y|N}")
         sys.exit()
   if totNumArgs >= 3:
      try:
         timeToWait = int(sys.argv[2])
      except ValueError as e:
         print("2nd parameter needs to be an integer number for the number of seconds to wait after one round of sharing")
         print("Usage: python posh_nursery.py {Y|N} {integerNumberOfSeconds} {Y|N}")
         sys.exit()
   if totNumArgs >= 4:
      goodFormat, maintainOrderBasedOnOrderFile = checkBooleanInput(sys.argv[3].lower())
      if not goodFormat:
         print("3rd parameter " + sys.argv[3] + " needs to be a boolean value Y|N for whether or not to maintain closet order based on order file")
         print("Usage: python posh_nursery.py {Y|N} {integerNumberOfSeconds} {Y|N}")
         sys.exit()
   if totNumArgs >= 5:
      print("Too many parameters. This program only takes 3 optional parameters")
      print("Usage: python posh_nursery.py {Y|N} {integerNumberOfSeconds} {Y|N}")
      sys.exit()
   
   username = config.username
   password = config.password
   while(1):
      posh_nursery = Posh_Nursery(username, password, slowMode, maintainOrderBasedOnOrderFile, checkCaptcha, debug)
      print("Logging in Poshmark as " + username + "...")
      posh_nursery.login()
      posh_nursery.shareMyCloset()
      posh_nursery.quit()   
      print("Shared closet, will share again in " + str(timeToWait/60) + " mins at " + str(datetime.now() + timedelta(seconds=timeToWait))) 
      time.sleep(timeToWait)
