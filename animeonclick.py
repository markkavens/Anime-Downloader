class Episode:
    number = 0
    siteLink = ""
    playerLink = ""
    downloadLinks = []

    def __init__(self,no):
        self.number = no
    def setSiteLink(self,url):
        self.siteLink = url
    def setPlayerLink(self,url):
        self.playerLink = url
    def setLinks(self,x):
        self.downloadLinks=x

##################################################
import requests 
from bs4 import BeautifulSoup 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from sys import exit
import os
from progress.bar import IncrementalBar

baseurl = "https://vidstreaming.io/"

def getanimename(start_url):
    temp = start_url.split("/")
    endInd = temp[-1].find("-episode")
    anime = temp[-1][0:endInd]
    return anime

def connection(url):
    try:
        site = requests.get(url) 
        soup = BeautifulSoup(site.content,'html5lib')
        return soup
    except Exception as e:
        print("Cannot reach site :( ")
        print(e)
        exit()

def tobedownloaded(url,l,r):
    ep = url.split('-')
    if int(ep[-1]) in range(l,r+1):
        return ep[-1]
    return -1

# get the episode list ...
def getAllepisodes(url,l,r):
    soup = connection(url)
    try:
        episodeUL = (soup.find('h3', class_="list_episdoe")).find_next('ul').findAll("a")
    except Exception:
        print("Something was not right :(")
        exit()
    episodes = []  # to be downloaded episodes
    for link in episodeUL:
        res = tobedownloaded(link['href'],l,r)
        if res!= -1 :
            ep = Episode(res)
            ep.setSiteLink(link['href'])
            episodes.insert(0,ep)
    return episodes

# get vidstreaming streaming player links
def getPlayerLinks(url,l,r):
    episodes = getAllepisodes(url,l,r)
    for episode in episodes:
        print("Found episode ", episode.number)
        epi_url = baseurl + episode.siteLink
        soup = connection(epi_url)
        iframeLink = "https:"+ soup.find('iframe').attrs['src'] # search iframe
        #print(iframeLink)
        episode.setPlayerLink(iframeLink)
    return episodes


# get final download links ... 
def realDownloadLinks(url,episodes):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    print("Preparing Download . . . Wait . . this might take time \n")
    for ep in episodes:
        try:
            driver.set_page_load_timeout(25)
            driver.get(ep.playerLink)
        except Exception as e:
            print(e)
            continue
        try:
            videoQualityList = driver.execute_script('return playerInstance.getPlaylist()[0].allSources')
            if len(videoQualityList) != 0:
                print("Links found episode",ep.number)
                x = []
                for j in range(len(videoQualityList)):
                    dct = {}
                    if qualityFilter(videoQualityList[j]['label']) == True :
                        dct['label'] = videoQualityList[j]['label']
                        dct['file'] = videoQualityList[j]['file']
                        x.append(dct)

            ep.setLinks(x)     # list of all episodes with all qualities
        except :
            print("Something unexpected occured in episode",ep.num)
            continue
    driver.close()


# download finally
def download(episodes,start_url):
    dir_name = makeFolder(getanimename(start_url))
    for ep in episodes:
        filename=""
        num = ep.number
        episode = ep.downloadLinks
        if episode == []:
            print("Episode",num,"Only Trash Quality available")
            continue

        try:
            for j in range(len(episode)):
                status = False  # to check if the download is done or not
                file = episode[j]['file']
                quality = (episode[j]['label']).replace(" ", "")
                site = requests.get(file,stream=True)
                filename = dir_name +  r"\Episode-" + str(num) + "-"+quality +".mp4"
                filesize = int(site.headers['Content-Length'])
                if os.path.exists(filename) :
                    print( "Episode-"+str(num)+"-",str(quality)+".mp4 already exsists")
                    break

                printInfo(str(num),round(filesize/(1024*1024),2),quality) 
                chunksize = int(1024*1024)  ## size in bytes
                with IncrementalBar(message="Downloading ",max=(filesize/chunksize),suffix='%(percent).1f%% - Time left %(eta_td)s') as bar:
                    with open(filename, 'wb') as f: 
                        for chunk in site.iter_content(chunk_size = chunksize):
                            if chunk: 
                                f.write(chunk)
                                bar.next()
    
                if os.stat(filename).st_size in range(filesize-100,filesize+100):
                    status = True
                else :
                    print("Couldn't download at ",quality," ;( \n")
                if status == True: 
                    print("Episode-",num," downloaded successfully !!  :)\n")
                    break
        except Exception as e:
            print("****ERROR OCCURED IN EPISODE-",num,"****")
            print(e,"\n")


def qualityFilter(label):
    if label not in ['Auto','240 P','144 P','hls P','SD P']:
        return True
    return False

def printInfo(no,size,quality):
    print("Episode : ",no)
    print("Size : ",size," MB")
    print("Quality : ",quality)


def makeFolder(anime):
    parent_dir = r''
    path = os.path.join(parent_dir, anime) 
    try: 
        os.makedirs(path, exist_ok = True) 
        print("Folder '%s' created successfully\n" % anime) 
    except OSError as error: 
        print("Folder '%s' can not be created" % anime,"\n",error)
    return path 

def checkurl(url):
    s = baseurl + 'videos/'
    r = url[:len(s)]
    if s == r :
        return True
    return False

def main():
    print("\n ** Curse Saransh Pushkar , if doesnt work **\n")
    print(" ** Follow the link >>>> ",baseurl,"\n ** Search the anime\n ** Copy the url and paste below :")
    start_url = input()
    if checkurl(start_url):
        print("")
        print(" ** from episode :",end=" ")
        l = int(input())
        print(" **  to  episode :",end=" ")
        r = int(input())
        print("")
        try:
            episodes = getPlayerLinks(start_url,l,r)
            realDownloadLinks(start_url,episodes)
            download(episodes,start_url)
        except Exception as e:
            print(e)
            print("Error")
    else :
        print("Invalid URL")
    

if __name__ == "__main__":
    main()
