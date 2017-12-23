import praw
import threading
import time

MIN_WORD_COUNT = 5
MAX_WORD_COUNT = 15
BEGINNING_WAIT_TIME_SECONDS = 5
REPLY_FAIL_RETRY_TIME_SECONDS = 10

BOT_MESSAGE = "^^^I'm a bot *boop* *beep* and this song is {}. Here is my [source]({})"

GITHUB_LINK = "https://github.com/ozeidan/lyrics-matcher-bot"


class CommentBot:
    snippet_queue = None
    lyrics_queue = None

    def __init__(self,
                 subreddits,
                 botname):
        self.reddit = praw.Reddit(botname)
        self.subreddits = self.reddit.subreddit('+'.join(subreddits))
        self.reply_thread = threading.Thread(target=self.__main_loop)

    def start(self):
        self.reply_thread.start()
        start_time = time.time()

        for comment in self.subreddits.stream.comments():
            if (time.time() - start_time) > BEGINNING_WAIT_TIME_SECONDS:
                self.handle_comment(comment)

            print("Size of queues: ({},{})".format(CommentBot.snippet_queue.qsize(),
                                                   CommentBot.lyrics_queue.qsize()))

    def handle_comment(self, comment):
        print("Parsing comment by {}".format(comment.author.name))

        if comment.body is None:
            print("Comment-body is empty")
            return

        if comment.author.name == self.reddit.config.username:
            print("Not replying to own comment")
            return

        if comment.author.name == "rosey-the-bot":
            return

        for child in comment.replies:
            if child.author.name == self.reddit.config.username:
                print("Already replied to this comment, skipping".format(
                    comment, comment.author))
                return

        last_line = check_for_valid_line(comment.body)

        if last_line is not None:
            CommentBot.snippet_queue.put((last_line, comment))
        else:
            print("Comment does not statify the format constraints")

    def __main_loop(self):
        while True:
            (line, song_title, comment) = CommentBot.lyrics_queue.get()
            reply = CommentBot.__transform_reply(line, song_title)
            CommentBot.__reply_to_comment(reply, comment)

    def __reply_to_comment(reply, comment):
        print("Replying {} to comment at {}".format(reply,
                                                    comment.permalink))
        try:
            comment.reply(reply)
        except praw.exceptions.APIException:
            print("Can't comment because of reply limit")
            print("Trying again in {} seconds".format(
                REPLY_FAIL_RETRY_TIME_SECONDS))

            time.sleep(REPLY_FAIL_RETRY_TIME_SECONDS)
            CommentBot.__reply_to_comment(reply, comment)

    def __transform_reply(reply, song_title):
        reply += " 🎶\n"
        reply += "***\n"

        bot_message = BOT_MESSAGE.format(song_title,
                                         GITHUB_LINK)

        bot_message = bot_message.replace(' ', '&#32;')

        return reply + bot_message


def check_for_valid_line(comment):
    comment_lines = comment.strip().split('\n')
    last_line = comment_lines[-1].strip()
    sentences = last_line.split(".")
    sentences = [x for x in sentences if not (x.isspace() or x == '')]

    if len(sentences) == 0:
        return None

    last_sentence = sentences[-1].strip()
    line_length = len(last_sentence.split(' '))

    if line_length < MIN_WORD_COUNT or line_length > MAX_WORD_COUNT:
        return None

    return last_sentence
