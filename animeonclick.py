import requests 
from bs4 import BeautifulSoup 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from sys import exit
import os
from progress.bar import IncrementalBar

# null = open(os.devnull,'wb')
# sys.stderr = null
baseurl = "https://vidstreaming.io/"
episodes=["0"]
#chromedriverLoc = str(r'\Desktop\AnimeDownloader\chromedriver.exe')


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
        #print(e)
        exit()

# get the episode list ...
def getAllepisodes(url):
    soup = connection(url)
    try:
        episodeUL = (soup.find('h3', class_="list_episdoe")).find_next('ul').findAll("a")
    except Exception:
        print("Something was not right\n")
        exit()
    for link in episodeUL:
        episodes.insert(1,link['href'])
    return episodes

# get vidstreaming streaming window links
def getDownloadLinks(url):
    links=["0"]
    episodes = getAllepisodes(url)
    for episode in episodes:
        if episode == "0":
            continue
        print("Found ",(episode.split("/"))[-1])
        epi_url = baseurl + episode
        soup = connection(epi_url)
        iframeLink = "https:"+soup.find('iframe').attrs['src'] # search iframe
        #print(iframeLink)
        links.append(iframeLink)
    return links

# get final download links ... 
def realDownloadLinks(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--window-size=1024x1400")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    sites_of_links = getDownloadLinks(url)
    print("Preparing Download . . . Wait . . this might take time \n")
    finalLinks=["0"]
    for i in range(1,len(sites_of_links)):
        try:
            driver.set_page_load_timeout(10)
            driver.get(sites_of_links[i])
        except Exception:
            pass
        videoQualityList = driver.execute_script('return playerInstance.getPlaylist()[0].allSources')
        print("Links found episode",i)
        finalLinks.append(videoQualityList) # list of all episodes with all qualities
    driver.close()
    return finalLinks

def qualityFilter(links):
    qualityContent=["0"]
    for qualities in links:
        if qualities=='0':
            continue
        good = []
        for j in range(len(qualities)):
            if qualities[j]['label'] not in ['Auto','360 P','hls P']:
                good.append(qualities[j])

        if good != []:
            qualityContent.append(good)
        else :
            qualityContent.append("0")
    print("Done filtering episodes")
    return qualityContent

# download finally
def download(downloadLinks,start_url):
    dir_name = makeFolder(getanimename(start_url))
    for i in range(1,len(downloadLinks)):
        filename=""
        if downloadLinks[i] == "0":
            print("Episode",i,"Only Trash Quality available")
            continue

        episode = downloadLinks[i]
        try:
            for j in range(len(episode)):
                status = False  # to check if the download is done or not
                file = episode[j]['file']
                quality = (episode[j]['label']).replace(" ", "")
                site = requests.get(file,stream=True)
                filename = dir_name +  r"\Episode-" + str(i) + "-"+quality +".mp4"
                filesize = int(site.headers['Content-Length'])
                if os.path.exists(filename) and os.stat(filename).st_size == filesize :
                    print( "Episode-"+str(i)+"-",str(quality)+".mp4 already exsists")
                    break
                print("\nEpisode ",str(i),"\nFilesize",round(filesize/(1024*1024),2) ,"MB\n",quality) ## size in bytes
                #with tqdm(total=(filesize/(1024*1024)),unit='MB') as pbar:
                chunksize = int((1024*1024)/2)
                with IncrementalBar(message="Downloading ",max=(filesize/chunksize),suffix='%(percent).1f%% - Time left %(eta_td)s') as bar:
                    with open(filename, 'wb') as f: 
                        for chunk in site.iter_content(chunk_size = chunksize):
                            if chunk: 
                                f.write(chunk)
                                bar.next()
    
                if os.stat(filename).st_size in range(filesize-10,filesize+10):
                    status = True
                else :
                    print("Couldn't download at ",quality," ;( \n")
                if status == True: 
                    print("Episode-",i," downloaded successfully !!  :)\n")
                    break
        except Exception as e:
            print("****ERROR OCCURED IN EPISODE-",i,"****")
            print(e,"\n")

def makeFolder(anime):
    parent_dir = r''
    path = os.path.join(parent_dir, anime) 
    try: 
        os.makedirs(path, exist_ok = True) 
        print("Folder '%s' created successfully" % anime) 
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
    print(" ** Follow the link >>>> ",baseurl,"\n ** Search the anime\n ** Copy the url and paste below")
    start_url = input()
    if checkurl(start_url):
        links0 = realDownloadLinks(start_url)
        links1 = qualityFilter(links0)
        download(links1,start_url)
    else :
        print("Invalid URL")
    


if __name__ == "__main__":
    main()

