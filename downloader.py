import requests 
from bs4 import BeautifulSoup 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import os

baseurl = ""
start_url = ""
temp = start_url.split("/")
temp = start_url.split("/")
endInd = temp[-1].find("-episode")
anime = temp[-1][0:endInd]
episodes=["0"]

def connection(url):
    site = requests.get(url) 
    soup = BeautifulSoup(site.content,'html5lib')
    return soup

# get the episode list ...
def getAllepisodes():
    soup = connection(start_url)
    episodeUL = (soup.find('h3', class_="list_episdoe")).find_next('ul').findAll("a")
    #print(episodeUL)
    for link in episodeUL:
        #print(link['href'])
        episodes.append(link['href'])
    return episodes

# get vidstreaming streaming window links
def getDownloadLinks():
    links=["0"]
    episodes = getAllepisodes()
    for episode in episodes:
        if episode == "0":
            continue
        url = baseurl + episode
        soup = connection(url)
        iframeLink = "https:"+soup.find('iframe').attrs['src'] # search iframe
        #print(iframeLink)
        links.append(iframeLink)
    return links

# get final download links ... 
def realDownloadLinks():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1024x1400")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    sites_of_links = getDownloadLinks()
    finalLinks=["0"]
    for i in range(1,len(sites_of_links)):
        driver.implicitly_wait(1)
        driver.get(sites_of_links[i])
        videoQualityList = driver.execute_script('return playerInstance.getPlaylist()[0].allSources')
        print(i," => ",videoQualityList[0]['file'])
        finalLinks.append(videoQualityList[0]['file'])
    driver.close()
    return finalLinks

# download finally
def download(downloadLinks):
    dir_name = makeFolder()
    print("here")
    for i in range(1,len(downloadLinks)):
        filename=""
        try:
            site = requests.get(downloadLinks[i],stream=True)
            filename = dir_name +  r"\Episode-" + str(i) + ".mp4"
            print(filename)
            print("download started")
            with open(filename, 'wb') as f: 
                for chunk in site.iter_content(chunk_size = 1024*1024): 
                    if chunk: 
                        f.write(chunk)
            print("Episode-",i," downloaded successfully !!\n")
        except Exception:
            print("**ERROR OCCURED IN EPISODE- **",i)
            print(Exception)

def makeFolder():
    parent_dir = ''
    path = os.path.join(parent_dir, anime) 
    try: 
        os.makedirs(path, exist_ok = True) 
        print("Directory '%s' created successfully" % anime) 
    except OSError as error: 
        print("Directory '%s' can not be created" % anime,"\n",error)
    return path 

if __name__ == "__main__": 
    links = realDownloadLinks()
    print("links")
    download(links)
