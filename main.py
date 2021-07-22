from selenium import webdriver
import pandas as pd
import json
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep


def main(core_page):
    # Set to headless to prevent the browser from popping up
    options = Options()
    options.headless = True

    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

    driver = webdriver.Chrome(options=options, desired_capabilities=capabilities)

    driver.get(core_page)
    sleep(3)  # Wait for networks to load
    logs = driver.get_log("performance")

    log_list = []
    nw_data = pd.DataFrame({'name': [], 'status': [], 'nw_call_type': [], 'url': []})

    for log in logs:
        refined_log_str = log['message']
        refined_log_dict = json.loads(refined_log_str)  # Convert to complete dictionary

        log_params = refined_log_dict['message']['params']
        if 'type' in log_params.keys():
            nw_type = log_params['type']
            log_list.append(log_params)
            # Make sure there is a 'response' and then extract the data
            if 'response' in log_params.keys():
                status = log_params['response']['status']
                url = log_params['response']['url']
                name = url.split('/')[len(url.split('/')) - 1]
                nw_data.loc[len(nw_data.index)] = [name, status, nw_type, url]
            # If there is no 'response' there still could be useful data, check if there is only 'request'
            elif 'request' in log_params.keys():
                status = '*200.0'
                url = log_params['request']['url']
                name = url.split('/')[len(url.split('/')) - 1]
                nw_data.loc[len(nw_data.index)] = [name, status, nw_type, url]

    driver.quit()

    # Downloads the data
    nw_data.to_csv('nw_data.csv', index=False)

    # Downloads all network data into a csv, very useful for understanding the dataset
    with open('networks.json', 'w') as outfile:  # Makes the json for the tags with list data
        json.dump(log_list, outfile, indent=4)


if __name__ == '__main__':
    main('https://www.coach.com/')
