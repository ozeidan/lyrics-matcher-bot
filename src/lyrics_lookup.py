import requests
from fuzzywuzzy import process
from bs4 import BeautifulSoup
import threading

CONFIDENCE_THRESHOLD = 95
base_url = "http://api.genius.com"
page_url = "http://genius.com"


class LyricsResolver:
    snippet_queue = None
    lyrics_queue = None

    def __init__(self, apikey):
        self.headers = {
            'Authorization':
            'Bearer ' + apikey
        }
        self.thread = threading.Thread(target=self.__main_loop)

    def start(self):
        self.thread.start()

    def stop(self):
        self.thread.stop()

    def __main_loop(self):
        while True:
            (snippet, comment) = LyricsResolver.snippet_queue.get()
            print("Fetching lyrics for comment by {}".format(
                comment.author.name))

            lyrics_obj = self.__find_lyrics_by_snippet(snippet)

            if lyrics_obj is None:
                print("Found no matching lyrics for comment by {}".format(
                    comment.author.name))
                continue

            (song_title, lyrics) = lyrics_obj
            matching_obj = LyricsResolver.__extract_matching_line(lyrics,
                                                                  snippet)

            if matching_obj is None:
                print("Found good line for this comment")
                continue

            (matching_line, confidence) = matching_obj

            print("Comment by {}: found song {} with confidence {}".format(
                  comment.author,
                  song_title,
                  confidence))

            print("Last line of commenter: {}".format(snippet))
            print("Matching line: {}".format(matching_line))

            if(confidence < CONFIDENCE_THRESHOLD):
                print("Confidence too low")
                continue

            LyricsResolver.lyrics_queue.put(
                (matching_line, comment))

    def __find_lyrics_by_snippet(self, lyrics):
        search_url = base_url + "/search"
        params = {'q': lyrics}
        response = requests.get(
            search_url, params=params, headers=self.headers)

        json = response.json()
        hits = json["response"]["hits"]

        if len(hits) != 0:
            song = hits[0]["result"]
            song_path = song["path"]
            full_title = song["full_title"]
            return (full_title,
                    LyricsResolver.__rip_lyrics_from_genius(song_path))
        else:
            return None

        # See https://bigishdata.com/2016/09/27/
        # getting-song-lyrics-from-geniuss-api-scraping/
    def __rip_lyrics_from_genius(song_path):
        # gotta go regular html scraping... come on Genius
        target_url = page_url + song_path
        page = requests.get(target_url)
        html = BeautifulSoup(page.text, "html.parser")
        # remove script tags that they put in the middle of the lyrics
        [h.extract() for h in html('script')]
        # at least Genius is nice and has a tag called 'lyrics'!
        # updated css where the lyrics are based in HTML
        lyrics = html.find("div", class_="lyrics").get_text()
        return lyrics

    def __extract_matching_line(lyrics, partial_lyrics):
        lyrics = lyrics.split('\n')
        lyrics = [x for x in lyrics if len(x) > 0 and x[0] != "["]

        best_match, confidence = process.extractOne(partial_lyrics, lyrics)

        lyrics_index = lyrics.index(best_match)

        if(len(lyrics) < lyrics_index + 2):
            return None

        return (lyrics[lyrics_index + 1], confidence)
