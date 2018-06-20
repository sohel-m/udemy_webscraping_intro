from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent

ua = UserAgent()
header = {'user-agent':ua.chrome}
url = "https://boston.craigslist.org/search/sof"

response=requests.get(url,headers=header)
if response.status_code == 200:
    source = response.text
    soup = BeautifulSoup(source,'html.parser')
    a_tags= soup.find_all('a',class_="result-title hdrlnk")
    for tag in a_tags:
        print("Job:",tag.string)
        print("URL:",tag['href'])
