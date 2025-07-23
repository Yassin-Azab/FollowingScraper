from flask import Flask, jsonify
import instaloader, os, json, requests

app = Flask(__name__)
USERNAME = "mr.thank.you"
DISCORD_WEBHOOK = os.environ.get("WEBHOOK_URL")
SESSION_USERNAME = "ya.azab"

def notify(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

def check():
    L = instaloader.Instaloader()
    # Load session from local file (in same directory)
    session_file = f"session-{SESSION_USERNAME}"
    L.load_session_from_file(SESSION_USERNAME, filename=session_file)

    profile = instaloader.Profile.from_username(L.context, USERNAME)

    # Check new followings
    current = [u.username for u in profile.get_followees()]
    old = json.load(open("followings.json")) if os.path.exists("followings.json") else []
    new_follows = set(current) - set(old)
    if new_follows:
        for u in new_follows:
            notify(f"🧲 {USERNAME} followed {u}")
        json.dump(current, open("followings.json", "w"))

    # Check for new post
    latest = next(profile.get_posts())
    lastid = open("last_post.txt").read().strip() if os.path.exists("last_post.txt") else ""
    if str(latest.mediaid) != lastid:
        notify(f"🆕 {USERNAME} posted https://instagram.com/p/{latest.shortcode}")
        open("last_post.txt", "w").write(str(latest.mediaid))

@app.route("/run", methods=["GET"])
def run():
    try:
        check()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
