from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pickle
import time
import json
import os
from dotenv import load_dotenv
import base64

load_dotenv()

def get_email_password():
    email = os.getenv("LINKED_IN_EMAIL_ID",None)
    if email:
        email = base64.b64decode(email).decode("ascii")
    password = os.getenv("LINKED_IN_PASSWORD",None)
    if password:
        password = base64.b64decode(password).decode("ascii")
    return email, password

def scrape_company_info(company_name):
    driver = None
    company_url = "Not Found"
    employee_count = "Not Found"
    search_url = "https://www.linkedin.com/search/results/all/?keywords={0}&origin=GLOBAL_SEARCH_HEADER&sid=Fvm"
    try:
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument('--ignore-certificate-errors')
        # # options.add_argument("user-data-dir=/home/onzway/onzway-py-grubhub/src/selenium/"+rest_unique_name)
        # options.add_experimental_option("useAutomationExtension", False)
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        caps = DesiredCapabilities.CHROME
        caps['loggingPrefs'] = {'performance': 'ALL', 'network': 'ALL'}
        caps['goog:loggingPrefs'] = {'performance': 'ALL', "network": "ALL"}
        driver = webdriver.Chrome(options=options,
                                # executable_path=r'/usr/bin/chromedriver',
                                executable_path=r'/usr/local/bin/chromedriver',
                                desired_capabilities=caps)
        search_page = search_url.format(company_name)
        login_url = "https://www.linkedin.com/login"
        driver.get(search_page)
        driver.delete_all_cookies()
        if os.path.exists("cookies.pkl"):
            cookies = pickle.load(open("cookies.pkl", "rb"))
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(e)
        if os.path.exists("sessions.pkl"):
            sessions = pickle.load(open("sessions.pkl", "rb"))
            for session in sessions.items():
                try:
                    driver.execute_script("window.sessionStorage.setItem('{}',{})".format(session[0], json.dumps(session[1])))
                except Exception as e:
                    print(e)
        if os.path.exists("localstorage.pkl"):
            sessions = pickle.load(open("localstorage.pkl", "rb"))
            for session in sessions.items():
                try:
                    driver.execute_script("window.localStorage.setItem('{}',{})".format(session[0], json.dumps(session[1])))
                except Exception as e:
                    print(e)
        driver.get(search_page) # or driver.refresh() if url is not login url.

        time.sleep(10)
        if driver.current_url == search_page:
            if "authwall" in driver.current_url or "login" in driver.current_url:
                driver.get(login_url)
                time.sleep(5)
                if login_url == driver.current_url:
                    email, password = get_email_password()
                    if email is not None  and password is not None:
                        email_input = driver.find_element(By.XPATH, "//input[@id='username']")
                        password_input = driver.find_element(By.XPATH, "//input[@id='password']")
                        time.sleep(5)

                        if email_input:
                            for e in list(email):
                                # print('p :: ', p)
                                email_input.send_keys(e)
                        if password_input:
                            for p in list(password):
                                # print('p :: ', p)
                                password_input.send_keys(p)
                        
                        login = driver.find_element(By.XPATH,"//button[@type='submit']")
                        login.click()
                        time.sleep(5)
                    else:
                        print("Please provide your email_id and password")
                        return company_url, employee_count

            driver.get(search_page)
            time.sleep(5)
            session_storage = driver.execute_script("return window.sessionStorage")
            local_storage = driver.execute_script("return window.localStorage")
            pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
            pickle.dump(session_storage, open("sessions.pkl", "wb"))
            pickle.dump(local_storage, open("localstorage.pkl", "wb"))
            time.sleep(5)
            company_link_located = driver.find_element(By.XPATH, "//div[contains(@data-chameleon-result-urn,'company')][1]//a")
            if company_link_located:
                company_url =  company_link_located.get_attribute("href")
                print(company_url)
                if company_url != "Not Found":
                    driver.get(company_url+"about/")
                    time.sleep(3)
                    get_company_size = driver.find_element(By.XPATH, "//dl[contains(., 'Company size')]//dd[contains(.,'employees')]")
                    if get_company_size:
                        print(get_company_size.text, (get_company_size.text.replace("employees","")).strip() )
                        employee_count = (get_company_size.text.replace("employees","")).strip()                        
    
                print("here",company_url, employee_count)
            time.sleep(5)
            driver.close()
            return company_url, employee_count
        else:
            print("can get login url", driver.current_url)
            print("possibley email and password provided by you is wrong")
            return company_url, employee_count
        
    except Exception as e:
        print("error is:{0}".format(e))
        if driver:
            driver.close()
        return company_url, employee_count


from playwright.sync_api import Playwright, sync_playwright, expect

def scrape_info_using_playwright(company_list):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    op_data = []
    try:
        email, password = get_email_password()
        if email is not None  and password is not None:
            page = context.new_page()
            page.goto("https://www.linkedin.com/login")
            page.get_by_label("Email or phone").click()
            page.get_by_label("Email or phone").fill("er.rushabhdoshi@gmail.com")
            page.get_by_label("Email or phone").press("Tab")
            page.get_by_label("Password", exact=True).fill("@irswan02")
            page.get_by_label("Password", exact=True).press("Enter")
            for data in company_list:
                company_url = "Not Found"
                employee_count = "Not Found"
                try: 
                    page.get_by_placeholder("Search", exact=True).click()
                    page.get_by_placeholder("Search", exact=True).fill(data[0])
                    page.get_by_placeholder("Search", exact=True).press("Enter")
                    page.get_by_role("group", name="Search results for "+data[0]+".")
                    element = page.locator("xpath=//div[contains(@data-chameleon-result-urn,'company')]").nth(0).locator("//a").nth(0)
                    company_url = element.get_attribute("href")
                    print(company_url)
                    # element.click()
                    page.goto(company_url+"/about")
                    # page.get_by_role("link", name="About", exact=True).click()
                    employee_count = page.locator("xpath=//dl[contains(., 'Company size')]//dd[contains(.,'employees')]").inner_html()
                    employee_count = employee_count.replace("employees","").strip()
                    print(company_url, employee_count)
                    data.extend([company_url, employee_count])
                    op_data.append(data)
            
                except Exception as e:
                    print("error is:{0}".format(e))
                    data.extend([company_url, employee_count])
                    op_data.append(data)
            context.close()
            browser.close()
            return op_data
        else:
            print("Please provide your email_id and password")
            context.close()
            browser.close()
            return op_data
        
    except Exception as e:
        print("error is:{0}".format(e))
        return op_data
