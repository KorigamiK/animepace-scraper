import requests
from bs4 import BeautifulSoup as bs
import base64
import subprocess
import re
import csv
# import os # will add ability to set download location
from tabulate import tabulate


class scraper:
    def __init__(self, url):
        self.orig_url = url
        self.host = url.split('/')[2]
        self.anime = url.split('/')[-2]
        self.final_dow_urls = []  # new downloads will be appended to this i.e. url(s)
        self.options = []  # carries the options to download final_dow_urls
        self.name = url.split('/')[url.split('/').index('anime') + 1].replace("-", " ").capitalize()

    @property
    def episode(self):
        return self.orig_url.split('/')[-1]

    def animepace_get_servers(self):
        data = {'email': "bnb35317@cuoly.com",
                'password': "origami",
                'submit': "login", }
        with requests.session() as client:
            client.post('https://www3.animepace.si/user/login', data=data)
            response = client.get(self.orig_url).text
            soup = bs(response, 'html.parser')
            servers = soup.find_all('iframe')[-1]['src']  # gets the iframe of downloadlinks after login
        return servers

    def get_animopace(self, x):
        soup = bs(requests.get(x).content, 'html.parser')
        option_list = []  # link to all servers
        flag = True

        servers = [["ser num", "server"]]
        for j, i in enumerate(soup.find_all('option')):
            try:
                self.server_opt
                flag = False
            except:
                servers.append([j, i.text])
            option_list += [i['value']]

        if len(option_list) == 0:
            print('No downloads availible')
            return None

        if flag == True:
            print(tabulate(servers, headers="firstrow"))
            opt = int(input('Enter server number: '))
            setattr(self, 'server_opt', opt)

        if self.server_opt == 'downloader':
            return option_list
        else:
            return option_list[self.server_opt]

    # sample SERVER url returned is like https://haloani.ru/Theta-Original-v4/d.php?q=f7ynJF1F1beE-b0beC4UUk_2j3EeFojNSJD90rofQIg    
    def get_server_link(self):
        r = scraper.get_animopace(self, scraper.animepace_get_servers(self))
        if r:
            return r
        else:
            print(f"{self.episode} not available. It will be skipped")
            return [None]  # because we iterate through it

    def _kickassanimex(self, link):
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
                except Exception as e:
                    print('Something went wrong with the server', e)
                    return None
        data = base64.b64decode(script)
        soup = bs(data.decode("utf-8"), "html.parser")

        flag = True
        dow_urls_allqualities = []
        for j, i in enumerate(soup.find_all('a')):
            try:
                self.quality
                flag = False
            except:
                print(j, i.text)
            dow_urls_allqualities += [str(''.join(i['href']))]
        if flag == True:
            setattr(self, 'quality', int(input('Enter quality number: ')))
        self.final_dow_urls += [dow_urls_allqualities[
                                    self.quality]]  # I dunno why but beautifulsoup4 need to be converted to list and then they behave as strings?
        self.options += [
            '--header="Referer: https://haloani.ru"' + ' -O ' + (self.name + " " + self.episode + ".mp4").replace(" ",
                                                                                                                  "_")]

    def _kickassanimev2(self, link):
        html = requests.get(link).text
        soup = bs(html, "html.parser")
        script = soup.find('div', class_="text-center").select("script")[0]
        script = str(str(script).split('document.write(atob("')[1].split('"))</script>')[0])
        script += "=" * ((4 - len(script) % 4) % 4)  # ugh from stack exchange
        data = base64.b64decode(script)
        soup = bs(data.decode("utf-8"), "html.parser")
        flag = True
        dow_urls_allqualities = []
        for j, i in enumerate(soup.select('a')):
            try:
                self.quality
                flag = False
            except:
                print(j, i.text)
            dow_urls_allqualities += ['https://haloani.ru/Kickassanimev2/' + i['href']]

        if flag == True:
            setattr(self, 'quality', int(input('Enter quality number: ')))
        self.final_dow_urls += [dow_urls_allqualities[self.quality]]
        self.options += ['-O ' + (self.name + " " + self.episode + ".mp4").replace(" ", "_")]

    def _betaserver(self, link):
        html = requests.get(link).text
        soup = bs(html, "html.parser")
        dow_urls_allqualities = []
        flag = True
        for j, i in enumerate(soup.find_all('a', rel="nofollow")):
            try:
                self.quality
                flag = False
            except:
                print(j, i.text)
            dow_urls_allqualities += [i['href']]

        if flag == True:
            setattr(self, 'quality', int(input('Enter quality number: ')))
        self.final_dow_urls += [dow_urls_allqualities[self.quality]]
        self.options += [
            '--header="Referer: https://haloani.ru"' + ' -O ' + (self.name + " " + self.episode + ".mp4").replace(" ",
                                                                                                                  "_")]

    # Thank you Arjix for helping me figure out this
    def get_final_links(self, link):  # link here is for server
        server = link.split('https://haloani.ru')[1].split('/')[1]
        self.server = server
        if server == 'KickAssAnimeX':
            scraper._kickassanimex(self, link)

        elif server == 'Kickassanimev2':
            scraper._kickassanimev2(self, link)

        elif server == 'Theta-Original-v4':
            scraper._kickassanimex(self, link)
            self.options[-1] = '-O ' + (self.name + " " + self.episode + ".mp4").replace(" ", "_")

        elif server == 'Dr.Hoffmann':
            scraper._kickassanimex(self, link)
            self.options[-1] = '-O ' + (self.name + " " + self.episode + ".mp4").replace(" ", "_")

        elif server == 'Original-quality-v2':
            scraper._kickassanimev2(self, link)

        elif server == 'BetaServer3':
            scraper._betaserver(self, link)

        elif server == 'Beta-Server':
            scraper._kickassanimex(self, link)
        # betaserver1 doesn't work (no links)
        elif server == 'mobile-v2':
            scraper._betaserver(self, link)

        elif server == 'Theta-Original':
            scraper._kickassanimex(self, link)

        else:
            print('Not supported')
            print(self.server)
            return None

    @staticmethod
    def download(link, options):
        query = f"""wget "{link}" -q --show-progress --no-check-certificate {options}"""
        subprocess.run(query, shell=True)


class downloader:
    def __init__(self, url, start, end, opt='low'):
        self.mode = opt
        self.anime_url = url
        self.start = start
        self.end = end

    @property
    def fetch_episodes(self):
        for i in range(self.start, self.end + 1):
            if len(str(i)) <= 2:
                yield f"{self.anime_url}episode-{i:0>2d}"
            else:
                yield f"{self.anime_url}episode-{i}"

    priority = {'low': {'Kickassanimev2': 1, 'KickAssAnimeX': 3, 'Beta-Server': 1, 'BetaServer3': 2, 'mobile-v2': -1,
                        'Theta-Original': -1, }}

    def make_downloads(self):
        priority_list = list(downloader.priority[self.mode].keys())
        var = scraper(self.anime_url + "episode-04")
        var.server_opt = "downloader"
        f = self.start
        for i in self.fetch_episodes:
            toggle_no_new_episodes = False
            print(f'fetching {f}')
            f += 1
            var.orig_url = i
            serverlinks = var.get_server_link()  # only for "downloader" class it gives the whole list of servers
            pattern = r'(https:\/\/haloani.ru\/)([A-Za-z-1-9.]+)(\/[^=]+)'
            servers = []
            for k in serverlinks:
                if k:
                    servers += [re.search(pattern, k).group(2)]
                else:
                    print('skipping')
                    toggle_no_new_episodes = True
                    break
            if toggle_no_new_episodes:
                break
            else:
                pass
            flag = 10  # arbitrary large number
            for j, i in enumerate(servers):
                if i in priority_list:
                    print('yes')
                    if priority_list.index(i) < flag:
                        flag = priority_list.index(i)
                        needed_server = serverlinks[j]
                        var.quality = downloader.priority[self.mode][i]
                    else:
                        pass
                else:
                    print('no')
            try:
                print(re.search(pattern, needed_server).group(2))
                var.get_final_links(needed_server)
            except Exception as e:
                print('server/ quality not found, trying any available quality')
                print(e)
                var.quality = -1
                var.get_final_links(needed_server)
                continue
            print()
        with open("all_links.txt", "a") as file:
            write = csv.writer(file)
            write.writerows(list(zip(var.final_dow_urls, var.options)))
        if input("download now? y/n: ") == 'y':
            for url, opt in zip(var.final_dow_urls, var.options):
                scraper.download(url, opt)


class searcher:
    def __init__(self, search_input):
        self.query = search_input

    def _call_api(self):
        response = requests.post("https://www3.animepace.si/search", data={"keyword": self.query})
        return response.json()

    def print_search(self):  # also returns url
        links = []
        for j, i in enumerate(search_and_get._call_api()):
            print(j, i["name"])
            links.append(i["slug"])
        inp = int(input("Enter anime number: "))
        return f'https://www3.animepace.si/anime/{links[inp]}/'

    def download_from_search(self):
        var = downloader(self.print_search(), int(input("Enter start number: ")), int(input("Enter end number: ")))
        downloader.make_downloads(var)


if __name__ == '__main__':
    x = {1: "use code", 2: "use url and download", 3: "search and download"}
    for i, j in x.items():
        print(i, j)
    option_input = int(input("Enter option number"))
if option_input == 1:
    a = scraper('https://www3.animepace.si/anime/vinland-saga/episode-01')
    print(a.name)
    if a.host == 'www3.animepace.si':
        for i in range(19, 20):
            a.orig_url = "https://www3.animepace.si/anime/vinland-saga/episode-{}".format(i)
            serverlink = a.get_server_link()
            #             print(serverlink)
            a.get_final_links(serverlink)
    #     print(list(zip(a.final_dow_urls, a.options)))
    #     print(a.options)
    #     print(a.final_dow_urls)
    for url, opt in zip(a.final_dow_urls, a.options):
        scraper.download(url, opt)
elif option_input == 2:
    a = downloader(input("Enter anime url: "), int(input("Enter start number: ")), int(input("Enter end number: ")))
    downloader.make_downloads(a)
elif option_input == 3:
    search_and_get = searcher(input("Enter anime name: "))
    search_and_get.download_from_search()
else:
    print("not implemented yet.")
