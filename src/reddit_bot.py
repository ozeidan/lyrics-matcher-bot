import praw
import threading
import time

MIN_WORD_COUNT = 5
MAX_WORD_COUNT = 15
BEGINNING_WAIT_TIME_SECONDS = 3
REPLY_FAIL_RETRY_TIME_SECONDS = 10


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

    def handle_comment(self, comment):
        print("Parsing comment by {}".format(comment.author.name))

        if comment.body is None:
            print("Comment-body is empty")
            return

        if comment.author.name == self.reddit.config.username:
            print("Not replying to own comment")
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
            (line, comment) = CommentBot.lyrics_queue.get()
            CommentBot.__reply_to_comment(line, comment)

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


def check_for_valid_line(comment):
    comment_lines = comment.split('\n')
    last_line = comment_lines[-1]
    sentences = last_line.split(".")
    last_sentence = sentences[-1]
    line_length = len(last_sentence.split(' '))

    if line_length < MIN_WORD_COUNT or line_length > MAX_WORD_COUNT:
        return None

    return last_sentence
