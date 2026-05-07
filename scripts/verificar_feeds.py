import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

def checar(nome, url):
    try:
        r = requests.get(url, timeout=8, headers=HEADERS, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        text = r.text[:300]
        is_xml = "xml" in ct or text.strip().startswith("<rss") or text.strip().startswith("<?xml") or "<feed" in text[:200]
        tipo = "XML" if is_xml else "HTML"
        print(f"{nome:12} {r.status_code} {tipo}  {r.url}")
        if is_xml:
            print(f"  -> {text[:120]}")
    except Exception as e:
        print(f"{nome:12} ERR  {url}: {e}")

print("=== R7 ===")
for url in [
    "https://noticias.r7.com/feed/",
    "https://noticias.r7.com/rss",
    "https://noticias.r7.com/rss.xml",
    "https://www.r7.com/feed/",
]:
    checar("r7", url)

print("\n=== BandNews ===")
for url in [
    "https://bandnewstv.uol.com.br/feed/",
    "https://bandnewstv.uol.com.br/rss.xml",
    "https://band.uol.com.br/bandnews/feed/",
    "https://bandnewstv.band.uol.com.br/rss/",
]:
    checar("band", url)

print("\n=== Belford Roxo ===")
for url in [
    "https://www.noticiasdebelfordroxo.com/feed/",
    "https://www.noticiasdebelfordroxo.com/feeds/posts/default",
    "https://noticiasdebelfordroxo.com/feed/",
]:
    checar("belfordroxo", url)
