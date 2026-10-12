import os, requests

TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID", "")

print("token length:", len(TOKEN), "| dots:", TOKEN.count("."), "| has space/newline:", TOKEN != TOKEN.strip())
print("channel id length:", len(CHANNEL_ID))

headers = {"Authorization": f"Bot {TOKEN.strip()}"}

# 1) فحص التوكن وحده
me = requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=30)
print("Token check:", me.status_code, me.text[:200])
if me.status_code != 200:
    raise SystemExit("Token is invalid, stop here.")

# 2) إرسال الرسالة
r = requests.post(
    f"https://discord.com/api/v10/channels/{CHANNEL_ID.strip()}/messages",
    headers=headers,
    json={"embeds": [{
        "title": "✅ اختبار البوت",
        "description": "إذا ظهرت هذه الرسالة فكل شيء في Discord يعمل.",
        "color": 0x22C55E,
    }]},
    timeout=30,
)
print("Send message:", r.status_code, r.text[:300])
r.raise_for_status()
