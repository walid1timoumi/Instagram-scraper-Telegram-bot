import re
import json
import time
from shutil import which
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from config.settings import COOKIES_PATH

def is_valid_username(username: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9._]{1,30}$', username))

def load_instagram_cookies(driver):
    with open(COOKIES_PATH, 'r') as f:
        cookies = json.load(f)
        for cookie in cookies:
            cookie.pop('sameSite', None)
            driver.add_cookie(cookie)

def scrape_instagram(username):
    if not is_valid_username(username):
        return {"error": "❌ Invalid Instagram username format."}

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")


    service = Service(which("chromedriver"))
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print("👀 Opening Instagram...")
        driver.get("https://www.instagram.com/")
        time.sleep(3)
        driver.get("https://www.instagram.com/")
        load_instagram_cookies(driver)
        driver.get("https://www.instagram.com/accounts/edit/")
        time.sleep(3)

        if "login" in driver.current_url:
            return {"error": "❌ Failed to log in. Cookies may be invalid or expired."}

        print(f"🔍 Visiting profile: {username}")
        profile_url = f"https://www.instagram.com/{username}/"
        driver.get(profile_url)
        time.sleep(5)

        if "Sorry, this page isn't available." in driver.page_source:
            return {"error": "❌ Instagram profile not found."}

        try:
            profile_pic = driver.find_element(By.XPATH, "//header//img").get_attribute("src")
        except:
            profile_pic = None

        try:
            name = driver.find_element(By.TAG_NAME, "h1").text
            if not name.strip():
                raise Exception("Empty")
        except:
            name = username

        try:
            bio = driver.find_element(By.XPATH, "//span[contains(@class, '_ap3a')]").text
        except:
            bio = "No bio found"

        try:
            followers = driver.find_elements(By.XPATH, "//ul/li")[1].text
        except:
            followers = "?"

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        post_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
        post_urls = []
        seen = set()
        for a in post_links:
            href = a.get_attribute("href")
            if href and href not in seen:
                seen.add(href)
                post_urls.append(href)
            if len(post_urls) == 3:
                break

        posts = []
        for url in post_urls:
            driver.get(url)
            time.sleep(3)

            try:
                img = driver.find_element(By.XPATH, "//article//img")
                image_url = img.getAttribute("src")
            except:
                image_url = None

            try:
                caption = driver.find_element(By.XPATH, "//div[contains(@class, '_a9zs')]/span").text
            except:
                caption = "No caption"

            posts.append({"image": image_url, "caption": caption})

        return {
            "name": name,
            "bio": bio,
            "followers": followers,
            "profile_pic": profile_pic,
            "posts": posts
        }

    except Exception as e:
        return {"error": f"⚠️ Error: {str(e)}"}

    finally:
        driver.quit()
