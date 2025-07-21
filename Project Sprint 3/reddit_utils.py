
import requests
import flet as ft

API_URL = "http://localhost:8000" 


def load_reddit_posts(reddit_section: ft.Column):
    reddit_section.controls.clear()
    reddit_section.visible = True

    try:
        res = requests.get(f"{API_URL}/reddit/posts")
        if res.status_code == 200:
            reddit_posts = res.json()
            if reddit_posts:
                reddit_section.controls.append(
                    ft.Text("🌐 Trending in r/mentalhealth", size=30, weight=ft.FontWeight.BOLD)
                )
                for post in reddit_posts:
                    reddit_section.controls.append(
                        ft.TextButton(
                            text=post["title"],
                            url=post["url"],
                            width=1600,
                            height=100,
                            content=ft.Column([
                                ft.Row([ft.Text(
                                    f"u/{post['author']}",
                                    color=ft.Colors.RED_ACCENT,
                                    weight=ft.FontWeight.BOLD,
                                    size=26,
                            )
                             ], alignment=ft.MainAxisAlignment.CENTER),

                             ft.Row([ 
                                 ft.Text(
                                post["title"],
                                color=ft.Colors.BLACK54,
                                weight=ft.FontWeight.BOLD,
                                
                                
                                size=26,
                                

                            )
                            ],alignment=ft.MainAxisAlignment.START)
                             ], spacing=5),
                            style=ft.ButtonStyle(
                                text_style=ft.TextStyle(color=ft.Colors.BLACK, size=26),
                                shape=ft.RoundedRectangleBorder(radius=7),
                                padding=20,
                                bgcolor=ft.Colors.BLUE_100,
                                side=ft.BorderSide(4, ft.Colors.BLACK),   
                            ),
                        )
                    )
                    
                    
            else:
                reddit_section.controls.append(ft.Text("No Reddit posts found.", size=20))
        else:
            reddit_section.controls.append(ft.Text("⚠️ Failed to load Reddit posts.", size=20, color=ft.Colors.RED))
    except Exception as ex:
        reddit_section.controls.append(ft.Text(f"❌ Exception loading Reddit: {ex}", size=20, color=ft.Colors.RED))
