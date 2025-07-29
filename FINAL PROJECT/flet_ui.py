import flet as ft
import requests
import random
from datetime import datetime
from reddit_utils import load_reddit_posts


def fetch_reddit_posts():
    try:
        response = requests.get("http://127.0.0.1:8000/reddit/posts")
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        print("Error fetching Reddit posts:", e)
        return []


API_URL = "http://127.0.0.1:8000"

BG_COLORS = [ft.Colors.BLUE_800]
MOTIVATIONAL_QUOTES = [
    "Keep going, you're doing great!",
    "You are stronger than you think.",
    "Progress, not perfection.",
    "Every day is a fresh start.",
    "Your mental health matters.",
    "Be kind to yourself today.",
    "One step at a time.",
]

def main(page: ft.Page):
    page.title = "Mental Health Tracker"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 50
    page.bgcolor = ft.Colors.DEEP_PURPLE_ACCENT_100

    token = None
    user_id = None

    # --- UI Sections ---
    welcome_text = ft.Text(size=60, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)
    quote_text   = ft.Text(size=44, italic=True, color=ft.Colors.BLACK)
    message_text = ft.Text(color=ft.Colors.BLACK, size=40)

    login_username    = ft.TextField(label="Username", width=800, height=100, text_size=44)
    login_password    = ft.TextField(label="Password", password=True, width=800, height=100, text_size=44)
    register_username = ft.TextField(label="New Username", width=800, height=100, text_size=44)
    register_email    = ft.TextField(label="Email", width=800, height=100, text_size=44)
    register_password = ft.TextField(label="Password", password=True, width=800, height=100, text_size=44)

    journal_input     = ft.TextField(label="Write your journal", multiline=True, min_lines=10,
                                     width=900, height=200, text_size=38)
    mood_score_slider = ft.Slider(min=1, max=10, divisions=9, label="{value}", value=5, width=500)

    mood_category_buttons = []
    selected_mood_value   = ft.Text(value="Happy", visible=False)
    MOOD_OPTIONS = ["Happy", "Sad", "Anxious", "Calm", "Excited", "Tired"]
    for mood in MOOD_OPTIONS:
        btn = ft.ElevatedButton(
            mood, width=200, height=80,
            style=ft.ButtonStyle(text_style=ft.TextStyle(size=32),side=ft.BorderSide(4, ft.Colors.LIGHT_GREEN_900),),
            
            on_click=lambda e, m=mood: (
                setattr(selected_mood_value, "value", m),
                [setattr(b.style, "bgcolor", ft.Colors.GREY_200) for b in mood_category_buttons],
                setattr(e.control.style, "bgcolor", ft.Colors.LIGHT_GREEN_900),
                page.update()
            )
        )
        mood_category_buttons.append(btn)
 

    # Dashboard sections
    login_register_section = ft.Row(visible=True)
    mood_journal_section   = ft.Column(visible=False)
    diary_section          = ft.Column(visible=False, spacing=30, expand=True)
    recent_moods_section   = ft.Column(visible=False, spacing=30, expand=True)
    reddit_section = ft.Column(visible=True, spacing=40, scroll=ft.ScrollMode.AUTO)


    # All-Users list
    user_list_section = ft.Column(visible=False, expand=True)
    

    external_user_section = ft.Column(visible=False, expand=True)

 
    back_button = ft.ElevatedButton("🔙 Back to Users List", width=300, height=80)

    

    def logout(e):
        
        nonlocal token, user_id
        token = user_id = None
        welcome_text.value = quote_text.value = ""
        message_text.value = "Logged out successfully."
  
        login_register_section.visible = True
        mood_journal_section.visible   = False
        diary_section.visible          = False
        recent_moods_section.visible   = False
        user_list_section.visible      = False
        external_user_section.visible  = False
        reddit_section.visible = False
        
        page.update()

    def login(e):
        recent_moods_section.visible = True
        
        
        nonlocal token, user_id
        try:
            res = requests.post(f"{API_URL}/token",
                                data={"username": login_username.value, "password": login_password.value})
            if res.status_code == 200:
                token = res.json()["access_token"]
                me = requests.get(f"{API_URL}/users/me", headers={"Authorization":f"Bearer {token}"})
                if me.status_code == 200:
                    u = me.json()
                    user_id = u["id"]
                    welcome_text.value = f"👋 Welcome, {u['username']}!"
                    # Fetch quote
                    load_reddit_posts(reddit_section)
                    try:
                        qres = requests.get(f"{API_URL}/motivation/quote")
                        if qres.status_code == 200:
                            q = qres.json()
                            quote_text.value = f"💡 {q['quote']} — {q['author']}"
                        else:
                            quote_text.value = f"💡 {random.choice(MOTIVATIONAL_QUOTES)}"
                    except:
                        quote_text.value = f"💡 {random.choice(MOTIVATIONAL_QUOTES)}"
                        reddit_posts = fetch_reddit_posts()
                        reddit_section.controls.clear()
                        if reddit_posts:
                            reddit_section.controls.append(ft.Text("🌐 Trending in r/mentalhealth", size=52, weight=ft.FontWeight.BOLD))
                            for post in reddit_posts:
                                 reddit_section.controls.append(
                                     ft.TextButton(
                                         text=post["title"],
                                         url=post["url"],
                                         style=ft.ButtonStyle(
                                             shape=ft.RoundedRectangleBorder(radius=5),
                                             padding=20,
                                             bgcolor=ft.Colors.PURPLE
                                             ),
                                             height=100
                                     )
                                 )
                            else:
                                 reddit_section.controls.append(ft.Text("No Reddit posts found.", size=36, color=ft.Colors.RED))
                                 reddit_section.visible = True


                    page.bgcolor = random.choice(BG_COLORS)
                    login_register_section.visible = False
                    mood_journal_section.visible   = True
                    diary_section.visible          = True
                    recent_moods_section.visible   = False
                    message_text.value             = ""
            else:
                message_text.color = ft.Colors.RED
                if res.headers.get("content-type","").startswith("application/json"):
                    message_text.value = res.json().get("detail")
                else:
                    message_text.value = f"Login failed: {res.status_code}"
        except Exception as ex:
            message_text.color = ft.Colors.RED
            message_text.value = f"Exception: {ex}"
            
            
            load_reddit_posts(reddit_section)
            reddit_section.visible = True


        page.update()

    def register(e):
        try:
            if not register_username.value.strip():
                message_text.value = "❌ Username is required."
                page.update()
                return
            if not register_email.value.strip():
                message_text.value = "❌ Email is required."
                page.update()
                return
            if "@gmail.com" not in register_email.value:
                message_text.color = ft.Colors.RED
                message_text.value = "❌ Invalid email address."
                page.update()
                return
            if not register_password.value.strip():
                message_text.value = "❌ Password is required."
                page.update()
                return
            
            if len(register_password.value) < 6:
                message_text.color = ft.Colors.RED
                message_text.value = "❌ Password too short. Minimum 6 characters."
                page.update()
                return
            
            
            

            
                
            res = requests.post(f"{API_URL}/users/",
                                json={"username":register_username.value,
                                      "email":register_email.value,
                                      "password":register_password.value})
            if res.status_code == 201:
                message_text.color = ft.Colors.GREEN
                message_text.value = "Registration successful! Please log in."
                register_username.value = register_email.value = register_password.value = ""

            
            else:
                detail = res.json().get("detail","Unknown error")
                message_text.color = ft.Colors.RED
                message_text.value = "❌ Registration failed"

                if "username" in detail.lower() and ("exist" in detail.lower() or "registered" in detail.lower()):
                    message_text.color = ft.Colors.RED
                    message_text.value = "❌ Username already taken."
                elif "email" in detail.lower() and ("exist" in detail.lower() or "registered" in detail.lower()):
                    message_text.color = ft.Colors.RED
                    message_text.value = "❌ Email already registered."

        except Exception as ex:
            message_text.color = ft.Colors.RED
            message_text.value = "❌ Registration failed"
        page.update()

    def submit_journal(e):
        res = requests.post(f"{API_URL}/users/{user_id}/journals/",
                            json={"content":journal_input.value}, 
                            headers={"Authorization":f"Bearer {token}"})
        if res.status_code == 201:
            journal_input.value = ""
            message_text.color = ft.Colors.GREEN
            message_text.value = "Journal saved!"
        else:
            message_text.color = ft.Colors.RED
            message_text.value = "Failed to save journal."
        page.update()
    
    
    def submit_mood(e):
        res = requests.post(f"{API_URL}/users/{user_id}/moods/",
                            json={"score":int(mood_score_slider.value),
                                  "category":selected_mood_value.value},
                            headers={"Authorization":f"Bearer {token}"})
        if res.status_code == 201:
            message_text.color = ft.Colors.GREEN
            message_text.value = "Mood saved!"
        else:
            message_text.color = ft.Colors.RED
            message_text.value = "Failed to save mood."
        page.update()

    def load_diary(e):

        back_from_diary_button = ft.ElevatedButton("🔙 Back to Dashboard", width=300, height=80, on_click=back_to_dashboard)

        reddit_section.visible = False
        mood_journal_section.visible  = False
        diary_section.visible         = True
        recent_moods_section.visible = True
        external_user_section.visible = False
        login_register_section.visible = False
        
        
        
        rj = requests.get(f"{API_URL}/users/{user_id}/journals/",
                          headers={"Authorization":f"Bearer {token}"})
        rm = requests.get(f"{API_URL}/users/{user_id}/moods/",
                          headers={"Authorization":f"Bearer {token}"})
        if rj.status_code == 200 and rm.status_code == 200:



            
            diary_section.controls = [ft.Container(content=ft.Text("📔 Your Past Journals", size=52, weight=ft.FontWeight.BOLD),
                                      alignment=ft.alignment.top_left,
                                      
                                      padding=ft.padding.only(top=90)
                                      )
                                      
                                ]
            back_from_diary_button.on_click = back_to_dashboard
           
            recent_moods_section.controls = [
                ft.Container(
                    content=back_from_diary_button,
                    alignment=ft.alignment.top_left,
                    padding=ft.Padding(0, 0, 0, 10)
                    ),
                    ft.Text("Recent Moods", size=52, weight=ft.FontWeight.BOLD)]
            for m in sorted(rm.json(), key=lambda x: x["timestamp"], reverse=True):
                d = datetime.fromisoformat(m["timestamp"].replace("Z","+00:00")).strftime("%B %d, %Y")
                recent_moods_section.controls.append(
                    ft.Container(
                         content=ft.Column([
                            ft.Text(f"Date: {d}", size=36, color=ft.Colors.BLACK),
                            ft.Text(f"Score: {m['score']}", size=36, color=ft.Colors.BLACK),
                            ft.Text(f"Category: {m['category']}", size=40, color=ft.Colors.BLACK),
                        ]),
                        padding=30,
                        bgcolor=ft.Colors.YELLOW_200,
                        border=ft.border.all(2, ft.Colors.GREY_400),
                        border_radius=12
                    )
                )
            for e in sorted(rj.json(), key=lambda x: x["timestamp"], reverse=True):
                d = datetime.fromisoformat(e["timestamp"].replace("Z","+00:00")).strftime("%B %d, %Y")
                diary_section.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(d, size=40,
                            color=ft.Colors.BLACK),
                            ft.Text(e["content"], size=40, color=ft.Colors.BLACK),

                        ]),
                        padding=30,
                        bgcolor=ft.Colors.GREEN_100,
                        border=ft.border.all(2, ft.Colors.GREY_300),
                        border_radius=12
                    )
                )
        else:
            message_text.color = ft.Colors.RED
            message_text.value = "Failed to load entries."
        
        page.update()

    def back_to_user_list(e):
        external_user_section.visible = False
        user_list_section.visible = True
        page.update()

    def show_user_data(selected_user):
    
        reddit_section.visible = False
        mood_journal_section.visible  = False
        diary_section.visible         = False
        recent_moods_section.visible = False
        login_register_section.visible = False
        user_list_section.visible = False
        external_user_section.visible = True
        external_user_section.controls.clear()
        
       

        back_from_user_button = ft.ElevatedButton("🔙 Back to User List",width=300,height=100)
        back_from_user_button.on_click = back_to_user_list
        
        external_user_section.controls.append(
            ft.Container(
            content=ft.Text(f"📝 {selected_user['username']}'s Journals & Moods", size=52, weight=ft.FontWeight.BOLD),
            alignment=ft.alignment.top_left,
            padding=ft.padding.only(top=90)
            )
        )

        external_user_section.controls.append(
            ft.Container(
                content=back_from_user_button,
                alignment=ft.alignment.top_left,
                padding=ft.Padding(0, 0, 0, 10)
            )
        )
        try:
            rj = requests.get(f"{API_URL}/users/{selected_user['id']}/journals/",
                              headers={"Authorization":f"Bearer {token}"})
            rm = requests.get(f"{API_URL}/users/{selected_user['id']}/moods/",
                              headers={"Authorization":f"Bearer {token}"})
            if rj.status_code == 200:
                external_user_section.controls.append(
                    ft.Container(content=ft.Text("📔 Journal Entries", size=52, weight=ft.FontWeight.BOLD),
                                 alignment=ft.alignment.top_left,
                                 padding=ft.padding.only(top=90)
                    )
                )

                for entry in sorted(rj.json(), key=lambda x: x["timestamp"], reverse=True):
                    date = datetime.fromisoformat(entry["timestamp"].replace("Z","+00:00")).strftime("%B %d, %Y")
                    external_user_section.controls.append(
                        ft.Container(content=ft.Column([ft.Text(date, size=40, color=ft.Colors.BLACK),
                                                        ft.Text(entry["content"], size=40, color=ft.Colors.BLACK),
                                                        ]),padding=30,
                                                        bgcolor=ft.Colors.GREEN_100,
                                                        border=ft.border.all(2, ft.Colors.GREY_300),
                                                        border_radius=12
                        )
                    )
            if rm.status_code == 200:
                external_user_section.controls.append(ft.Container(
                    content=ft.Text("Recent Moods", size=52, weight=ft.FontWeight.BOLD),
                    alignment=ft.alignment.top_left,
                    padding=ft.padding.only(top=50)
                        )

                )
                for mood in sorted(rm.json(), key=lambda x: x["timestamp"], reverse=True):
                    date = datetime.fromisoformat(mood["timestamp"].replace("Z","+00:00")).strftime("%B %d, %Y")
                    external_user_section.controls.append(ft.Container(content=ft.Column([
                        ft.Text(f"Date: {date}", size=36, color=ft.Colors.BLACK),
                        ft.Text(f"Score: {mood['score']}", size=36, color=ft.Colors.BLACK),
                        ft.Text(f"Category: {mood['category']}", size=40, color=ft.Colors.BLACK)
                    ]),
                    padding=30,
                        bgcolor=ft.Colors.GREEN_100,
                        border=ft.border.all(2, ft.Colors.GREY_300),
                        border_radius=12
                    )
                                                                                          
                    )
        except Exception as ex:
            external_user_section.controls.append(
                ft.Text(f"❌ Error: {ex}", color=ft.Colors.RED, size=36)
            )

       
        page.update()


    def back_to_dashboard(e):
        user_list_section.visible = False
        mood_journal_section.visible = True
        diary_section.visible = False
        recent_moods_section.visible = False
        external_user_section.visible = False
        login_register_section.visible = False
        reddit_section.visible = True
        page.update()




    def view_all_users(e):
        mood_journal_section.visible  = False
        diary_section.visible         = False
        recent_moods_section.visible = False
        external_user_section.visible = False
        login_register_section.visible = False
        reddit_section.visible = False

        try:
            res = requests.get(f"{API_URL}/users/all",
                               headers={"Authorization":f"Bearer {token}"})
            user_list_section.controls.clear()
            if res.status_code == 200:
                user_list_section.visible = True
                
                
                user_list_section.controls.append( 
                     ft.ElevatedButton(
                         text="🔙 Back to Dashboard",
                         on_click=back_to_dashboard,
                         width=200
                     )
                 )
                user_list_section.controls.append(ft.Text("👥 All Users", size=90, weight=ft.FontWeight.BOLD))
                for u in res.json():
                    if u["id"] != user_id:
                        user_list_section.controls.append(
                            ft.ElevatedButton(
                                f"{u['username']} | {u['email']}",
                                on_click=lambda e, usr=u: show_user_data(usr),
                                width=600, height=150
                            )
                        )
            else:
                user_list_section.controls.append(
                    ft.Text("⚠️ Failed to fetch users", size=40, color=ft.Colors.RED)
                )
        except Exception as ex:
            message_text.color = ft.Colors.RED
            message_text.value = f"Exception: {ex}"
        page.update()

    # --- Layout ---

    login_register_section.controls = [
        ft.Column([
            ft.Text("🔐 Login", size=60, weight=ft.FontWeight.BOLD),
            login_username, login_password,
            ft.ElevatedButton("Login", on_click=login, width=500, height=100),
        ], spacing=40),
        ft.VerticalDivider(width=60),
        ft.Column([
            ft.Text("🆕 Register", size=60, weight=ft.FontWeight.BOLD),
            register_username, register_email, register_password,
            ft.ElevatedButton("Register", on_click=register, width=500, height=100),
        ], spacing=40),
    ]

    

    mood_journal_section.controls = [
        welcome_text, quote_text, ft.Divider(),
        ft.Row([
            ft.Column([
                ft.Text("📝 Journal Entry", size=52, weight=ft.FontWeight.BOLD),
                journal_input,
                ft.ElevatedButton("Submit Journal", on_click=submit_journal, width=500, height=100,
                                  style=ft.ButtonStyle(side=ft.BorderSide(5, ft.Colors.ORANGE_600)),)
            ], spacing=40, expand=True),
            ft.VerticalDivider(width=60),
            ft.Column([
                ft.Text("😊 Mood Entry", size=52, weight=ft.FontWeight.BOLD),
                ft.Row(mood_category_buttons, wrap=True),
                mood_score_slider,
                ft.ElevatedButton("Submit Mood", on_click=submit_mood, width=200, height=100,
                                  style=ft.ButtonStyle(side=ft.BorderSide(5, ft.Colors.ORANGE_600)),)
                
            ], spacing=30, expand=True),
        ]),
        ft.Row([
            ft.ElevatedButton("📤 Load Diary", on_click=load_diary, width=300, height=100,
                              style=ft.ButtonStyle(side=ft.BorderSide(5, ft.Colors.PURPLE_600)),),
            
            ft.ElevatedButton("👥My Community", on_click=view_all_users, width=300, height=100,
                              style=ft.ButtonStyle(side=ft.BorderSide(5, ft.Colors.YELLOW_800)),),
            
        ],
        alignment=ft.MainAxisAlignment.START
        ),
        ft.Container(
            ft.ElevatedButton("🚪 Logout", on_click=logout, width=300, height=100, bgcolor=ft.Colors.RED_400,style=ft.ButtonStyle(side=ft.BorderSide(5, ft.Colors.BLACK)),),
            alignment=ft.alignment.bottom_left,
            expand=True,
            border_radius=12,
            padding=ft.padding.only(left=1500)
        )
    ]

    page.add(
        ft.Column([
            login_register_section,
            message_text,
            mood_journal_section,
            reddit_section,
            ft.Row([recent_moods_section, diary_section], spacing=60, expand=True,vertical_alignment=ft.CrossAxisAlignment.START),
            user_list_section,       
            external_user_section,  
        ], spacing=50)
    )



ft.app(target=main)
