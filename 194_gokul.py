__author__ = 'Gokul R'

PROJECT_DIR_NAME = 'jobsgenericwebcrawlerapp'
import sys, os, traceback, re, json, time, html

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_DIR_LIST = SCRIPT_DIR.split(PROJECT_DIR_NAME)
PROJECT_PATH = f"{SCRIPT_DIR_LIST[0]}{PROJECT_DIR_NAME}"
sys.path.append(os.path.dirname(PROJECT_PATH + r"\\"))
from bs4 import BeautifulSoup
import requests

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
        PageNo = 1
        JobCount = 0
        Domain = page.split('postings/')[0] + 'postings/'
        source_count_checker = Domain+"search"
        print(source_count_checker)
        UrlDomain = "https://"+page.split('/')[2]
        print(UrlDomain)

        soup = BeautifulSoup(requests.get(source_count_checker).content, "html.parser")
        # SourceCount = int(soup.find("h2", id="search-results").findNext("span").text.replace(")","").replace("(",""))
        # print(SourceCount)
        session = requests.Session()

        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        ]

        try:
            while True:
                PageUrl = Domain + f'search?page={PageNo}'
                print(PageUrl)
                headers = {"User-Agent": random.choice(USER_AGENTS)}
                response = requests.get(PageUrl,headers=headers)

                Status, Soup = self.getBSoupResult(response.content, Name='html.parser')
                JobsListag = Soup.find_all("div", class_=re.compile("job-item job-item-posting|job-item job-item-pool"))
                print(len(JobsListag))
                if not JobsListag:
                    break

                for JobItem in JobsListag:
                    JobCount += 1
                    title = JobItem.findNext("a").text.strip().replace("'",'')
                    url = JobItem.find("a")["href"]
                    job_url = UrlDomain + url
                    Descresponse = requests.get(job_url, headers=headers)

                    DescSoup = BeautifulSoup(Descresponse.content, 'html.parser')
                    try:
                        description = DescSoup.find("div", id="form_view").text.replace('”','').replace("'",'')
                        description = self.getcleanText(description)
                    except:
                        description = " "

                    try:
                        job_id=job_url.split('/')[-1]
                    except:
                        job_id='N/A'
                    try:
                        job_division=DescSoup.find('th',string=re.compile('Department')).findNext('td').text.replace("'",'')
                    except:
                        job_division='N/A'
                    try:
                        time_type=DescSoup.find('th',string=re.compile('Full-Time/Part-Time|Status:|Position Category')).findNext('td').text.replace("'",'')
                    except:
                        time_type='N/A'
                    try:
                        job_category=DescSoup.find('th',string=re.compile('Category|Position Type:|Department')).findNext('td').text.replace("'",'')
                        if time_type==job_category:
                            job_category=''
                    except:
                        job_category='N/A'

                    try:
                        location=DescSoup.find('th',string=re.compile('Location|Campus:')).findNext('td').text.replace("'",'')
                    except:
                        location='Global'
                    if 'ashland' in page:
                        location='Ashland, OH 44805'
                    elif 'jobs.ecsu.edu' in page:
                        location='1704 Weeksville Road,Elizabeth City, NC 27909'
                    try:
                        posted_date=DescSoup.find('th',string=re.compile('Open Date|Expected Start Date|Posting Date')).findNext('td').text.replace("'",'')
                    except:
                        posted_date=self.CurrentDateStr
                    try:
                        close_date=DescSoup.find('th',string=re.compile('Close Date|Closing Date')).findNext('td').text.replace("'",'')
                    except:
                        close_date='N/A'
                    try:
                        experience_req=DescSoup.find('th',string=re.compile('Minimum Qualifications|Preferred Qualifications')).findNext('td').text.replace("'",'')
                    except:
                        experience_req='N/A'
                    try:
                        job_compensation=DescSoup.find('th',string=re.compile('Salary')).findNext('td').text.replace("'",'')
                    except:
                        job_compensation='N/A'
                    try:
                        vacancy_count=DescSoup.find('th',string=re.compile('Number of Vacancies|Number of Positions')).findNext('td').text.replace("'",'')
                    except:
                        vacancy_count='N/A'
                    job_data = {
                        'title': title,
                        'joburl': job_url,
                        'posted_date':posted_date,
                        'location':location,
                        'job_category':job_category[:100],
                        'time_type':time_type,
                        'close_date':close_date,
                        'vacancy_count':vacancy_count,
                        'job_id':job_id,
                        'job_division':job_division[:100],
                        'job_compensation':job_compensation[:200],
                        'experience_req': experience_req[:400],
                        'description': description,
                    }
                    print(job_data)
                    db_result = self.insertJob(CmpData, job_data)
                    SuccessTotal += db_result['SuccessTotal']
                    FailedTotal += db_result['FailedTotal']
                PageNo += 1
                print("Pageeeeeeeeeeeeeeeeeeeeeeeeee Nooooooooooooooooooooooooooooo", PageNo, JobCount)

                time.sleep(5)

            spider_result['data']['SuccessTotal'] = SuccessTotal
            spider_result['data']['FailedTotal'] = FailedTotal
            spider_result['data']['response']['status_code'] = response.status_code
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
    URLSNoList=[202699,229695]
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
