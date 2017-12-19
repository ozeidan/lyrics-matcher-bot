import requests
from bs4 import BeautifulSoup


class LyricsResolver:
    base_url = "http://api.genius.com"
    page_url = "http://genius.com"
    headers = None

    def __init__(self, apikey):
        self.headers = {
            'Authorization':
            'Bearer ' + apikey
        }

    def find_lyrics_by_fragment(self, lyrics):
        search_url = self.base_url + "/search"
        params = {'q': lyrics}
        response = requests.get(
            search_url, params=params, headers=self.headers)

        json = response.json()
        hits = json["response"]["hits"]

        if len(hits) != 0:
            song_path = hits[0]["result"]["path"]
            return self.__lyrics_from_song_api_path__(song_path)

        return None

    # See https://bigishdata.com/2016/09/27/
    # getting-song-lyrics-from-geniuss-api-scraping/
    def __lyrics_from_song_api_path__(self, song_path):
        # gotta go regular html scraping... come on Genius
        page_url = self.page_url + song_path
        page = requests.get(page_url)
        html = BeautifulSoup(page.text, "html.parser")
        # remove script tags that they put in the middle of the lyrics
        [h.extract() for h in html('script')]
        # at least Genius is nice and has a tag called 'lyrics'!
        # updated css where the lyrics are based in HTML
        lyrics = html.find("div", class_="lyrics").get_text()
        return lyrics
