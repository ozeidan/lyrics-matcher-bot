import argparse
import driver


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Start the lyrics matcher bot.")
    parser.add_argument('apikey', metavar='apikey', nargs=1,
                        help='API key for the genius.com API')
    parser.add_argument('subreddits', metavar='subreddit', nargs='+',
                        help='a list of subreddit names '
                        'which the bot should listen')

    args = parser.parse_args()
    driver.start(args.subreddits, args.apikey[0])
