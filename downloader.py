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
        episodes.insert(1,link['href'])
    return episodes

# get vidstreaming streaming window links
def getDownloadLinks():
    links=["0"]
    episodes = getAllepisodes()
    for episode in episodes:
        if episode == "0":
            continue
        print(episode)
        url = baseurl + episode
        soup = connection(url)
        iframeLink = "https:"+soup.find('iframe').attrs['src'] # search iframe
        print(iframeLink)
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
        if len(videoQualityList) > 1:
            for j in range(len(videoQualityList)):
                if videoQualityList[j]['label'] == "Auto":
                    videoQualityList.remove(videoQualityList[j])
                    break

        print(i," => ",videoQualityList)
        finalLinks.append(videoQualityList)
    driver.close()
    return finalLinks

# download finally
def download(downloadLinks):
    dir_name = makeFolder()
    print("here")
    for i in range(1,len(downloadLinks)):
        filename=""
        episode = downloadLinks[i]
        try:
            for j in range(len(episode)): ## incomplete
                status = False  # to check if the download is done or not
                file = episode[j]['file']
                quality = episode[j]['label']
                site = requests.get(file,stream=True)
                filename = dir_name +  r"\Episode-" + str(i) + quality +".mp4"
                print(site.headers) ## size in bytes
                print("download started")
                with open(filename, 'wb') as f: 
                    for chunk in site.iter_content(chunk_size = 1024*1024): 
                        if chunk: 
                            f.write(chunk)
                print("Episode-",i," downloaded successfully !!\n")
                if status == True:  ## incomplete
                    break
        except Exception:
            print("**ERROR OCCURED IN EPISODE- **",i)
            print(Exception)

def makeFolder():
    parent_dir = r''
    path = os.path.join(parent_dir, anime) 
    try: 
        os.makedirs(path, exist_ok = True) 
        print("Folder '%s' created successfully" % anime) 
    except OSError as error: 
        print("Folder '%s' can not be created" % anime,"\n",error)
    return path 

if __name__ == "__main__": 
    links = realDownloadLinks()
    print("links")
    download(links)
