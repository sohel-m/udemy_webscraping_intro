import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

user_agent = UserAgent()
main_url = 'http://codingbat.com/java'
page = requests.get(main_url,headers={'user-agent':user_agent.chrome})
soup = BeautifulSoup(page.content,'lxml')

base_url = 'http://codingbat.com'

all_divs = soup.find_all('div',class_='summ')
section_info = [i.text for i in all_divs]
section_links = [base_url + div.a['href'] for div in all_divs]

fp = open('codingbat_questions.txt','a+')       # file opened in append mode, no overwriting of data

for link,section_info in zip(section_links,section_info):

    fp.write('\n\n\n'+section_info +'\n\n')     # just to make text file more readable

    section_page = requests.get(link,headers={'user-agent':user_agent.chrome})
    section_soup = BeautifulSoup(section_page.content,'lxml')
    div = section_soup.find('div',class_='tabc')
    question_links=[base_url + td.a['href'] for td in div.table.find_all('td')]

    qno=1                                       # question no in each section should begin with 1

    for question_link in question_links:

        question_page = requests.get(question_link)
        question_soup = BeautifulSoup(question_page.content, 'lxml')
        indent_div = question_soup.find('div', attrs={'class':'indent'})

        problem_statement = ("Q%d). %s")%(qno,indent_div.table.div.text)

        siblings_of_statement = indent_div.table.div.next_siblings

        examples = [sibling for sibling in siblings_of_statement if sibling.string is not None]

        for example in examples:
            problem_statement+='\n'+example

        problem_statement+='\n\n\n'             # just to make text file more readable
        fp.write(problem_statement)

        qno+=1

fp.close()
