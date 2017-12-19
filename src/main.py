from reddit_bot import CommentBot
from lyrics_lookup import LyricsResolver, extract_lines

CONFIDENCE_THRESHOLD = 95
MIN_WORD_LENGTH = 5
MAX_WORD_LENGTH = 15


def main():
    global resolver
    global redditBot
    resolver = LyricsResolver(
        "jmHgM139pZPlGXIFf6IDOcezibtN5jPXV_DH56iGcW2ZW-1WKhbiroe_p5RLkfoY")

    redditBot = CommentBot(["kendricklamar", "music"], "bot1")
    redditBot.start(handle_comment)


def handle_comment(comment):
    if comment.body is None:
        return

    print("Finding lyrics for comment {} by {}:".format(comment,
                                                        comment.author))
    print(comment.body)

    comment_lines = comment.body.split('\n')
    last_line = comment_lines[-1]
    line_length = len(last_line.split(' '))

    if line_length < MIN_WORD_LENGTH or line_length > MAX_WORD_LENGTH:
        return

    lyrics_result = resolver.find_lyrics_by_fragment(last_line)

    if lyrics_result is None:
        print("No matching lyrics found")
        return

    (song_name, lyrics) = lyrics_result

    line_result = extract_lines(lyrics, last_line)

    if line_result is None:
        print("Comment was last line of lyrics")
        return

    line, confidence = line_result

    if confidence < CONFIDENCE_THRESHOLD:
        print("Confidence is too low: {}".format(confidence))
        return

    print("Responding to comment")
    redditBot.post_comment_reply(comment, line)


if __name__ == "__main__":
    main()
