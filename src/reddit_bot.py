import praw


class CommentBot:
    def __init__(self, subreddits, botname):
        self.reddit = praw.Reddit(botname)
        self.subreddit_list = subreddits
        self.subreddits = self.reddit.subreddit('+'.join(subreddits))

    def start(self, commentHandler):
        for comment in self.subreddits.stream.comments():
            print("##############################################")
            print()
            print()
            commentHandler(comment)
            print()
            print()
            print("##############################################")

    def post_comment_reply(self, comment, reply):
        comment.reply(reply)
