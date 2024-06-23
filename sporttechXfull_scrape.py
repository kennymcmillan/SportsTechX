from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

import socket
import time
import re
import pandas as pd

computer_name = socket.gethostname()

if computer_name == "AZFLP2593":
    
    options = webdriver.EdgeOptions()
    options.add_argument("--incognito")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
    driver.maximize_window()
  
else:
# Setup Chrome and WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    

print(f"Using {'Edge' if computer_name == 'AZFLP2593' else 'Chrome'} WebDriver")

# Open the Looker Studio report
url = 'https://lookerstudio.google.com/reporting/c7175b01-3602-41d5-9c31-31bfcbfcc574/page/p_0dc9nmnl8c'
driver.get(url)
driver.maximize_window()
time.sleep(3)

wait = WebDriverWait(driver, 5)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.tableBody')))
table_body = driver.find_element(By.CSS_SELECTOR, '.tableBody')
scroll_container = driver.find_element(By.CSS_SELECTOR, '.centerColsContainer')

# Function to extract rows data
def extract_rows():
    rows_data = []
    rows = table_body.find_elements(By.CSS_SELECTOR, '.row')
    for row in rows:
        try:
            cells = row.find_elements(By.CLASS_NAME, 'cell')
            row_data = [cell.text for cell in cells]
            rows_data.append(row_data)
            # print(row_data)
        except StaleElementReferenceException:
            continue  
    return rows_data

all_rows_data = set()
total_rows = 0

page_info = driver.find_element(By.CSS_SELECTOR, ".pageLabel").text
max_rows = int(re.search(r'/ (\d+)', page_info).group(1))
total_pages = (max_rows + 99) // 100  

for _ in range(total_pages): ## outer loop
    
    driver.execute_script('arguments[0].scrollTop = 0', scroll_container)
    time.sleep(3)
    
    for _ in range(6):  ## inner loop
        new_rows_data = extract_rows()
        for data in new_rows_data:
            all_rows_data.add(tuple(data))  # Add as tuple to allow set usage
        driver.execute_script('arguments[0].scrollTop += 500', scroll_container)
        time.sleep(3)

    if _ < total_pages - 1:  # Check to prevent clicking on the last page
        forward_button = driver.find_element(By.CSS_SELECTOR, '.pageForward')
        driver.execute_script("arguments[0].click();", forward_button)
        time.sleep(3)

unique_rows_data = [list(row) for row in all_rows_data if len(row) ==8]

driver.quit()

## Tidy scrape into a dataframe and save to csv

df = pd.DataFrame(unique_rows_data, 
                  columns=['Number','Name', 'Website', 'Description', 'City', 'Country', 'Sector', 'Sub-Sector'])
df['Number'] = df['Number'].str.replace(r'[^\d.-]', '', regex=True)
df = df[df['Number'].str.strip().astype(bool)]
df['Number'] = df['Number'].astype(float).astype(int)
df.sort_values('Number', inplace=True)

df.to_csv("sportstech.csv")
