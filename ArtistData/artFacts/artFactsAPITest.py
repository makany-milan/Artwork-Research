import requests
from time import sleep


def getArtistData(artistLink):
    artistID = artistLink.split('/')[-1]
    fileName = artistID + '.json'

    sleep(2)
    r = requests.get(f'https://artfacts.net/api/v0/artists/{artistID}/spotlight')
    if r.status_code == 200:
        pass
    if r.status_code == 429:
        print(r.headers)
    else:
        print(r.status_code)
        return None

    return artistID

if __name__ == '__main__':
    artist = 'https://artfacts.net/artist/michael-zabel/450826'
    getArtistData(artist)