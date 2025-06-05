
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def login_to_linkedin(driver, email, password):
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)
    driver.find_element(By.ID, "username").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(5)

def scrape_profile(driver, profile_url):
    driver.get(profile_url)
    time.sleep(5)
    profile_data = {}
    try:
        profile_data['Full_Name'] = driver.find_element(By.CSS_SELECTOR, 'h1.text-heading-xlarge').text
    except:
        profile_data['Full_Name'] = None
    try:
        profile_data['Professional_Summary'] = driver.find_element(By.CSS_SELECTOR, 'div.text-body-medium').text
    except:
        profile_data['Professional_Summary'] = None
    # Additional fields can be scraped similarly...
    return profile_data

# Example use:
# options = Options()
# options.add_argument("--start-maximized")
# driver = webdriver.Chrome(options=options)
# login_to_linkedin(driver, "youremail", "yourpassword")
# data = scrape_profile(driver, "https://www.linkedin.com/in/example")
