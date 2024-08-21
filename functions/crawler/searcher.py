from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from functions.database.utils import save_to_database, update_status
import os, base64, random, time, logging, traceback

PAUSE_SEC = random.randrange(1,3)
def ERROR_CONTROL(driver, originalurl, e, isgit=False, isexit=False):
  if isexit:
    print("[!] NO SUCH ELEMENT EXCEPTION in [{0}]: Bot detect alert".format(originalurl))
    driver.quit()

    update_status("g", originalurl, "notstarted", isgit)
    os._exit(1)
  else:
    print("[!] ERROR in [{0}]:".format(originalurl), e)
    logging.error(traceback.format_exc())
  
  return 0

############### SETUP ###############

def cut_string_including_substring(main_string, substring):
  index = main_string.find(substring)
  if index != -1:
    return main_string[index:]
  else:
    return main_string

def decode_base64(s):
  result = base64.b64decode(s.replace("\\_", "/") + '====').decode('utf-8')
  return result

def driver_setup(executor_link):
  ua_val = random.randint(0,6)
  ua_list = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
             "Mozilla/5.0 (X11; CrOS x86_64 10066.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
             "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36 OPR/65.0.3467.48",
             "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36 OPR/65.0.3467.48",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:70.0) Gecko/20100101 Firefox/70.0",
             "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:70.0) Gecko/20100101 Firefox/70.0"]
  options = webdriver.ChromeOptions()
  
  options.add_argument('headless')
  options.add_argument('incognito')

  options.add_argument('window-size=1920x1080')
  options.add_argument('user-agent={0}'.format(ua_list[ua_val]))
  options.add_argument("--disable-blink-features=AutomationControlled")

  driver = webdriver.Remote(
    command_executor = executor_link,
    options = options)
  
  return driver

def scrolltoend_chrome(driver):
  last_height = driver.execute_script("return document.body.scrollHeight")

  while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(PAUSE_SEC)
    new_height = driver.execute_script("return document.body.scrollHeight")

    if new_height == last_height:
      try:
        time.sleep(PAUSE_SEC)
        driver.find_element(By.CLASS_NAME, "RVQdVd").click()
      except:
        break
    last_height = new_height
  return 0

def scrolltoend_bing(driver):
  last_height = driver.execute_script("return document.body.scrollHeight")

  while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(PAUSE_SEC)
    new_height = driver.execute_script("return document.body.scrollHeight")

    if new_height == last_height:
      break
    last_height = new_height
  return 0

############### SEARCHER ###############

def google_search(originalurl, target="default"):
  logging.basicConfig(filename='C:\\Users\\itf\\Documents\\selenium-search-api\\logs\\crawler_error.log', level=logging.WARNING, encoding="utf-8")
  driver = driver_setup('http://127.0.0.1:4444/wd/hub')
  isgit = False

  if target == "github":
    isgit = True
    searchkey = "site:github.com" + originalurl
  else:
    searchkey = "site:" + originalurl

  update_status('g', originalurl, 'processing', isgit)

  driver.get("https://www.google.com/")
  time.sleep(PAUSE_SEC * 3)

  # 캡챠 발생 시 탈출
  try: searchfield = driver.find_element(By.XPATH, '//*[@id="APjFqb"]')
  except NoSuchElementException as e: ERROR_CONTROL(driver, originalurl, e, isgit, isexit=True)
  except Exception as e: ERROR_CONTROL(driver, originalurl, e)
  
  # 검색어 전송 후 검색 진행
  searchfield.send_keys(searchkey)
  time.sleep(PAUSE_SEC * 3)
  searchfield.send_keys(Keys.ENTER)
  
  scrolltoend_chrome(driver)
  time.sleep(PAUSE_SEC * 3)

  while True:
    # 캡챠 발생 시 탈출
    try: resultfield = driver.find_element(By.ID, 'search')
    except NoSuchElementException as e: ERROR_CONTROL(driver, originalurl, e, isgit, isexit=True)
    except Exception as e: ERROR_CONTROL(driver, originalurl, e)
    
    # search 안에서 검색
    try:
      res_title = resultfield.find_elements(By.TAG_NAME, 'h3')
      res_content = resultfield.find_elements(By.CLASS_NAME, 'VwiC3b.yXK7lf.lVm3ye.r025kc.hJNv6b.Hdw6tb')

      res_link = []
      for titlefield in res_title:
        linkpath = titlefield.find_element(By.XPATH, '..')
        res_link.append(linkpath.get_attribute('href'))

      idx = len(res_title)
      for i in range(idx):
        res_title_alt = res_title[i].text
        res_title_alt = res_title_alt.replace("'", "\\'")

        if i < len(res_content):
          res_content_alt = res_content[i].text
          res_content_alt = res_content_alt.replace("'", "\\'")
          res_content_alt = res_content_alt.replace('"', '\\"')
          res_content_alt = res_content_alt.replace("%", "\\%")
        else:
          res_content_alt = ""
        
        tmp = res_link[i].split('/')
        url = tmp[2]
        save_to_database("G", url, res_title_alt, res_link[i], res_content_alt, target)
    except Exception as e: ERROR_CONTROL(driver, originalurl, e)

    # botstuff 안에서 검색
    resultfield = driver.find_element(By.ID, 'botstuff')
    try:
      res_title = resultfield.find_elements(By.TAG_NAME, 'h3')
      res_content = resultfield.find_elements(By.CLASS_NAME, 'VwiC3b.yXK7lf.lVm3ye.r025kc.hJNv6b.Hdw6tb')

      res_link = []
      for titlefield in res_title:
        linkpath = titlefield.find_element(By.XPATH, '..')
        res_link.append(linkpath.get_attribute('href'))

      idx = len(res_title)-2 # <h3 aria_hidden="true">, <h3>다시 시도</h3>
      for i in range(idx):
        res_title_alt = res_title[i].text
        res_title_alt = res_title_alt.replace("'", "\\'")

        if i < len(res_content):
          res_content_alt = res_content[i].text
          res_content_alt = res_content_alt.replace("'", "\\'")
          res_content_alt = res_content_alt.replace('"', '\\"')
          res_content_alt = res_content_alt.replace("%", "\\%")
        else:
          res_content_alt = ""

        tmp = res_link[i].split('/')
        url = tmp[2]
        save_to_database("G", url, res_title_alt, res_link[i], res_content_alt, target)
    except Exception as e: ERROR_CONTROL(driver, originalurl, e)

    # 다음 페이지가 있으면 클릭
    time.sleep(PAUSE_SEC)
    try: driver.find_element(By.ID, 'pnnext').click()
    except: break
  driver.quit()

  update_status('g', originalurl, 'finished', isgit)
  print("done!")

def bing_search(originalurl, target="default"):
  logging.basicConfig(filename='C:\\Users\\itf\\Documents\\selenium-search-api\\logs\\crawler_error.log', level=logging.WARNING, encoding="utf-8")
  driver = driver_setup('http://127.0.0.1:4444/wd/hub')
  isgit = False

  searchkey = ''
  nextpage_link = ''

  if target == "github":
    isgit = True
    searchkey = "site:github.com" + originalurl
  else:
    searchkey = "site:" + originalurl
    
  update_status('b', originalurl, 'processing', isgit)

  driver.get("https://www.bing.com/search")

  time.sleep(PAUSE_SEC)
  searchfield = driver.find_element(By.XPATH, '//*[@id="sb_form_q"]')

  searchfield.send_keys(searchkey)
  time.sleep(PAUSE_SEC)
  searchfield.send_keys(Keys.ENTER)
  
  while True:
    scrolltoend_bing(driver)
    time.sleep(PAUSE_SEC)

    scrolltoend_bing(driver)    
    resultfield = driver.find_element(By.ID, 'b_results')
    try:
      res_content = resultfield.find_elements(By.TAG_NAME, 'p')
      titlefield = resultfield.find_elements(By.XPATH, '//h2//a')
      res_title = []
      res_link = []
      
      for title in titlefield:
        res_title.append(title.text)
        res_link.append(title.get_attribute('href'))

      idx = len(res_title)
      for i in range(idx):
        res_title_alt = res_title[i]
        res_title_alt = res_title_alt.replace("'", "\\'")

        if i < len(res_content):
          res_content_alt = res_content[i].text
          res_content_alt = res_content_alt.replace("'", "\\'")
          res_content_alt = res_content_alt.replace('"', '\\"')
          res_content_alt = res_content_alt.replace("%", "\\%")

          index = res_content_alt.find("일 · ")
          if index > 0:
            index = index + 3
            res_content_alt = res_content_alt[index:]
        else:
          res_content_alt = ""

        res_link_alt = res_link[i]
        res_link_alt = res_link_alt.replace("'", "\\'")
        res_link_alt = res_link_alt.replace('"', '\\"')
        res_link_alt = res_link_alt.replace("%", "\\%")
        res_link_alt = res_link_alt.replace("_", "\\_")

        if "aHR0c" in res_link_alt:
          tmp = cut_string_including_substring(res_link_alt, "aHR0c")
          tmp_b64 = tmp.split('&')[0]
          try: res_link_alt = decode_base64(tmp_b64)
          except Exception as e: ERROR_CONTROL(driver, tmp_b64, e, isexit=True)

        tmp = res_link_alt.split('/')
        if target == "github": url = originalurl
        else: url = tmp[2]

        try: save_to_database("B", url, res_title_alt, res_link_alt, res_content_alt[1:], target)
        except Exception as e: ERROR_CONTROL(driver, res_link_alt, e)
    except Exception as e: ERROR_CONTROL(driver, originalurl, e)

    time.sleep(PAUSE_SEC)
    try:
      nextpage = driver.find_element(By.CLASS_NAME, 'sw_next').find_element(By.XPATH, '..')
      tmp_link = nextpage.get_attribute('href')

      if nextpage_link == tmp_link:
        ERROR_CONTROL(driver, originalurl, "ERROR", isexit=True)
      else:
        nextpage_link = tmp_link
        driver.get(nextpage_link)

    except: break

  driver.quit()

  update_status('b', originalurl, 'finished', isgit)
  print("done!")