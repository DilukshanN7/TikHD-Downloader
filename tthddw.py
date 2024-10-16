from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
from urllib.parse import urlparse

def get_json_from_script(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set up the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for the script tag to be present in the DOM
        wait = WebDriverWait(driver, 10)
        script_present = EC.presence_of_element_located((By.ID, "__UNIVERSAL_DATA_FOR_REHYDRATION__"))
        wait.until(script_present)

        # Get the page source
        html = driver.page_source

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Find the script tag
        script_tag = soup.find('script', id='__UNIVERSAL_DATA_FOR_REHYDRATION__')

        if script_tag:
            # Extract the JSON content
            json_content = script_tag.string

            try:
                # Parse the JSON content
                data = json.loads(json_content)
                return data
            except json.JSONDecodeError:
                print("Failed to parse JSON content")
                return None
        else:
            print("Script tag not found")
            return None

    finally:
        # Close the browser
        driver.quit()

def download_file(url, folder):
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the URL and get the path
        parsed_url = urlparse(url)
        
        # Get the last part of the path as the filename
        filename = os.path.basename(parsed_url.path)
        
        # If filename is empty, use a default name
        if not filename:
            filename = 'video.mp4'
        
        # Ensure the filename is valid
        filename = ''.join(c for c in filename if c.isalnum() or c in '._- ')
        
        # Create the full file path
        filepath = os.path.join(folder, filename)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filepath}")
    else:
        print(f"Failed to download: {url}")

# Usage
url = "https://www.tiktok.com/@tatatopsecret/video/7425160516324150560?_r=1&_t=8qVywtdGma0"  # Replace with the actual URL
json_data = get_json_from_script(url)

if json_data:
    # Now you can work with the JSON data
    video = json_data["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]["video"]

    bitrate_info = video["bitrateInfo"]

    try:
        lowest_quality = min(bitrate_info, key=lambda x: x.get('QualityType', float('inf')))

        url_list = lowest_quality['PlayAddr']['UrlList']

        folder_name = "downloaded_videos"
        os.makedirs(folder_name, exist_ok=True)

        # Download each URL
        for url in url_list:
            download_file(url, folder_name)

    except ValueError:
        print("No valid quality information found.")    
    
else:
    print("Failed to retrieve JSON data")