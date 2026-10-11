import os, requests

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]

r = requests.post(
    f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
    headers={"Authorization": f"Bot {TOKEN}"},
    json={"embeds": [{
        "title": "✅ اختبار البوت",
        "description": "إذا ظهرت هذه الرسالة فكل شيء في Discord يعمل.",
        "color": 0x22C55E,
    }]},
    timeout=30,
)
print(r.status_code, r.text)
r.raise_for_status()
