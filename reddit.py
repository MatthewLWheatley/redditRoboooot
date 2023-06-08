import praw

reddit = praw.Reddit(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="your_user_agent",
)

subreddit = reddit.subreddit("AmITheAsshole")

top_post = subreddit.top("week", limit=1)

for post in top_post:
    print(post.title)