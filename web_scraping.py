import requests
import bs4
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


load_dotenv()
host = os.getenv('dbhost')
dbname = os.getenv('dbname')
user = os.getenv('dbuser')
port = os.getenv('dbport')
password = os.getenv('dbpassword')
db_info = {'user': user, 'password': password, 'host': host, 'port': port, 'dbname': dbname}
# print(db_info)


def connect_pg_db(db_info):
    conn_str = "{}://{}:{}@{}:{}/{}".format(
        "postgresql+psycopg2",
        db_info["user"],
        db_info["password"],
        db_info["host"],
        db_info["port"],
        db_info["dbname"],
    )
    alchemyEngine = create_engine(conn_str, pool_recycle=3600)
    pg_connection = alchemyEngine.connect()
    return pg_connection


def get_area_code(location):
    pg_conn = connect_pg_db(db_info)
    sql_ = "select * from location_code_ct where target_location = '{}'".format(location)
    row = pg_conn.execute(sql_)
    area_code_ct = pd.DataFrame(row.fetchall(), columns=row.keys())
    area_code = area_code_ct['area_code'][0]
    pg_conn.close()
    return area_code


def parse_data_from_104(location, position, ro=1, isnew=7):
    area_code = get_area_code(location)
    # full-time: ro = 1
    # updated in 7 days: isnew = 7
    url = "https://www.104.com.tw/jobs/search/?ro={}&isnew={}&kwop=7&keyword={}&area={}&jobsource=2018indexpoc&ro=0".format(ro, isnew, position, area_code)
    htmlFile = requests.get(url)
    ObjSoup = bs4.BeautifulSoup(htmlFile.text, 'html.parser')
    jobs = ObjSoup.find_all('article', class_='js-job-item')
    jobs_info = []
    for j in jobs:
        title = j.find('a', class_="js-job-link").text
        company = j.get('data-cust-name')
        locate = j.find('ul', class_='job-list-intro').find('li').text
        salary = j.find('span',class_='b-tag--default').text
        website = j.find('a').get('href')
        info = 'title: {}\ncompany: {}\nlocation: {}\nsalary: {}\nwebsite: https:{}'.format(title, company, locate, salary, website)
        print(info)
        jobs_info.append(info)
    # print(jobs_info)


if __name__ == "__main__":
    parse_data_from_104('台南', "資料工程")
