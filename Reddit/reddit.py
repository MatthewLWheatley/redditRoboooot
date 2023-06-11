import csv
import praw
from praw.models import Submission

def get_new_post(subreddit_name: str = "AmITheAsshole", time_span: str = "week") -> Submission:
    reddit = praw.Reddit(
        client_id="sZRalb8HbGbqM3M_G6FVUg",     # replace with your client id
        client_secret="KLAQNOFu5G4vf6aAo7QAca5-yeOr4Q",  # replace with your client secret
        user_agent="Windows:RedditRobot:v1.03:Mattyl3e",    # replace with your user agent
        username="Mattyl3e",  # your Reddit username
        password="B8173157zantac!" # your Reddit password
        )

    subreddit = reddit.subreddit(subreddit_name)

    # Load the existing posts from the CSV
    done_posts = {}
    with open('output/Done.csv', 'r') as done_file:
        reader = csv.reader(done_file)
        for row in reader:
            done_posts[row[0]] = (row[1], row[2], row[3])  # Key: post_id, Value: (username, title, subreddit)

    # Retrieve top posts of the given time period
    top_posts = subreddit.top(time_filter=time_span)

    # Iterate over the posts
    for post in top_posts:
        # If post has not been processed
        if post.id not in done_posts:
            # Skip the post if the first word of the title is 'UPDATE'
            if post.title.split()[0].upper() == 'UPDATE':
                continue

            author_name = post.author.name if post.author else "Unknown"
            # Add the new post to the done_posts dictionary
            done_posts[post.id] = (author_name, post.title, subreddit_name)
            
            # Write the updated list back to the CSV
            with open('output/Done.csv', 'w', newline='') as done_file:
                writer = csv.writer(done_file)
                for post_id, (username, title, subreddit) in done_posts.items():
                    writer.writerow([post_id, username, title, subreddit])

            # Return the new post
            return post

    # If no new post was found, return None
    return None