
import logging
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import time
import pandas as pd


URL = "https://portexaminer.com/"

def get_config(config_file_path):
    """
    Read config file and return config dictionary

    Parameters
    ----------
    config_file_path : TYPE
       
    Returns
    -------
    config : TYPE
        
    """
    
    with open(config_file_path, "r") as fp:
        config = json.load(fp)

    return config



def get_trade_data(companies: list):
    """
    This function uses crome browser to get details of shipments of companies 
    given as input from the global portexaminer url. It searches for the company
    and then navigates to company page. Then traverse links within the page to 
    to get required details.

    Parameters
    ----------
    companies : list
        
    Returns
    -------
    df : TYPE

    """
    global URL
    logger = logging.getLogger(__name__)
    
    driver = webdriver.Chrome()
    
    searched_importer =[]
    shipper=[] 
    consignee = []
    notify_party = []
    bill_of_lading_no = []
    
    #traverse companies to get links on each company page
    for company in companies:
        
        driver.get(URL)
        
        #identify dropdown
        sel = Select(driver.find_element(By.NAME, 'search-field-1'))
        
        # select Importer name from dropdown
        sel.select_by_visible_text("Importer Name")
        time.sleep(0.8)
    
        #enter company name is search box
        input_box = driver.find_element(By.ID, 'input-box')
        input_box.send_keys(company)
        
        #click search button
        button = driver.find_element(By.ID, 'search-button')
        button.click()
        time.sleep(0.8)
    
        search_items = driver.find_elements(By.CSS_SELECTOR, 'div.search-item')
        time.sleep(10)
        
        links = []
        
        # traverse for loop to get details of shipper,consignee,notify party, bill 
        for item in search_items:
            link = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
            links.append(link)
        
        # get details on each link
        for link in links:
            driver.get(link)
            try:
                shipper_id = driver.find_element(By.ID,'shipper')
                shipper.append(shipper_id.find_element(By.CSS_SELECTOR,'span').text)
            except:
                shipper.append("")
    
            try:
                consignee_id = driver.find_element(By.ID,'consignee')
                consignee.append(consignee_id.find_element(By.CSS_SELECTOR,'span').text)
            except:
                consignee.append("")
            
            try:
                notify_party_id = driver.find_element(By.ID,'notify-1')
                notify_party.append(notify_party_id.find_element(By.CSS_SELECTOR,'span').text)
            except:
                notify_party.append("")
            
            try:
                details = driver.find_element(By.ID,'details')
                bill_of_lading_no.append(details.find_element(By.XPATH,'//*[@id="details"]/div/div/div[1]/div[1]/div').text)
            except:
                bill_of_lading_no.append("")
            
            searched_importer.append(company)
            driver.back()
            
        logger.info(f"Success: Scraped data for importer {company}")
            
            
    driver.close()
    
    df = pd.DataFrame({'Searched Importer':searched_importer,
                       'Shipper':shipper, 
                       'Consignee':consignee, 
                       'Notify Party':notify_party, 
                       'Bill Of Lading No':bill_of_lading_no})
    return df



def main():
    """
    Main function, First get data using function and store into csv file
    :return:
    """
    # Set up logging
    logging.basicConfig(filename='portexaminer_webscrapping_log_file.log', level=logging.INFO, 
                        format='%(asctime)s:%(levelname)s:%(message)s')

    config = get_config("portexaminer_webscrapping_Config_file.json")
    
    df = get_trade_data(config["Companies"])
    
    
    df.to_csv(config["File"], index=False, encoding='utf-8')
    logging.info("Success: Saved data into csv file")
    

if __name__ == '__main__':
    main()




