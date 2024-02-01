# config.py for zipRecruiter
from datetime import datetime
class Config:
    proxy = "http://4985462b823f2071f48ff52fb687708658d0d488:@proxy.zenrows.com:8001"
    
    url_zip = "https://www.ziprecruiter.com/jobs-search"
    url_indeed = "https://www.indeed.com/jobs?q={keyword}&sc=0kf%3Ajt%28contract%29%3B&page={page}"
    url_career = "https://www.careerbuilder.com/jobs?cb_apply=false&cb_workhome=all&emp=jtct%2Cjtc2%2Cjtcc&keywords={keyword}&location=&pay=&posted=&sort=date_desc&page={page}"
    url_dice = "https://job-search-api.svc.dhigroupinc.com/v1/dice/jobs/search"
    
    USER_AGENT_LIST = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    ]
    
    API_KEY = "1YAt0R9wBg4WfsF9VB2778F5CHLAPMVW3WAZcKd8"
    HEADERS = {
        "authority": "job-search-api.svc.dhigroupinc.com",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "x-api-key": API_KEY,
    }
    
    output_csv_zip = "output_ZipRecruiter.csv"
    output_csv_indeed = "output_Indeed.csv"
    output_csv_dice = "output_Dice.csv"
    output_csv_career = "output_CareerBuilder.csv"
    
    search_type = "1"
    
    output_directory = "output"
    subdirectory = datetime.now().strftime('%Y-%m-%d')
    output_csv_path1 = f"output/{datetime.now().strftime('%Y-%m-%d')}"
    output_csv_path2 = f"{output_directory}/{subdirectory}"
    keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientists", "Data engineer", "Business System Analyst"]