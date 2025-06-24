__author__ = 'Thirupathilaxmi Sangepu'


PROJECT_DIR_NAME = 'jobsgenericwebcrawlerapp'
import sys, os, traceback, re, json, time, html

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_DIR_LIST = SCRIPT_DIR.split(PROJECT_DIR_NAME)
PROJECT_PATH = f"{SCRIPT_DIR_LIST[0]}{PROJECT_DIR_NAME}"
sys.path.append(os.path.dirname(PROJECT_PATH + r"\\"))
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
driver=webdriver.Chrome()
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException

from Settings import JA_CRAWL_STATUS_MASTER as CRAWL_STATUS, DAILY_SPIDER_CONFIG, HTTP_STATUS_CODES_CONFIG
from main.GenericWebCrawlerAdapter import GenericWebCrawlerBaseAdapterClass
from main.GenericDBRepository import GenericDBRepositoryClass
import random


class NonATSCustomSpiderClass(GenericWebCrawlerBaseAdapterClass):
    def __init__(self, DailySpiderID, PatternID=None, CallDescOnly=False, **kwargs):
        super().__init__(kwargs.get('DBEnv'), DailySpiderID, PatternID)
        self.CDMSID = kwargs.get('CDMSID', 0)
        self.URLSNoList = kwargs.get('URLSNoList', [])
        self.PyResourceName = kwargs.get('PyResourceName', '').strip()
        self.CallDescOnly = CallDescOnly

    def __repr__(self):
        return self.__class__.__name__

    @property
    def CurrentFilePath(self):
        """
        Get Current File path
        """
        return str(os.path.abspath(__file__))

    def getCompanyList(self, **kwargs):
        """
        Get Company URL List by DailySpider, CDMSID/URLSNO
        """
        return self.getCompanies(self.CDMSID, self.URLSNoList, self.PyResourceName, **kwargs)

    def spiderCode(self, page, **kwargs):
        """
        Jobs Listing Page: Extract Jobs from given Page
        """
        CmpData = kwargs
        """Extract jobs from Delta Plus careers page"""
        self.logger.info("# Step-4. Run spiderCode for Job Listing from Page: %s", page)
        SuccessTotal, FailedTotal = (0, 0)
        spider_result = {
            'status': None,
            'data': {'response': {'status_code': '', 'content': ''}, 'SuccessTotal': SuccessTotal,
                     'FailedTotal': FailedTotal},
            'error': ''
        }
        PageNo=1
        JobCount=0
        try:
            Domain=page.split('/')[2]
            SubCategory=page.split('/')[4]
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': f'https://{Domain}',
                'Referer': f'https://{Domain}/careersection/{SubCategory}/joblist.ajax',
                'Sec-Fetch-Dest': 'iframe',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                # 'Cookie': 'lastActiveElementId=requisitionListInterface.pagerDivID1792.P3; locale=en; _gcl_au=1.1.796261439.1748843870; _gid=GA1.3.225094484.1748843870; _fbp=fb.2.1748843871072.468227083961666271; _gat_UA-109329221-3=1; _ga=GA1.1.1457703424.1748843870; _ga_QTZBXS7ZNZ=GS2.1.s1748849519$o2$g1$t1748849747$j60$l0$h0',
            }
            while True:
                data = {
                    'iframemode': '1',
                    'ftlpageid': 'reqListAllJobsPage',
                    'ftlinterfaceid': 'requisitionListInterface',
                    'ftlcompid': 'rlPager',
                    'jsfCmdId': 'rlPager',
                    'ftlcompclass': 'PagerComponent',
                    'ftlcallback': 'ftlPager_processResponse',
                    'ftlajaxid': 'ftlx3',
                    'rlPager.currentPage': f'{PageNo}',
                    'languageSelect': 'en',
                    'dropListSize': '25',
                    'dropSortBy': '10',
                    'lang': 'en',
                }

                response = requests.post(page, headers=headers, data=data)
                try:
                    try:
                        match = re.search(r'\((\d+) jobs found\)|(\d+)\s+competitions\s+found', response.text)
                        total_jobs = match.group(1)
                    except:
                        try:
                            match = re.search(r"(\d+)\s+jobs\s+found", response.text)
                            total_jobs = match.group(1)
                        except:
                            match = re.search(r"(\d+)\s+offerte di lavoro trovate|Posizioni aperte\s*\(*\s*(\d+)\s+offerte", response.text)
                            total_jobs = match.group(1)


                except:
                    try:
                        match = re.search(r":\s*(\d+)\s+(jobs matching your criteria)|Search Results\s*:\s*(\d+)", response.text)
                        total_jobs = match.group(1)
                    except:
                        break

                if JobCount>int(total_jobs):
                    break
                try:
                    try:
                        job_numbers = set(re.findall('Job Number[:\\%5C]*\s*([A-Z0-9]+)', response.text))
                    except:
                        job_numbers=set(re.findall(r"Codice offerta%5C: (\d+)",response.text))
                    if len(job_numbers)==0:
                        break
                    print(job_numbers)
                    print(len(job_numbers))
                except:
                    break
                JobCount += 25

                PageNo+=1
                for eachid in job_numbers:
                    job_url=f'https://{Domain}/careersection/{SubCategory}/jobdetail.ftl?job={str(eachid)}&lang=en'
                    print("job_url:" ,job_url)
                    driver.get(job_url)
                    self.sleep(1)
                    Soup = BeautifulSoup(driver.page_source, 'html.parser')
                    try:
                        title=Soup.find('span',class_='titlepage').text.replace("'",'')
                    except:
                        try:
                            title=Soup.find('h1',class_=re.compile('mb-4|title')).text.replace('\t','').replace('\n','').replace("'",'')
                        except:
                            continue
                    try:
                        location=Soup.find('span',string=re.compile('Location')).findNext('span',class_='text').text.replace("'",'')
                    except:
                        try:
                            location=Soup.find('div',id='job-details').text.replace('\t','').replace('\n','').replace("'",'')
                        except:
                            try:
                                location=Soup.find_all('span',id=re.compile('^requisitionDescriptionInterface.ID'))[3].text
                            except:
                                location=''

                    try:
                        description = Soup.find('table',class_='tablelist').text.replace("'",'')

                    except:
                        try:
                            description=Soup.find('div',class_=re.compile('job_description|mainsection|ftllist')).text.replace("'",'')

                        except:
                            description = " "

                    try:
                        job_id=job_url.split('?job=')[1].replace('&lang=en','')
                    except:
                        job_id='N/A'
                    try:
                        posted_date = Soup.find('span', string=re.compile('Posting')).findNext('span', class_='text').text
                    except:
                        try:
                            posted_date=Soup.find('span',class_='field_value posted-date').text
                        except:
                            posted_date=self.CurrentDateStr
                    try:
                        job_category=Soup.find('span',string=re.compile('Organization')).findNext('span',class_='text').text.replace("'",'')
                    except:
                        job_category=''
                    try:
                        category=Soup.find('span',string=re.compile('Organization')).findNext('div').text.replace("'",'')
                        if posted_date==category:
                            job_subcategory=''
                        elif location==category:
                            job_subcategory = ''
                        else:
                            job_subcategory=''

                    except:
                        job_subcategory=''
                    try:
                        job_shift=Soup.find('span',string=re.compile('Shift')).findNext('span',class_='text').text.replace("'",'')
                    except:
                        job_shift=''
                    try:
                        time_type=Soup.find('span',string=re.compile('Full Time|Part Time')).findNext('span',class_='text').text.replace("'",'')
                    except:
                        time_type=''


                    job_data = {
                        'title': title,
                        'joburl': job_url,
                        'posted_date':posted_date,
                        'location':location[:100],
                        'job_id':job_id,
                        'time_type':time_type,
                        'job_category':job_category,
                        'job_subcategory':job_subcategory,
                        'job_shift':job_shift,
                        'description': description,
                    }
                    print(job_data)
                    db_result = self.insertJob(CmpData, job_data)
                    SuccessTotal += db_result['SuccessTotal']
                    FailedTotal += db_result['FailedTotal']

            spider_result['data']['SuccessTotal'] = SuccessTotal
            spider_result['data']['FailedTotal'] = FailedTotal
            spider_result['data']['response']['status_code'] ='200'
            spider_result['status'] = True
            return spider_result
        except Exception as e:
            self.logger.error("spiderCode ErrorLog %s", traceback.format_exc())
            spider_result['status'] = False
            spider_result['error'] = str(traceback.format_exc())
            return spider_result

    def parserCode(self, job_data):
        """
        Extract the job description from the job data.
        """
        pass
if __name__ == '__main__':
    PatternID = None
    URLSNoList=[208055]
    DBRepo = GenericDBRepositoryClass('DBEnv')
    if URLSNoList:
        QStatus,CMPList = DBRepo.getCompaniesbyURLSNoList(URLSNoList)
    elif PatternID:
        QStatus,CMPList = DBRepo.getCompaniesbyPatternID(PatternID)
    else:
        QStatus = None
        print ("Provide URLSNoList or PatternID Details")
    print ("QStatus:", QStatus, "CMPList:",  CMPList)
    if QStatus:
        for eachCMP in CMPList:
            print (eachCMP)
            print ("*#"*100)
            if eachCMP['PatternID'] is None:
                eachCMP['PatternID'] = 0

            NonATSCustomSpiderClass(DailySpiderID=eachCMP['DailySpider'],PatternID=eachCMP['PatternID'], CDMSID=eachCMP['CDMSID'], URLSNoList=[eachCMP['Sno']]).run()
            print ("*#"*100)
    else:
        print ("Invalid Compnay Details Provided")
