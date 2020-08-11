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
   def __init__(self, username, password, slowMode = False, maintainOrder = False, debug = False):
      self.username = username
      self.password = password
      self.timeOutSecs = 20
      self.chrome_options = Options()
      #self.chrome_options.add_argument("--headless")
      self.chrome_options.add_argument("--window-size=1920x1080")
      self.driver = webdriver.Chrome(options = self.chrome_options)
      self.shareButtons = []
      self.orderedShareButtons = []
      self.closetSize = 0
      self.itemNameElements = []
      self.itemNames = []
      self.loginUrl = "https://poshmark.com/login"
      self.closetUrl = "https://poshmark.com/closet"
      self.closetStatsUrl = "https://poshmark.com/users/self/closet_stats"
      self.statsXPath = "//div[@class='stat-count']"
      self.loginID = "login_form_username_email"
      self.passwordID = "login_form_password"
      self.socialXPath = "//*[@class='d--fl ai--c social-action-bar__action social-action-bar__share']"
      #self.socialXPath = "//*[@class='share']"
      self.itemNameXPath = "//*[@class='tile__title tc--b']"
      #self.itemNameXPath = "//*[@class='title']"
      self.cssShareClass = "div.share-wrapper__icon-container"
      #self.cssShareClass = "div.icon-con"
      self.shareXPath = "//i[@class='icon pm-logo-white']"
      self.modalTitleXPath = "//h5[@class='modal__title']"
      self.captchaXButtonXPath = "//button[@class='btn btn--close modal__close-btn simple-modal-close']"
      if maintainOrder: 
         self.orderTextFile = "order.txt"
      else:
         self.orderTextFile = ""
      self.hasUpdate = False
      self.closetOrder = []
      self.closetOrderDict = {}
      self.debug = debug
      self.slowMode = slowMode
      self.availableUrl = self.getClosetAvailableUrl(self.username)
   
   def getRandomSec(self):
      return random.randrange(1, 5, 1)

   def login(self): 
      self.driver.get(self.loginUrl)
      
      if self.slowMode:
         time.sleep(5)
       
      timedOut = False
      try:
         userNameElement = WebDriverWait(self.driver, self.timeOutSecs).until(EC.element_to_be_clickable((By.ID, self.loginID)))
      except TimeoutException as e:
         print("Time out at locating username with ID: " + str(e))
         try:
            userNameElement = WebDriverWait(self.driver, self.timeOutSecs).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='userHandle']")))
         except TimeoutException as e:
            timedOut = True
            print("Timed out again with username xpath")
            print("Please manually enter username, then type 'continue'")
            pdb.set_trace()
      
      if not timedOut:
         for char in self.username:
            userNameElement.send_keys(char)
            time.sleep(random.random())
       
      if self.slowMode:
         time.sleep(self.getRandomSec())

      timedOut = False
      try:
         passwordElement = WebDriverWait(self.driver, self.timeOutSecs).until(EC.element_to_be_clickable((By.ID, self.passwordID)))
      except TimeoutException as e:
         print("Timed out at locating password with ID: " + str(e))
         try:
            passwordElement = WebDriverWait(self.driver, self.timeOutSecs).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='password']")))
         except TimeoutException as e:
            timedOut = True
            print("Timed out again with password xpath")
            print("Please manually enter password, then type 'continue'")
      
      if not timedOut:
         for char in self.password:
            passwordElement.send_keys(char)
            time.sleep(random.random())
      
      if self.slowMode:
         time.sleep(self.getRandomSec())

      try:
         passwordElement.submit()
      except:
         print("Exception occured while trying to log in, exiting.")
         self.quit()
         self.exit()
      
      if self.debug:  
         print(self.driver.title)
      
      try:
         WebDriverWait(self.driver, self.timeOutSecs).until(EC.title_contains("Feed"))
      except Exception as e:
         print("ERROR: logging error{}".format(e))
         print("Please solve captcha and then type 'continue'")
         pdb.set_trace()
      
      if self.debug:  
         print(self.driver.title)
      
      print("Logged into poshmark")

   def getClosetAvailableUrl(self, username):   
      availableUrl = "{}/{}{}".format(self.closetUrl, username, "?availability=available")
      return availableUrl 
  
   def scrollCloset(self, waitTime = 10):
      waitTime = waitTime
      lastHeight = self.driver.execute_script("return document.body.scrollHeight")
      scrollMore = True
      while scrollMore:
         print("Scrolling")
         self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

         newHeight = self.driver.execute_script("return document.body.scrollHeight")
         if newHeight == lastHeight:
            scrollMore = False
         lastHeight = newHeight

         time.sleep(waitTime)
   
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
            print(str(count) + " is None.")
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
  
   def checkForCaptcha(self): 
      modalTitle = ""
      try:
         modalTitle = self.driver.find_element_by_xpath(self.modalTitleXPath).text
      except Exception as e:
         if self.debug:
            print("      No modal, no captcha")
      if modalTitle:
         if modalTitle == "Share this listing":
            if self.debug:
               print("      No captcha")
         elif modalTitle == "Oh the HUMAN-ity. Check the box if you're a real person.":
            print("      Captcha detected, please solve")
            pdb.set_trace()
            try:
               captchaXButton = self.driver.find_element_by_xpath(self.captchaXButtonXPath)
               self.driver.execute_script("arguments[0].click();", captchaXButton)
            except Exception as e:
               print("      Exception occured while closing captcha pop up: " + str(e))
               pdb.set_trace()
         else:
            print("      Modal title: " + modalTitle)

   def clickFirstShareButton(self, shareButton):
      self.driver.execute_script("arguments[0].click();", shareButton)
      if self.debug:
         print("      Clicked 1st share")
      # wait until modal pops up
      WebDriverWait(self.driver, self.timeOutSecs).until(EC.presence_of_element_located((By.XPATH, self.modalTitleXPath)))
      self.checkForCaptcha()
      if self.slowMode:
         time.sleep(self.getRandomSec())
   
   def clickSecondShareButton(self):
      shareToFollowers = WebDriverWait(self.driver, self.timeOutSecs).until(EC.element_to_be_clickable((By.XPATH, self.shareXPath)))
      self.driver.execute_script("arguments[0].click();", shareToFollowers)
      if self.debug:
         print("      Clicked 2nd share")
      
      shareModalIsGone = False
      while not shareModalIsGone:
         try:
            shareModalIsGone = WebDriverWait(self.driver, self.timeOutSecs).until(EC.invisibility_of_element_located(shareToFollowers)) #wait until the share modal is gone
         except TimeoutException as e:
            print("Timed out while waiting for share pop up window to disappear..waiting again")
            print(e)

      self.checkForCaptcha()
      WebDriverWait(self.driver, self.timeOutSecs).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='social-action-bar tile__social-actions']"))) #wait until social button is clickable again
      
      if self.slowMode:
         time.sleep(self.getRandomSec())
   
   def shareCloset(self, orderList, shareButtonsList):
      for itemName, shareButton in zip(reversed(orderList), reversed(shareButtonsList)):
         if self.debug:
            print("   Sharing " + itemName)
         self.clickFirstShareButton(shareButton) 
         self.clickSecondShareButton()
   
   def shareAllItems(self):
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
   
   def getClosetSizeFromStatsPage(self):
      self.driver.get(self.closetStatsUrl)
      availableStats = None
      while not availableStats:
         try:
            availableStats = WebDriverWait(self.driver, self.timeOutSecs).until(EC.presence_of_element_located((By.XPATH, self.statsXPath))).text
         except TimeoutException as e:
            print("Timed out waiting for availabe stats to load, trying again")
      if self.debug:
         print("Available items from stats = " + str(availableStats))
      
      return int(availableStats)
      
       
   def shareMyCloset(self):
      
      closetSizeFromStatsPage = self.getClosetSizeFromStatsPage()
      
      self.driver.get(self.availableUrl)
      
      scroll = True
      while scroll:
         self.scrollCloset()
      
         self.getItemNames()

         self.getShareButtons()
      
         print("Available items in the closet: {}".format(self.closetSize))
         if closetSizeFromStatsPage == self.closetSize:
            scroll = False
         else:
            print("Closet size doesn't match on stats page of " + str(closetSizeFromStatsPage) + ". Scroll more...")
            scroll = True
         
      if self.orderTextFile:
         print("Keeping closet order based on " + self.orderTextFile)
         self.arrangeClosetItemsForSharing()
      
      self.shareAllItems()
      

   def quit(self):   
      self.driver.quit()
      
if __name__ == "__main__":
  
   totNumArgs = len(sys.argv)
   if totNumArgs <= 1:
      timeToWait = 3600 # default wait time is 1 hr
      maintainOrderBasedOnOrderFile = False
   
   elif totNumArgs == 3:
      try:
         timeToWait = int(sys.argv[1])
      except ValueError as e:
         print("Usage: python3 posh_nursery.py <integerNumberOfSeconds> <Y/N>")
         sys.exit()
          
      if sys.argv[2].lower() in ('y', 'yes', 't', 'true', '1'):
         maintainOrderBasedOnOrderFile = True
      elif sys.argv[2].lower() in ('n', 'no', 'f', 'false', '0'):
         maintainOrderBasedOnOrderFile = False
      else:
         print(sys.argv[2] + " is not right")
         print("Usage: python3 posh_nursery.py <integerNumberOfSeconds> <Y/N>")
         sys.exit()
   
   else:
      print("Usage: python3 posh_nursery.py <integerNumberOfSeconds> <Y/N>")
   
   debug = False
   slowMode = False
   username = config.username
   password = config.password
   while(1):
      posh_nursery = Posh_Nursery(username, password, slowMode, maintainOrderBasedOnOrderFile, debug)
      
      print("Logging in Poshmark as " + username + "...")
      posh_nursery.login()
      
      posh_nursery.shareMyCloset()
   
      posh_nursery.quit()   
      print("Shared closet, will share again in " + str(timeToWait/60) + " mins at " + str(datetime.now() + timedelta(seconds=timeToWait))) 
      
      time.sleep(timeToWait)


