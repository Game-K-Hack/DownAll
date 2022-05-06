import requests
import fake_useragent
from bs4 import BeautifulSoup

class vostfree():
    def __init__(self) -> None:
        self.url = "https://vostfree.tv"
        self.user_agent = fake_useragent.UserAgent().firefox
        self.headers = {
            'User-Agent': self.user_agent, 
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3', 
            'Accept-Encoding': 'gzip, deflate, br', 
            'Referer': self.url, 
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    def search(self, name: str) -> list:
        data = f"do=search&subaction=search&story={name}&submit=Envoyer"
        headers = self.headers
        headers['Content-Length'] = str(len(data))
        r = requests.post(self.url, headers=headers, data=data)
        soup = BeautifulSoup(r.text, 'html.parser')
        lenght = soup.find('div', class_='berrors').text
        s = lenght.index('InformationTrouvé ') + len('InformationTrouvé ')
        e = lenght.index(' réponses', s)
        self.lenght = int(lenght[s:e])
        ListeAllAnime = []

        for elm in soup.find_all('div', class_='search-result'):
            TempDict = {}

            title = elm.find('div', class_='title')
            language = elm.find('div', class_='quality').text
            TempDict['title'] = title.text.replace(' FRENCH' if language == 'VF' else 'VOSTFR', '')
            TempDict['link'] = title.find('a').get('href')
            TempDict['language'] = language
            TempDict['image'] = self.url + elm.find('span', class_='image').img.get('src')
            info = elm.find('div', class_='info')
            TempDict['short-resume'] = elm.find('div', class_='desc').text
            addinfo = info.find('ul', class_='additional')
            TempDict['genre'] = [(i.text, i.get('href')) for i in addinfo.find_all('li', class_='type')[0].find_all('a')]
            s = str(addinfo).index('<span>Réalisateur:</span>') + len('<span>Réalisateur:</span>')
            e = str(addinfo).index('</li>', s)
            TempDict['realisator'] = str(addinfo)[s:e].strip()
            s = str(addinfo).index('<span>Durée:</span>') + len('<span>Durée:</span>')
            e = str(addinfo).index('</li>', s)
            TempDict['time'] = str(addinfo)[s:e].strip()
            s = str(addinfo).index('<span>Anneé:</span>') + len('<span>Anneé:</span>')
            e = str(addinfo).index('</li>', s)
            addinfo = str(addinfo)[s:e].strip()
            s1 = addinfo.index('href="') + len('href="')
            e1 = addinfo.index('">', s1)
            s2 = addinfo.index('href="' + addinfo[s1:e1] + '">') + len('href="' + addinfo[s1:e1] + '">')
            e2 = addinfo.index('</a>', s2)
            TempDict['year'] = (addinfo[s2:e2], addinfo[s1:e1])

            ListeAllAnime.append(TempDict)

        return ListeAllAnime

    def url2episode(self, url) -> dict:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        ListeAllEpisode = {}

        for cloud in ['1fichier', 'uptobox']:
            ListeAllEpisode[cloud] = {}
            for quality in ['HD 720p', 'FHD 1080p']:
                ListeAllEpisode[cloud][quality] = []

        for cloud in soup.find('div', class_='tab-blocks').find_all('div', class_='tab-content')[1:]:
            for quality in cloud.find('div', class_='home-episode').find_all('div', class_='block'):
                q = quality.find_all('div', class_='lien-episode')[0].find('div', class_='alt').find('b').text
                for episode in quality.find_all('div', class_='lien-episode'): 
                    try: ListeAllEpisode[episode.find('a').get('href').split('//')[1].split('.')[0]][q].append((episode.find('div', class_='year2').find('b').text, episode.find('a').get('href')))
                    except: pass

        return ListeAllEpisode

class skidrowreloaded():
    def __init__(self) -> None:
        self.url = "https://www.skidrowreloaded.com"

    def search(self, name, page=-1) -> list:
        # Request the page
        r = requests.get(f'{self.url}{f"/page/{page}/" if page != -1 else "/"}?s={name.replace(" ", "+").lower()}&x=0&y=0')
        soup = BeautifulSoup(r.text, 'html.parser')
        ListeAllGames = []
        liste = soup.select('div[id="overall-container"] div[id="main-content"] div')
        # For all games on the page
        for i in liste[1:]:
            try:
                element = i.find('div', class_='post-excerpt').find_all('p')
                tag = [i.strip() for i in element[1].text.split('–')]
                ListeAllGames.append({
                    'title': i.find('h2').text,
                    'url': i.find('a').get('href'),
                    'post_date': i.find('div', class_='meta').text.split('in')[0].strip().replace('Posted ', ''),
                    'image': element[0].find('img').get('data-lazy-src'),
                    'tag': tag,
                    'crack_name': tag[0],
                    'short_resume': element[2].text})                
            except: pass
        # Add number of games found
        number_search = int(liste[0].find('h2').text.split(' ')[0])
        ListeAllGames.append({'lenght': number_search})
        # Return the list of all games
        return ListeAllGames

    def url2game(self, url) -> dict:
        # Request the page
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Get the game informations
        s = str(soup).index('<h5>ABOUT THE GAME</h5>') + len('<h5>ABOUT THE GAME</h5>')
        e = str(soup).index('</a></p>', s)
        desc = BeautifulSoup(str(soup)[s:e], 'html.parser')
        info = {elm.split(': ')[0].lower() : ': '.join(elm.split(': ')[1:]) for elm in desc.find_all('p')[1].text.split('\n')}
        try: info['Genre'] = info['Genre'].split(', ')
        except: pass
        # Get size of the game
        sizetitle = [elm.text for elm in soup.find_all('p') if '\nSize: ' in elm.text][0]
        s = sizetitle.index('\nSize: ') + len('\nSize: ')
        e = sizetitle.index('\n', s)
        size = sizetitle[s:e]
        # Get the game direct download links
        try:
            s = str(soup).index('<strong>ONE FTP LINK</strong>') + len('<strong>ONE FTP LINK</strong>')
            e = str(soup).index('<strong>TORRENT</strong>', s)
            directlink = BeautifulSoup(str(soup)[s:e], 'html.parser')
        except:
            s = str(soup).index('<strong>FTP LINK</strong>') + len('<strong>FTP LINK</strong>')
            e = str(soup).index('<strong>TORRENT</strong>', s)
            directlink = BeautifulSoup(str(soup)[s:e], 'html.parser')
        # Get the game torrent download links
        s = str(soup).index('<strong>TORRENT</strong>') + len('<strong>TORRENT</strong>')
        e = str(soup).index('<p>Enjoy</p>', s)
        torrentlink = BeautifulSoup(str(soup)[s:e], 'html.parser')
        # Create the game dictionary
        game = {
            'title-original': sizetitle.split('\n')[0],
            'image': soup.find('img', class_='lazy lazy-hidden aligncenter').get('data-lazy-src'),
            'description': desc.find_all('p')[0].text,
            'link-original': desc.find('a').get('href') if desc.find('a').get('href') != self.url else None,
            'size': size}
        # Sort the data in the game dictionary
        for k in info: game[k] = info[k]
        # Add all links to the game dictionary
        game['link-download-direct'] = {'.'.join('://'.join(elm.get('href').split('://')[1:]).split('/')[0].split('.')[:-1]):elm.get('href') for elm in directlink.find_all('a') if elm.get('href') != self.url}
        game['link-download-torrent'] = {'.'.join('://'.join(elm.get('href').split('://')[1:]).split('/')[0].split('.')[:-1]):elm.get('href') for elm in torrentlink.find_all('a') if elm.get('href') != self.url}
        # Return the game dictionary
        return game