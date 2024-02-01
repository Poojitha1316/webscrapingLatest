import re
import os
import time
import json
import random
import warnings
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from config import Config
from datetime import datetime, timedelta

# Suppress warnings
warnings.filterwarnings('ignore')

# User-agent list for random selection
# user_agent_list = [
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
# ]

# Randomly select a user-agent
user_agent = random.choice(Config.USER_AGENT_LIST)
headers = {'User-Agent': user_agent}
proxy = Config.proxy
proxies = {"http": proxy, "https": proxy}

# Function to categorize work type based on title
def categorize_work_type(title):
    if 'Onsite' in title:
        return 'On-site'
    elif 'Hybrid' in title:
        return 'Hybrid'
    elif 'Remote' in title:
        return 'Remote'
    else:
        return None

# Function to convert relative dates to actual dates
def convert_relative_dates(relative_date):
    try:
        if 'today' in relative_date or 'Today' in relative_date:
            return datetime.now().date()
        elif 'yesterday' in relative_date or '1 day ago' in relative_date:
            return (datetime.now() - timedelta(days=1)).date()
        elif 'days ago' in relative_date:
            days_ago = int(relative_date.split()[0])
            return (datetime.now() - timedelta(days=days_ago)).date()
        else:
            return None
    except Exception as e:
        return None

# Function to get data from the soup object
def get_data(soup):
    try:
        # Extracting job listings using different classes
        job_listings = soup.find_all('div', class_='collapsed-activated')
        all_dfs = []

        for listing in job_listings:
            listing_soup = BeautifulSoup(str(listing), 'html.parser')
            inner_listings = listing_soup.find_all('li', class_='data-results-content-parent relative bg-shadow')

            inner_dfs = []

            for inner_listing in inner_listings:
                job_data = {}
                inner_soup = BeautifulSoup(str(inner_listing), 'html.parser')

                try:
                    # Extracting data from the inner listing
                    job_data['publish_time'] = inner_soup.find('div', class_='data-results-publish-time').text.strip()
                    job_data['title'] = inner_soup.find('div', class_='data-results-title').text.strip()
                    job_data['company'] = inner_soup.find('div', class_='data-details').find('span').text.strip()
                    job_data['location'] = inner_soup.find('div', class_='data-details').find_all('span')[1].text.strip()
                    job_data['employment_type'] = inner_soup.find('div', class_='data-details').find_all('span')[2].text.strip()
                    job_url = inner_listing.find('a', class_='data-results-content')['href']
                    job_data['url'] = f"https://www.careerbuilder.com{job_url}"
                    result = inner_soup.select('div.block:not(.show-mobile)')
                    job_data['result'] = result[0].get_text(strip=True)

                    inner_dfs.append(pd.DataFrame([job_data]))

                except Exception as e:
                    continue

            try:
                combined_df = pd.concat(inner_dfs, ignore_index=True)
                all_dfs.append(combined_df)
            except Exception as e:
                continue

        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df['Work Location'] = final_df['location'].apply(categorize_work_type)
        final_df['Date Posted'] = final_df['publish_time'].apply(convert_relative_dates)
        final_df['Current Date'] = datetime.now().date()

        # Column mapping
        columns_mapping = {
            'title': 'Title',
            'company': 'Company',
            'location': 'Location',
            'employment_type': 'Job_type',
            'url': 'Job_url',
            'result': 'Salary'
        }

        final_df.rename(columns=columns_mapping, inplace=True)

        # Extract job IDs and create a new column
        final_df['Job_id'] = final_df['Job_url'].str.extract(r'/job/(.*)')
        final_df.drop(columns=['publish_time'], inplace=True)

        return final_df

    except Exception as e:
        return None

# Define the output file path based on the config
output_directory = Config.output_directory
output_subdirectory = Config.subdirectory
output_filename = Config.output_csv_career
output_path = os.path.join(output_directory, output_subdirectory)
output_file_path = os.path.join(output_path, output_filename)

# Initialize lists to store data and soup objects
dfs = []
soups = []

# Create a session to reuse the same connection
session = requests.Session()

try:
    for keyword in Config.keywords:
        keyword_lower = keyword.lower()

        for u in range(0, 20):
            url = Config.url_career.format(keyword=keyword_lower.replace(" ", "%20"), page=u)

            try:
                response = session.get(url, headers=headers, proxies=proxies, verify=False)
                response.raise_for_status()

                if response.status_code == 200:
                    print('Success!')
                else:
                    print('Sorry, your connection is blocked by the website')
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')
                soups.append(soup)
                result_df = get_data(soup)

                if result_df is None or result_df.empty:
                    print('Sorry, but the bot did not find proper data on this page')
                    continue

                dfs.append(result_df)
                print(f'Success for the page: {u}')

            except requests.RequestException as e:
                print(f'Request error for page {u}: {e}')

            except Exception as e:
                print(f'Error for page {u}: {e}')

            time.sleep(5)

except Exception as e:
    print(f'An unexpected error occurred: {e}')

# Concatenate dataframes
final_df = pd.concat(dfs, ignore_index=True)
final_df.drop_duplicates(inplace=True)

# Save the data to the specified file path
if not os.path.exists(output_path):
    os.makedirs(output_path)

final_df.to_csv(output_file_path, index=False)
