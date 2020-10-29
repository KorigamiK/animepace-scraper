import requests
from bs4 import BeautifulSoup as bs
import base64
import subprocess
import os

class scraper:    
    def __init__(self,url):
        self.orig_url = url
        self.host = url.split('/')[2]
        self.anime = url.split('/')[-2]
        self.final_dow_urls = []#new downloads will be appended to this i.e. url(s)
        self.name = url.split('/')[url.split('/').index('anime')+1].replace("-"," ").capitalize()
        
    def animepace_get_servers(self):
        data={'email':"bnb35317@cuoly.com",
              'password':"origami",
              'submit':"login",}        
        with requests.session() as client:
            client.post('https://www3.animepace.si/user/login', data=data)
            response=client.get(self.orig_url).text
            soup=bs(response, 'html.parser')
            servers = soup.find_all('iframe')[-1]['src'] #gets the iframe of downloadlinks after login
        return servers
    
    def get_animopace(self, x):
        soup = bs(requests.get(x).content, 'html.parser')
        option_list = [] # link to all servers
        flag = True
        
        for j, i in enumerate(soup.find_all('option')):
            try:
                self.server
                flag = False
            except:
                print(j, i.text)                
            option_list += [i['value']]
            
        if len(option_list) == 0:
            print('No downloads availible')
            return None
        
        if flag == True:
            opt = int(input('Enter server number: '))
            setattr(self, 'server', opt)
            
        return option_list[self.server]
    
    # sample server url returned is like https://haloani.ru/Theta-Original-v4/d.php?q=f7ynJF1F1beE-b0beC4UUk_2j3EeFojNSJD90rofQIg    
    def get_server_link(self):
        return scraper.get_animopace(self, scraper.animepace_get_servers(self))
    
    @staticmethod
    def download(x):
        query="""wget --header="Referer: https://haloani.ru" "{}" --no-check-certificate """.format(x)
        print(query)
        subprocess.run(query,shell=True)
    
    # Thank you Arjix for helping me figure out this
    def get_final_links(self,link): #link here is for server
        html = requests.get(link).text
        soup = bs(html, "html.parser")
        script = soup.select("script")
        for i in script:
            if "document.write" in str(i):
                try:
                    script = (
                        str(i).replace('atob', 'Base64.decode')
                        .split('javascript">')[1]
                        .split("</script>")[0]
                        .split('document.write(Base64.decode("')[1]
                        .split('"));')[0]
                    )
               # Need to work on kickassaimev2srever
#                    script = (
#                        str(i).replace('atob', 'Base64.decode')
#                        .split('t>')[1]
#                        .split("</script>")[0]
#                        .split('document.write(Base64.decode("')[1]
#                        .split('"));')[0]
#                    )
                except:
                    print('That server is not supported at the moment')
                    return None
        data = base64.b64decode(script)
        print(data)
        soup = bs(data.decode("utf-8"), "html.parser")
        flag = True
        dow_urls_allqualities = []
        for j,i in enumerate(soup.find_all('a')):
            try:
                self.quality
                flag = False
            except:
                print(j, i.text)
                
            dow_urls_allqualities += [str(''.join(i['href']))]
            
        if flag == True:
            setattr(self, 'quality', int(input('enter quality number')))
            
        self.final_dow_urls += [dow_urls_allqualities[self.quality]] #I dunno why but beautifulsoup4 need to be converted to list and then they behave as strings? 
        
if __name__=='__main__'  :  
    a = scraper('https://www3.animepace.si/anime/boruto-naruto-next-generations/episode-92')
    print(a.name)
    if a.host == 'www3.animepace.si' :
        serverlink = a.get_server_link()
        print(serverlink)
#        this is where the problem starts
        a.get_final_links(serverlink) # check for qualities and set the quality desired
        scraper.download(a.final_dow_urls[0])

