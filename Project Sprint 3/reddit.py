

import requests
from fastapi import APIRouter

reddit_router = APIRouter()




@reddit_router.get("/reddit/posts")
def get_reddit_posts():
    url = "https://www.reddit.com/r/mentalhealth/top.json?limit=5"
    headers = {"User-agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": "Failed to fetch Reddit posts"}

    data = response.json()
    posts = [
        {
            "title": post["data"]["title"],
            "url": f"https://reddit.com{post['data']['permalink']}",
            "author": post["data"].get("author", "unknown"),
            "subreddit": post["data"].get("subreddit", "mentalhealth")
        }
        for post in data["data"]["children"]
    ]
    return posts
