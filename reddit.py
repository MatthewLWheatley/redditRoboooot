import csv
import csv
import praw
from praw.models import Submission

def get_new_post() -> Submission:
    reddit = praw.Reddit(
        client_id="sZRalb8HbGbqM3M_G6FVUg",     # replace with your client id
        client_secret="KLAQNOFu5G4vf6aAo7QAca5-yeOr4Q",  # replace with your client secret
        user_agent="Windows:RedditRobot:v1.03:Mattyl3e",    # replace with your user agent
        username="Mattyl3e",  # your Reddit username
        password="B8173157zantac!" # your Reddit password
        )

    subreddit = reddit.subreddit("AmITheAsshole")

    # Load the existing posts from the CSV
    done_posts = {}
    with open('Done.csv', 'r') as done_file:
        reader = csv.reader(done_file)
        for row in reader:
            done_posts[row[0]] = (row[1], row[2])  # Key: post_id, Value: (username, title)

    # Retrieve top posts of the week
    top_posts = subreddit.top("week")

    # Iterate over the posts
    for post in top_posts:
        # If post has not been processed
        if post.id not in done_posts:
            # Add the new post to the done_posts dictionary
            done_posts[post.id] = (post.author.name, post.title)
            
            # Write the updated list back to the CSV
            with open('output\Done.csv', 'w', newline='') as done_file:
                writer = csv.writer(done_file)
                for post_id, (username, title) in done_posts.items():
                    writer.writerow([post_id, username, title])

            # Return the new post
            return post

    # If no new post was found, return None
    return None

# Usage
new_post = get_new_post()
if new_post is not None:
    print(new_post.title)