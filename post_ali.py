import hashlib, hmac, json, os, sys, time
import requests

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]
APP_KEY = os.environ["ALI_APP_KEY"].strip()
APP_SECRET = os.environ["ALI_APP_SECRET"].strip()
TRACKING_ID = os.environ["ALI_TRACKING_ID"].strip()
print("key length:", len(APP_KEY), "| secret length:", len(APP_SECRET), "| tracking:", TRACKING_ID)

MAX_PER_RUN = int(os.environ.get("MAX_PER_RUN", "3"))
GATEWAY = "https://api-sg.aliexpress.com/sync"


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def sign(params):
    base = "".join(k + str(params[k]) for k in sorted(params))
    return hmac.new(APP_SECRET.encode(), base.encode(), hashlib.sha256).hexdigest().upper()


def search(keyword):
    params = {
        "app_key": APP_KEY,
        "method": "aliexpress.affiliate.product.query",
        "sign_method": "sha256",
        "timestamp": str(int(time.time() * 1000)),
        "keywords": keyword,
        "tracking_id": TRACKING_ID,
        "page_no": "1",
        "page_size": "20",
        "sort": "LAST_VOLUME_DESC",
        "target_currency": "USD",
        "target_language": "EN",
    }
    params["sign"] = sign(params)
    r = requests.get(GATEWAY, params=params, timeout=30)
    print("HTTP status:", r.status_code)
    data = r.json()
    print("Raw response:", json.dumps(data, ensure_ascii=False)[:1500])
    try:
        return data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]
    except (KeyError, TypeError):
        print("Could not find products in response.")
        return []


keywords = load("keywords.json", ["gaming mouse"])
posted = load("posted.json", [])

# كلمة بحث مختلفة في كل تشغيل
keyword = keywords[int(time.time() // 3600) % len(keywords)]
print("Keyword:", keyword)

products = [p for p in search(keyword) if str(p["product_id"]) not in posted][:MAX_PER_RUN]
if not products:
    print("No new products.")
    sys.exit(0)

failed = False
for p in products:
    price = p.get("target_sale_price", "?")
    cur = p.get("target_sale_price_currency", "")
    old = p.get("target_original_price")
    desc = f"💰 {price} {cur}"
    if old and old != price:
        desc += f"  ~~{old}~~"
    if p.get("discount"):
        desc += f"\n🔥 خصم {p['discount']}"

    embed = {
        "title": p["product_title"][:250],
        "description": desc,
        "url": p["promotion_link"],
        "color": 0xE62E04,
        "footer": {"text": "رابط أفلييت: قد أحصل على عمولة عند الشراء."},
    }
    if p.get("product_main_image_url"):
        embed["image"] = {"url": p["product_main_image_url"]}

    r = requests.post(
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
        headers={"Authorization": f"Bot {TOKEN}"},
        json={"embeds": [embed]},
        timeout=30,
    )
    if r.status_code in (200, 201):
        posted.append(str(p["product_id"]))
        print("Posted:", p["product_id"])
    else:
        print("Discord failed:", r.status_code, r.text)
        failed = True

with open("posted.json", "w", encoding="utf-8") as f:
    json.dump(posted[-500:], f, indent=2)

sys.exit(1 if failed else 0)
