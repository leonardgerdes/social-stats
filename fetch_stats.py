import urllib.request
import re
import json
from datetime import datetime, timezone

def extract_meta(html, key):
    p1 = rf'<meta[^>]+(?:property|name)=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)["\']'
    p2 = rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']{re.escape(key)}["\']'
    for p in [p1, p2]:
        m = re.search(p, html, re.IGNORECASE)
        if m:
            return m.group(1).replace('&amp;', '&')
    return ""

def fetch_instagram(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
        
        followers = 0
        desc = extract_meta(content, "og:description") or extract_meta(content, "description")
        target_text = desc if desc else content
        f_match = re.search(r'([\d,\.kKmM]+)\s*(?:Followers|Follower|Abonnenten)', target_text, re.IGNORECASE)
        if f_match:
            raw = f_match.group(1).replace(',', '')
            if 'k' in raw.lower(): followers = int(float(raw.lower().replace('k', '')) * 1000)
            elif 'm' in raw.lower(): followers = int(float(raw.lower().replace('m', '')) * 1000000)
            else: followers = int(raw)

        avatar = extract_meta(content, "og:image")

        return {"status": "ok", "username": username, "followers": followers, "avatar": avatar, "url": f"https://www.instagram.com/{username}/"}
    except Exception as e:
        return {"status": "error", "followers": 0, "avatar": "", "url": f"https://www.instagram.com/{username}/"}

def fetch_tiktok(username):
    url = f"https://www.tiktok.com/@{username}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
        
        f_match = re.findall(r'"followerCount":\s*(\d+)', content)
        followers = int(f_match[0]) if f_match else 0
            
        l_match = re.findall(r'"heartCount":\s*(\d+)', content)
        likes = int(l_match[0]) if l_match else 0

        av_match = re.findall(r'"avatarLarger":\s*"([^"]+)"', content)
        avatar = av_match[0].encode().decode('unicode_escape') if av_match else ""

        return {"status": "ok", "username": username, "followers": followers, "likes": likes, "avatar": avatar, "url": f"https://www.tiktok.com/@{username}"}
    except Exception as e:
        return {"status": "error", "followers": 0, "likes": 0, "avatar": "", "url": f"https://www.tiktok.com/@{username}"}

def fetch_pinterest(username):
    url = f"https://www.pinterest.com/{username}/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
        
        f_match = re.findall(r'"follower_count":\s*(\d+)', content)
        followers = int(f_match[0]) if f_match else 0

        img_match = re.findall(r'"image_medium_url":\s*"([^"]+)"', content)
        avatar = img_match[0].replace('75x75_RS', '280x280_RS') if img_match else ""

        return {"status": "ok", "username": username, "followers": followers, "avatar": avatar, "url": f"https://www.pinterest.com/{username}/"}
    except Exception as e:
        return {"status": "error", "followers": 0, "avatar": "", "url": f"https://www.pinterest.com/{username}/"}

def main():
    data = {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "instagram": fetch_instagram("janaue7"),
        "tiktok_chiarajana": fetch_tiktok("chiarajana"),
        "tiktok_janaa_ue": fetch_tiktok("janaa_ue"),
        "pinterest": fetch_pinterest("janaue7")
    }
    with open("stats.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
