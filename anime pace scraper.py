import requests
from bs4 import BeautifulSoup as bs

class scraper:
    def __init__(self,url):
        self.orig_url = url
        self.host = url.split('/')[2]
        self.anime = url.split('/')[-2]
        
    def animepace_downloadpage(self):
        with requests.session() as client:
            client.post('https://www3.animepace.si/user/login', data={'email':"bnb35317@cuoly.com",
                                                                      'password':"origami",
                                                                      'submit':"login",})

            response=client.get(self.orig_url).text
            soup=bs(response, 'html.parser')
            servers = soup.find_all('iframe')[-1]['src'] #gets the iframe of downloadlinks after login
        return servers
    
    @staticmethod
    def get_animopace(x):
        soup = bs(requests.get(x).content, 'html.parser')
        option_list = []
        for j, i in enumerate(soup.find_all('option')):
            print(j, i.text)
            option_list += [i['value']]
        opt = int(input('Enter server number: '))
        return option_list[opt]
    
    # sample url returned is like https://haloani.ru/Theta-Original-v4/d.php?q=f7ynJF1F1beE-b0beC4UUk_2j3EeFojNSJD90rofQIg    
    def get_server_link(self):
        return scraper.get_animopace(scraper.animepace_downloadpage(self))
    
    # I cannot figure out kissanimeX please help
    @staticmethod
    def get_final_links(link):
        # uncomment this if you want to see kissanimeX content
#        soup = bs(requests.get(link).text , 'html.parser')
#        encoded = soup.find('div', class_="row").script
#        print(encoded)
        soup = bs(requests.get(link).text, 'html.parser')
        links = soup.find('a', rel="nofollow")
        print(links['href'])
        
if __name__=='__main__'  :  
    a = scraper('https://www3.animepace.si/anime/uzaki-chan-wa-asobitai-dub/episode-06')
    print(a.host)
    if a.host == 'www3.animepace.si' :
        serverlink = a.get_server_link()
        print(serverlink)
#        this is where the problem starts
        scraper.get_final_links(serverlink)