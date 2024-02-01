import re
import os
import time
import json
import random
import warnings
import requests
import numpy as np
import pandas as pd
from config import Config
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse, parse_qs

warnings.filterwarnings('ignore')

def extract_digits(text):
    # Use a regular expression to find all digits in the text
    digits = re.findall(r'\d', text)
    # Join the list of digits into a single string
    result = ''.join(digits)
    return result

def extract_data_from_url(url):
    # Use urlparse to get the query parameters from the URL
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    company = query_params.get('company', [None])[0]
    posted_date_match = re.search(r'posted_time=(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)', url)
    posted_date = posted_date_match.group(1) if posted_date_match else None
    return company, posted_date

def process_remote_status(remote_dict):
    if 'remote' in remote_dict and remote_dict['remote']:
        return 'remote'
    else:
        return ''

def extract_job_id(url):
    # Check if the "jid=" parameter is present in the URL
    if "jid=" in url:
        # Split the URL by the "jid=" parameter and take the second part
        job_id_part = url.split("jid=")[1]
        # Extract the job ID by taking characters until the next "&" or end of the string
        job_id = job_id_part.split("&")[0]
        return job_id
    else:
        return None

def get_data(soup):
    try:
        # Find the script containing job list data
        script = soup.find('script', id='js_variables')

        if not script or not script.string:
            print("Script content not found.")
            return None

        script_content = script.string
        json_data = json.loads(script_content)
        json_list = json_data.get('jobList', [])

        selected_fields = ['Title', 'City', 'FormattedSalaryShort', 'EmploymentType', 'EmploymentTags', 'JobURL', 'SaveJobURL']
        selected_data_list = []

        for json_data in json_list:
            try:
                # Create a dictionary with only the selected fields for the current JSON
                selected_data = {field: json_data.get(field, None) for field in selected_fields}

                # Append the selected data to the list
                selected_data_list.append(selected_data)
            except Exception as e:
                print(f"Error in inner loop: {e}")
                continue  # Skip this iteration if there's an error

        # Create a DataFrame from the selected data list
        df = pd.DataFrame(selected_data_list)

        # Extract additional data from the 'SaveJobURL' field
        try:
            df[['Company', 'Posted_date']] = df['SaveJobURL'].apply(extract_data_from_url).apply(pd.Series)
        except Exception as e:
            print(f"Error extracting data from 'SaveJobURL': {e}")

        # Process 'EmploymentTags' to get 'RemoteStatus'
        try:
            df['RemoteStatus'] = df['EmploymentTags'].apply(process_remote_status)
        except Exception as e:
            print(f"Error processing 'EmploymentTags': {e}")

        # Extract 'JobID' from 'JobURL'
        try:
            df['JobID'] = df['JobURL'].apply(extract_job_id)
        except Exception as e:
            print(f"Error extracting 'JobID' from 'JobURL': {e}")

        # Add 'Current_Date_Time' column
        df['Current_Date_Time'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

        # Rename 'FormattedSalaryShort' column to 'Salary'
        df.rename(columns={'FormattedSalaryShort': 'Salary'}, inplace=True)

        # Drop unnecessary columns
        df.drop(['EmploymentTags', 'SaveJobURL'], axis=1, inplace=True)

        return df

    except Exception as e:
        print(f"Error in outer try block: {e}")
        return None

# You can customize the exception handling based on the specific errors you anticipate.
# %%
user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
]

proxy = Config.proxy
proxies = {"http": proxy, "https": proxy}

output_directory = Config.output_directory
subdirectory = Config.subdirectory
os.makedirs(os.path.join(output_directory, subdirectory), exist_ok=True)

all_dfs = []

for keyword in Config.keywords:
    Config.keyword = keyword
    url = f'https://www.ziprecruiter.com/jobs-search?search={keyword}&location=&company=&refine_by_location_type=&radius=&days=&refine_by_salary=&refine_by_employment=employment_type%3Aemployment_type%3Acontract&'
    user_agent = random.choice(Config.USER_AGENT_LIST)
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers, proxies=proxies, verify=False)

    if response.status_code == 200:
        # Do something with the response here
        print('Success!')
    else:
        # Print an error message
        print(f"Sorry, the website blocked your connection. Status Code: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')
    a = BeautifulSoup(str(soup.find('div', class_='job_results_headline')), 'html.parser').find('h1').get_text(strip=True)
    result = int(extract_digits(a))
    df1 = get_data(soup)
    all_dfs.append(df1)

    if 20 < result < 100:
        for j in range(2, 4):
            url2 = f'https://www.ziprecruiter.com/jobs-search?search={keyword}&location=&company=&refine_by_location_type=&radius=&days=&refine_by_salary=&refine_by_employment=employment_type%3Aemployment_type%3Acontract&page={j}'

            user_agent = random.choice(Config.USER_AGENT_LIST)
            headers = {'User-Agent': user_agent}
            res2 = requests.get(url2, headers=headers, proxies=proxies, verify=False)

            if res2.status_code == 200:
                # Do something with the response here
                print('Success!')
            else:
                # Print an error message
                print(f"Sorry, the website blocked your connection. Status Code: {res2.status_code}")

            soup2 = BeautifulSoup(res2.content, 'html.parser')
            df3 = get_data(soup2)
            all_dfs.append(df3)
            print('success for page ' + str(j))
    elif 100 < result:
        for i in range(2, 7):
            url1 = f'https://www.ziprecruiter.com/jobs-search?search={keyword}&location=&company=&refine_by_location_type=&radius=&days=&refine_by_salary=&refine_by_employment=employment_type%3Aemployment_type%3Acontract&page={i}'

            user_agent = random.choice(Config.USER_AGENT_LIST)
            headers = {'User-Agent': user_agent}
            res1 = requests.get(url1, headers=headers, proxies=proxies, verify=False)

            if res1.status_code == 200:
                # Do something with the response here
                print('Success!')
            else:
                # Print an error message
                print(f"Sorry, the website blocked your connection. Status Code: {res1.status_code}")

            soup1 = BeautifulSoup(res1.content, 'html.parser')
            df2 = get_data(soup1)
            all_dfs.append(df2)
            print('success for page ' + str(i))
    else:
        print('This keyword has only this data')

final_df = pd.concat(all_dfs)
final_df = final_df[final_df['EmploymentType'] != 'Full-Time']
final_df.drop_duplicates(inplace=True)

final_df

output_path = Config.output_csv_path1
if not os.path.exists(output_path):
    os.makedirs(output_path)

final_df.to_csv(os.path.join(output_path, Config.output_csv_zip), index=False)
