from reddit_bot import CommentBot
from lyrics_lookup import LyricsResolver
import queue


RESOLVER_THREAD_COUNT = 10

snippet_queue = queue.Queue()
lyrics_queue = queue.Queue()

resolver_workers = []


def start(subreddits, apikey):
    CommentBot.snippet_queue = snippet_queue
    CommentBot.lyrics_queue = lyrics_queue
    LyricsResolver.snippet_queue = snippet_queue
    LyricsResolver.lyrics_queue = lyrics_queue

    for i in range(0, RESOLVER_THREAD_COUNT):
        print("Starting worker {}".format(i))
        worker = LyricsResolver(apikey)
        worker.start()
        resolver_workers.append(worker)

    print("Starting comment parser/replier")
    redditBot = CommentBot(subreddits, "bot1")
    redditBot.start()

    for worker in resolver_workers:
        worker.thread.join()
