import instaloader
import time
import json
import os
import requests
from datetime import datetime

# SETTINGS
SESSION_USERNAME = 'ya.azab'
DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1397679805125623971/L-MooU-NqajtcEx-JW0H7r5zbpufNZCsdkYk3THgwYE4-nkMcm1yPfM9S0BPvzO8--d-'
FOLLOW_FILE = 'follow_snapshots.json'
POST_FILE = 'post_snapshots.json'
CHECK_INTERVAL = 15 * 60  # 15 minutes

# USERS TO MONITOR
follow_notification_users = ['user1', 'user2']
post_notification_users = ['user3', 'user4']

# INIT
L = instaloader.Instaloader(dirname_pattern='.', quiet=True)

def notify_discord(title, body):
    try:
        data = {
            "embeds": [{
                "title": title,
                "description": body,
                "color": 3447003,
                "timestamp": datetime.utcnow().isoformat()
            }]
        }
        requests.post(DISCORD_WEBHOOK, json=data)
    except Exception as e:
        print(f"[DISCORD ERROR] {e}")

def load_session():
    try:
        L.load_session_from_file(SESSION_USERNAME)
        print(f"[INFO] Loaded session for {SESSION_USERNAME}")
    except FileNotFoundError:
        print(f"[LOGIN REQUIRED] Logging in for {SESSION_USERNAME}")
        L.login(SESSION_USERNAME, input("Enter password: "))
        L.save_session_to_file()

def load_json(file):
    return json.load(open(file)) if os.path.exists(file) else {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

def get_following(username):
    try:
        prof = instaloader.Profile.from_username(L.context, username)
        return sorted([u.username for u in prof.get_followees()])
    except Exception as e:
        print(f"[FOLLOW ERROR] {username}: {e}")
        return []

def get_last_post(username):
    try:
        prof = instaloader.Profile.from_username(L.context, username)
        posts = list(prof.get_posts())
        return posts[0].date_utc.isoformat() if posts else None
    except Exception as e:
        print(f"[POST ERROR] {username}: {e}")
        return None

def check_new_follows(snapshots):
    for user in follow_notification_users:
        current = get_following(user)
        previous = snapshots.get(user, [])
        new_follows = list(set(current) - set(previous))
        if new_follows:
            msg = f"🟢 **{user}** followed: `{', '.join(new_follows)}`"
            notify_discord(f"{user} New Follows", msg)
        snapshots[user] = current

def check_new_posts(snapshots):
    for user in post_notification_users:
        recent = get_last_post(user)
        if not recent:
            continue
        previous = snapshots.get(user)
        if previous != recent:
            msg = f"📷 **{user}** posted at `{recent}`"
            notify_discord(f"{user} New Post", msg)
            snapshots[user] = recent

def main_loop():
    load_session()
    follows = load_json(FOLLOW_FILE)
    posts = load_json(POST_FILE)

    while True:
        print(f"[CHECKING @ {datetime.now().isoformat()}]")
        check_new_follows(follows)
        check_new_posts(posts)
        save_json(FOLLOW_FILE, follows)
        save_json(POST_FILE, posts)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main_loop()
