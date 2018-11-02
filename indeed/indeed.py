# Import packages 
import requests
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
#import warnings
#warnings.filterwarnings("ignore")

################################## FILTERS #########################################
#List of words to avoid in job title
red_flags = ["senior","manager","director","sr","lead","head","vp","chief","vice president"] 
#required = ["software"] #Can also check for required words

def qualifies(title):
    title = title.lower()
    #Define a function to check if a job title is worth checking out  
    for word in red_flags:
        if word in title: return False
    return True
   
    
# Now define the Regex, 
# 1. Should not have the phrase 1+ years, 1-2 Years, so on..
p1 = re.compile('[2-9]\s*\+?-?\s*[2-9]?\s*[yY]e?a?[rR][Ss]?')
# 2. Should not have mention of "doctor", "doctoral", so on..
p2 = re.compile('[Dd]octor?(al)?')

t1 = p1.search("2+ Years of experiencce")
t2 = p1.search("0-1 Year")

################################## MAIN #########################################
start_time = time.clock()

url_template = "http://www.indeed.com/jobs?q={}&l={}&start={}"
max_results_per_city = 500 # Set this to a high-value (5000) to generate more results. 

job_set = ['data+scientist','data+analyst','quantitative+research',
           'quantitative+research+analyst']

cities=['New+York','Brooklyn','Long+Island','Mechanicsburg', 'Harrisburg','Carlisle',
      'Anaheim','Brea','Buena+Park','Costa+Mesa','Cypress','Dana+Point',
      'Fountain+Valley','Fullerton','Garden+Grove','Westminster','Huntington+Beach','Irvine',
      'La+Habra','La+Palma','Laguna+Beach','Laguna+Hills','Laguna+Niguel','Laguna+Woods',
      'Lake+Forest','Los+Alamitos','Orange','Santa+Ana','Seal+Beach','Stanton',
      'Los+Angeles', 'San+Diego','Fresno', 'Long+Beach','Sacramento', 'Oakland',
        'San+Francisco', 'San+Jose',  
        'Washington%2C+DC']
columns = ['city_key', 'Title', 'Company', 'Location', 'Summary', 'Salary']



# Crawling more results, will also take much longer. First test your code on a small number of results and then expand.
i = 0
results = []
df_more = pd.DataFrame(columns=columns)
for city in set(cities):
    for start in range(0, max_results_per_city, 10):
        #print(city+" pg"+str(start/10.)) #to keep track of progress
        # Grab the results from the request (as above)
        url = url_template.format(job_set,city, start)
        # Append to the full set of results
        html = requests.get(url)
        time.sleep(1)
        soup = BeautifulSoup(html.content, 'html.parser', from_encoding="utf-8")
        for each in soup.find_all(class_= "result" ):
            #try:
            #    city=city
            #except:
            #    city = ''
            try: 
                title = each.find(class_='jobtitle').text.replace('\n', '')
            except:
                title = ''
            try:
                location = each.find('span', {'class':"location" }).text.replace('\n', '')
            except:
                location = ''
            try: 
                company = each.find(class_='company').text.replace('\n', '')
            except:
                company = ''
            try:
                salary = each.find('span', {'class':'no-wrap'}).text.strip()
            except:
                salary = ''
            try:
                summary = each.find('span', {'class':'summary'}).text.replace('\n', '')
            except:
                synopsis = ''
            try:
                link = 'http://www.indeed.com'+each.find('a').get('href')
            except:
                link = ''
            try:
                easyapply= each.find(name='span', attrs={'class':'iaLabel'}).text.strip()
            except:
                easyapply= ''
            if(qualifies(title.lower())):
                m = p1.search(summary)
                n = p2.search(summary)
                if not m and not n:
                    df_more = df_more.append({'Title':title,'Company':company, 'Location':location,'Summary':summary,'Salary':salary,'link':link,'easyapply':easyapply}, ignore_index=True)
            i += 1
            if i % 1000 == 0: 
                print('You have ' + str(i) + ' results.')
print('You have total '+str(df_more.shape[0])+ ' jobs. ' +str(df_more.dropna().drop_duplicates().shape[0]) + " of these aren't rubbish.")
print('Execution time is: %s seconds'%(time.clock() - start_time))
df_more.to_csv('Indeed_not_cleaned_.csv', encoding='utf-8',index=False,index_label=False)
