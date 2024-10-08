from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from functions.database.utils import save_to_database, update_status
import base64, random, time, logging


# =====================================================
# ==                    UTILS                        ==
# =====================================================


PAUSE_SEC = random.randrange(2,5)
logging.basicConfig(filename='C:\\Users\\itf\\Documents\\selenium-search-api\\logs\\crawler_error.log', level=logging.WARNING, encoding="utf-8")

def decode_base64(s):
    result = base64.urlsafe_b64decode(bytes(s + '====', 'UTF-8')).decode('UTF-8')
    return result

def no_escape_sequence(s):
    result = s.translate(str.maketrans({"'": "\\'", '"': '\\"', '\\': '\\\\'}))
    return result


# =====================================================
# ==                    SETUP                        ==
# =====================================================


def driver_setup(executor_link):

    # === User-Agent 설정 ===

    ua_val = random.randint(0,6)
    ua_list = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
               "Mozilla/5.0 (X11; CrOS x86_64 10066.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
               "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36 OPR/65.0.3467.48",
               "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36 OPR/65.0.3467.48",
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:70.0) Gecko/20100101 Firefox/70.0",
               "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:70.0) Gecko/20100101 Firefox/70.0"]
    
    # === 옵션 추가 ===
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    options.add_argument("--window-position=-10000,-10000")
    
    options.add_argument('--user-agent={0}'.format(ua_list[ua_val]))
    options.add_argument('--disable-features=OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction,OptimizationHints')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-search-engine-choice-screen')
    
    # === 드라이버 실행 ===

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


# =====================================================
# ==                 GOOGLE_SEARCH                   ==
# =====================================================


def google_search(original_url, git=False):
    driver = driver_setup('http://127.0.0.1:4444/wd/hub')

    if git: searchkey = "site:github.com " + original_url
    else: searchkey = "site:" + original_url

    driver.get("https://www.google.com/")
    time.sleep(PAUSE_SEC * 3)

    # === 캡챠 발생 시 탈출 ===

    try: searchfield = driver.find_element(By.XPATH, '//*[@id="APjFqb"]')
    except NoSuchElementException: raise ValueError(f"Critical error processing item: {original_url}")
    except Exception: raise ValueError(f"Unknown minor error processing item: {original_url}")
    
    # === 검색어 전송 후 검색 진행 ===
    
    searchfield.send_keys(searchkey)
    time.sleep(PAUSE_SEC * 3)
    searchfield.send_keys(Keys.ENTER)
    
    scrolltoend_chrome(driver)
    time.sleep(PAUSE_SEC * 3)

    while True:
        try: resultfield = driver.find_element(By.ID, 'search')
        except NoSuchElementException: raise ValueError(f"Critical error processing item: {original_url}")
        except Exception: raise ValueError(f"Unknown minor error processing item: {original_url}")

        # === 검색 섹션: search ===
    
        try:
            res_title = resultfield.find_elements(By.TAG_NAME, 'h3')
            res_content = resultfield.find_elements(By.CLASS_NAME, 'VwiC3b.yXK7lf.lVm3ye.r025kc.hJNv6b.Hdw6tb')

            res_link = []
            for titlefield in res_title:
                linkpath = titlefield.find_element(By.XPATH, '..')

                # === 링크에서 특수문자 삭제 ===

                res_link_alt = linkpath.get_attribute('href')
                res_link_alt = no_escape_sequence(res_link_alt)
                
                res_link.append(res_link_alt)

            # === 제목에서 특수문자 삭제 ===

            idx = len(res_title)
            for i in range(idx):
                res_title_alt = res_title[i].text
                res_title_alt = no_escape_sequence(res_title_alt)

                # === 컨텐츠에서 특수문자 삭제 ===

                if i < len(res_content):
                    res_content_alt = res_content[i].text
                    res_content_alt = no_escape_sequence(res_content_alt)

                else: res_content_alt = ''
                
                if git:
                    url = original_url
                else:
                    tmp = res_link[i].split('/')
                    url = tmp[2]

                save_to_database('G', url, res_title_alt, res_link[i], res_content_alt, git, original_url)
                
        except Exception: raise ValueError(f"Stale element reference error processing item {original_url}")

        # === 검색 섹션: botstuff ===
        
        resultfield = driver.find_element(By.ID, 'botstuff')
        try:
            res_title = resultfield.find_elements(By.TAG_NAME, 'h3')
            res_content = resultfield.find_elements(By.CLASS_NAME, 'VwiC3b.yXK7lf.lVm3ye.r025kc.hJNv6b.Hdw6tb')

            res_link = []
            for titlefield in res_title:
                linkpath = titlefield.find_element(By.XPATH, '..')

                # === 링크에서 특수문자 삭제 ===

                res_link_alt = linkpath.get_attribute('href')
                res_link_alt = no_escape_sequence(res_link_alt)
                
                res_link.append(res_link_alt)

            # === 제목에서 특수문자 삭제 ===

            idx = len(res_title) - 2 # → 제외된 2개: <h3 aria_hidden="true"> <h3>다시 시도</h3> (항상 제외됨)
            for i in range(idx):
                res_title_alt = res_title[i].text
                res_title_alt = res_title_alt.replace("'", "\\'")

                # === 컨텐츠에서 특수문자 삭제 ===

                if i < len(res_content):
                    res_content_alt = res_content[i].text
                    res_content_alt = no_escape_sequence(res_content_alt)
                    
                else: res_content_alt = ''

                if git:
                    url = original_url
                else:
                    tmp = res_link[i].split('/')
                    url = tmp[2]
                save_to_database('G', url, res_title_alt, res_link[i], res_content_alt, git, original_url)

        except Exception: raise ValueError(f"Stale element reference error processing item {original_url}")

        # === 다음 페이지가 있으면 클릭 ===

        time.sleep(PAUSE_SEC)
        try: driver.find_element(By.ID, 'pnnext').click()
        except: break

    driver.quit()
    update_status('G', original_url, 'finished', git)


# =====================================================
# ==                  BING_SEARCH                    ==
# =====================================================


def bing_search(original_url, git=False):
    driver = driver_setup('http://127.0.0.1:4444/wd/hub')
    
    searchkey = ''
    nextpage_link = ''

    if git: searchkey = "site:github.com " + original_url
    else: searchkey = "site:" + original_url

    driver.get("https://www.bing.com/search")

    # === 검색어 전송 후 검색 진행 ===

    time.sleep(PAUSE_SEC * 2)
    try:
        searchfield = driver.find_element(By.XPATH, '//*[@id="sb_form_q"]')
    except NoSuchElementException:
        raise ValueError(f"Element load error processing item: {original_url}")

    searchfield.send_keys(searchkey)
    time.sleep(PAUSE_SEC)
    searchfield.send_keys(Keys.ENTER)
    
    while True:
        time.sleep(PAUSE_SEC)
        scrolltoend_bing(driver)

        # === 검색 섹션: b_results ===

        try:
            resultfields = driver.find_elements(By.XPATH, '//*[@id="b_results"]/li')
        except NoSuchElementException:
            raise ValueError(f"Element load error processing item: {original_url}")
        
        try:
            for resultfield in resultfields:
                if resultfield.get_attribute('class') != "b_algo": break

                titlefield = resultfield.find_element(By.XPATH, '//h2//a')
                res_content = no_escape_sequence(resultfield.find_element(By.XPATH, '//div[2]//p').text)
                
                res_title = no_escape_sequence(titlefield.text)
                res_url = titlefield.get_attribute('href')
                
                # === 컨텐츠에서 날짜 정보/특수문자 삭제 ===

                if " · " in res_content[:20]: res_content = res_content.split(" · ")[1]
                elif res_content[0] == "웹":
                    res_content = res_content[1:]

                # === 링크에서 BASE64 인코딩 해제 및 텍스트 삭제 ===

                if "aHR0c" in res_url:
                    tmp = "aHR0c" + res_url.split("aHR0c")[1]
                    tmp_b64 = tmp.split('&')[0]

                    res_url = no_escape_sequence(decode_base64(tmp_b64))
                    
                if r"#:~:text=" in res_url:
                    res_url = res_url.split(r"#:~:text=")[0]

                if git: url = original_url
                else: url = res_url.split('/')[2]

                # === 캐시된 페이지 확인 ===

                cached_data = None
                if not git:
                    try:
                        cache = driver.find_element(By.CLASS_NAME, 'trgr_icon')
                        cache.click()

                        cached_element = cache.find_element(By.XPATH, "..").find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "a")
                        cached_element.click()

                        # === 새 탭에서 캐시된 페이지 소스 저장 ===

                        last_tab = driver.window_handles[-1]
                        driver.switch_to.window(window_name=last_tab)
                        
                        time.sleep(PAUSE_SEC)
                        if "<!-- Apologies:Start -->" not in driver.page_source:
                            cached_data = driver.page_source.encode('utf-8')
                        driver.close()

                        first_tab = driver.window_handles[0]
                        driver.switch_to.window(window_name=first_tab)
                    except: pass

                # === 데이터베이스에 저장 ===

                try: save_to_database('B', url, res_title, res_url, res_content, git, original_url, cached_data=cached_data)
                except Exception as e: raise ValueError(f"Database save error - {e}")
        
        except Exception as e: raise ValueError(f"Value error processing item {original_url} - {e}")

        # === 다음 페이지가 있으면 넘어감 ===

        try:
            nextpage = driver.find_element(By.CLASS_NAME, 'sw_next').find_element(By.XPATH, '..')
            tmp_link = nextpage.get_attribute('href')

            if nextpage_link == tmp_link:
                raise ValueError(f"Critical error processing item: {original_url}")
            else:
                nextpage_link = tmp_link
                driver.get(nextpage_link)

        except: break

    driver.quit()
    update_status('B', original_url, 'finished', git)