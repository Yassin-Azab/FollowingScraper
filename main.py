import requests, json, os
from bs4 import BeautifulSoup

USERNAME = "mr.thank.you"
DISCORD_WEBHOOK = os.environ.get("WEBHOOK_URL")  # Set this in Render dashboard later

def get_following():
    url = f"https://www.instagram.com/{USERNAME}/"
    headers = {
        "User-Agent": "Mozilla/5.0",
    }
    r = requests.get(url, headers=headers)
    if "edge_followed_by" not in r.text:
        return []

    shared_data_prefix = 'window._sharedData = '
    shared_data = r.text.split(shared_data_prefix)[1].split(";</script>")[0]
    json_data = json.loads(shared_data)

    try:
        user_id = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
    except Exception:
        return []

    follow_url = f"https://i.instagram.com/api/v1/friendships/{user_id}/following/?count=10"
    headers.update({
        "User-Agent": "Instagram 219.0.0.12.117 Android",
        "x-ig-app-id": "936619743392459",
    })
    r = requests.get(follow_url, headers=headers)
    return r.json().get("users", [])

def load_last_following():
    try:
        with open("last_following.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_current_following(following):
    with open("last_following.json", "w") as f:
        json.dump(following, f)

def send_discord_notification(new_users):
    for user in new_users:
        requests.post(DISCORD_WEBHOOK, json={
            "content": f"🆕 @{USERNAME} just followed @{user['username']} — {user.get('full_name', '')}"
        })

def main():
    current = get_following()
    current_usernames = [u["username"] for u in current]
    previous_usernames = load_last_following()

    new_followed = [u for u in current if u["username"] not in previous_usernames]
    if new_followed:
        send_discord_notification(new_followed)
        save_current_following(current_usernames)

main()
