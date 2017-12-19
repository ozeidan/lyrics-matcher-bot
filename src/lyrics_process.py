from fuzzywuzzy import process


def extract_lines(lyrics, partial_lyrics):
    lyrics = lyrics.split('\n')
    lyrics = [x for x in lyrics if len(x) > 0 and x[0] != "["]

    best_match, confidence = process.extractOne(partial_lyrics, lyrics)

    if(confidence < 90):
        return None

    lyrics_index = lyrics.index(best_match)

    return [lyrics[lyrics_index], lyrics[lyrics_index + 1]]
