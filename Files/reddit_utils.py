# reddit_utils.py
import requests
import flet as ft

API_URL = "http://localhost:8000"  # Adjust if different

def load_reddit_posts(reddit_section: ft.Column):
    try:
        reddit_res = requests.get(f"{API_URL}/reddit/top")
        reddit_section.controls.clear()
        if reddit_res.status_code == 200:
            posts = reddit_res.json()
            reddit_section.controls.append(
                ft.Text("🌐 Trending in r/mentalhealth", size=20, weight=ft.FontWeight.BOLD)
            )
            for post in posts:
                reddit_section.controls.append(
                    ft.TextButton(
                        text=post["title"],
                        url=post["url"],
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=5),
                            padding=20,
                            bgcolor=ft.Colors.BLUE_100
                        ),
                        height=60
                    )
                )
        else:
            reddit_section.controls.append(ft.Text("⚠️ Failed to load Reddit posts."))
    except Exception as err:
        reddit_section.controls.clear()
        reddit_section.controls.append(ft.Text(f"⚠️ Reddit Error: {err}"))
