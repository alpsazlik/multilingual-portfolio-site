import requests
import sqlite3
import re
import time
import urllib.parse
import email.utils
from bs4 import BeautifulSoup


def resim_bul(haber_linki, headers):
    try:
        site_cevap = requests.get(haber_linki, headers=headers, timeout=5)
        soup = BeautifulSoup(site_cevap.content, "html.parser")
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"): return og_image["content"]
        twitter_image = soup.find("meta", name="twitter:image")
        if twitter_image and twitter_image.get("content"): return twitter_image["content"]
        for div_class in ["detail-image", "detail_image", "article-image", "news-image", "featured-image",
                          "hero-image"]:
            div = soup.find("div", class_=re.compile(div_class, re.I))
            if div and div.find("img"):
                img_src = div.find("img").get("src")
                if img_src and "http" in img_src: return img_src
    except:
        pass
    return None


def haber_zaten_var_mi(yeni_baslik, eski_basliklar):
    yeni_kelimeler = set([k.lower() for k in yeni_baslik.split() if len(k) > 3])
    if not yeni_kelimeler: return False
    for eski_baslik in eski_basliklar:
        eski_kelimeler = set([k.lower() for k in eski_baslik.split() if len(k) > 3])
        if not eski_kelimeler: continue
        ortak_kelimeler = yeni_kelimeler.intersection(eski_kelimeler)
        benzerlik = len(ortak_kelimeler) / min(len(yeni_kelimeler), len(eski_kelimeler))
        if benzerlik > 0.60: return True
    return False


def zaman_damgasi_al(blok):
    match = re.search(r'<(?:pubDate|published|updated)>(.*?)</(?:pubDate|published|updated)>', blok, re.IGNORECASE)
    if match:
        try:
            dt_tuple = email.utils.parsedate_tz(match.group(1))
            if dt_tuple: return email.utils.mktime_tz(dt_tuple)
        except:
            pass
    return time.time()


def canli_akis_baslat():
    baglanti = sqlite3.connect("haberler.db")
    imlec = baglanti.cursor()

    imlec.execute("""
    CREATE TABLE IF NOT EXISTS haberler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        baslik TEXT UNIQUE,
        icerik TEXT,
        link TEXT,
        kategori TEXT,
        resim_url TEXT,
        dil TEXT,
        kaynak TEXT
    )
    """)
    baglanti.commit()

    kaynaklar = [

        {"url": "https://www.ntv.com.tr/gundem.rss", "dil": "TR", "varsayilan": "Türkiye", "ad": "NTV Gündem"},
        {"url": "https://www.haberturk.com/rss/gundem.xml", "dil": "TR", "varsayilan": "Türkiye", "ad": "HT Gündem"},
        {"url": "https://www.cnnturk.com/feed/rss/turkiye/news", "dil": "TR", "varsayilan": "Türkiye",
         "ad": "CNN Türk"},
        {"url": "https://www.trt.net.tr/rss/gundem.rss", "dil": "TR", "varsayilan": "Türkiye", "ad": "TRT Gündem"},
        {"url": "https://www.sabah.com.tr/rss/gundem.xml", "dil": "TR", "varsayilan": "Türkiye", "ad": "Sabah Gündem"},
        {"url": "https://www.hurriyet.com.tr/rss/gundem", "dil": "TR", "varsayilan": "Türkiye",
         "ad": "Hürriyet Gündem"},

        {"url": "https://www.aspor.com.tr/rss/anasayfa.xml", "dil": "TR", "varsayilan": "Spor", "ad": "A Spor"},
        {"url": "https://www.ntvspor.net/rss", "dil": "TR", "varsayilan": "Spor", "ad": "NTV Spor"},
        {"url": "https://www.trtspor.com.tr/rss/sondakika.rss", "dil": "TR", "varsayilan": "Spor", "ad": "TRT Spor"},
        {"url": "https://www.haberturk.com/rss/spor.xml", "dil": "TR", "varsayilan": "Spor", "ad": "HT Spor"},

        {"url": "https://www.haberturk.com/rss/ekonomi.xml", "dil": "TR", "varsayilan": "Ekonomi", "ad": "HT Ekonomi"},
        {"url": "https://www.cnnturk.com/feed/rss/ekonomi/news", "dil": "TR", "varsayilan": "Ekonomi",
         "ad": "CNN Ekonomi"},
        {"url": "https://www.donanimhaber.com/rss/tum/", "dil": "TR", "varsayilan": "Teknoloji", "ad": "DonanımHaber"},
        {"url": "https://www.haberturk.com/rss/teknoloji.xml", "dil": "TR", "varsayilan": "Teknoloji",
         "ad": "HT Teknoloji"},
        {"url": "https://www.haberturk.com/rss/saglik.xml", "dil": "TR", "varsayilan": "Sağlık", "ad": "HT Sağlık"},


        {"url": "http://rss.cnn.com/rss/edition_world.rss", "dil": "EN", "varsayilan": "Dünya", "ad": "CNN World"},
        {"url": "http://feeds.bbci.co.uk/news/world/rss.xml", "dil": "EN", "varsayilan": "Dünya", "ad": "BBC World"},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "dil": "EN", "varsayilan": "Dünya",
         "ad": "NYT World"},
        {"url": "http://feeds.bbci.co.uk/sport/rss.xml", "dil": "EN", "varsayilan": "Spor", "ad": "BBC Sport"},
        {"url": "https://www.espn.com/espn/rss/news", "dil": "EN", "varsayilan": "Spor", "ad": "ESPN"},
        {"url": "https://techcrunch.com/feed/", "dil": "EN", "varsayilan": "Teknoloji", "ad": "TechCrunch"},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml", "dil": "EN", "varsayilan": "Sağlık",
         "ad": "NYT Health"},
        {"url": "https://finance.yahoo.com/news/rss", "dil": "EN", "varsayilan": "Ekonomi", "ad": "Yahoo Finance"},



        {"url": "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml", "dil": "ES", "varsayilan": "Dünya",
         "ad": "El Mundo"},
        {"url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada", "dil": "ES", "varsayilan": "Dünya",
         "ad": "El País"},
        {"url": "https://www.abc.es/rss/feeds/abc_ultima.xml", "dil": "ES", "varsayilan": "Dünya", "ad": "ABC España"},
        {"url": "https://e00-marca.uecdn.es/rss/portada.xml", "dil": "ES", "varsayilan": "Spor", "ad": "Marca"},
        {"url": "https://as.com/rss/tags/ultimas_noticias.xml", "dil": "ES", "varsayilan": "Spor", "ad": "Diario AS"},
        {"url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/tecnologia/portada", "dil": "ES",
         "varsayilan": "Teknoloji", "ad": "El País Tech"},
        {"url": "https://e00-expansion.uecdn.es/rss/portada.xml", "dil": "ES", "varsayilan": "Ekonomi",
         "ad": "Expansión"},
        {"url": "https://www.abc.es/rss/feeds/abc_salud.xml", "dil": "ES", "varsayilan": "Sağlık", "ad": "ABC Salud"}

    ]

    kara_liste = [
        "Yayın Akışı", "Programlar", "Ekran Yüzleri", "Canlı Yayın", "Frekanslar",
        "WhatsApp", "Linki Kopyala", "Yazıyı Büyüt", "Yazıyı Küçült", "Resmi İlanlar",
        "Demirören", "Sitene Ekle", "Günün Manşetleri", "Son Dakika", "Foto Galeri",
        "deneyimli editör", "notlarını aktarmaya", "devam ediyor", "Abone ol", "tıklayınız", "tıklayın",
        "EN ÇOK OKUNANLAR", "Aktüel", "Kataloğu", "Aldın Aldın", "Fırsatlarında", "İlginizi Çekebilir",
        "Sign up for", "Subscribe", "Read more", "Share this", "Follow us"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,tr;q=0.8"
    }

    print(" YABANCI DİL ÇÖZÜCÜ VE TÜM KATEGORİLERİ DOLDURAN BOT SAHADA!\n")

    while True:
        imlec.execute("SELECT baslik FROM haberler ORDER BY id DESC LIMIT 200")
        eski_basliklar = [satir[0] for satir in imlec.fetchall()]
        tum_haberler_havuzu = []

        for kaynak in kaynaklar:
            print(f" {kaynak['ad']} taranıyor...")
            try:
                cevap = requests.get(kaynak["url"], headers=headers, timeout=10)
                cevap.encoding = cevap.apparent_encoding
                haber_bloklari = re.findall(r'<(?:item|entry)>(.*?)</(?:item|entry)>', cevap.text,
                                            re.DOTALL | re.IGNORECASE)

                for blok in haber_bloklari[:4]:
                    ts = zaman_damgasi_al(blok)
                    tum_haberler_havuzu.append({'zaman': ts, 'blok': blok, 'kaynak': kaynak})
            except:
                pass

        tum_haberler_havuzu.sort(key=lambda x: x['zaman'])
        yeni_haber_sayisi = 0

        for item in tum_haberler_havuzu:
            blok = item['blok']
            kaynak = item['kaynak']

            baslik_bul = re.search(r'<title.*?>(.*?)</title>', blok, re.IGNORECASE)
            if not baslik_bul: continue
            temiz_baslik = baslik_bul.group(1).replace('<![CDATA[', '').replace(']]>', '').strip()
            temiz_baslik = re.sub(r'<[^>]+>', '', temiz_baslik)

            if haber_zaten_var_mi(temiz_baslik, eski_basliklar): continue

            link_bul = re.search(r'<link[^>]*href=["\'](.*?)["\']', blok, re.IGNORECASE)
            if not link_bul: link_bul = re.search(r'<link>(.*?)</link>', blok, re.IGNORECASE)
            haber_linki = link_bul.group(1).strip() if link_bul else ""

            resim = ""
            enclosure = re.search(r'<enclosure[^>]+url=["\'](.*?)["\']', blok, re.IGNORECASE)
            if enclosure: resim = enclosure.group(1)
            if not resim:
                media = re.search(r'<media:content[^>]+url=["\'](.*?)["\']', blok, re.IGNORECASE)
                if media: resim = media.group(1)
            if not resim:
                media_thumb = re.search(r'<media:thumbnail[^>]+url=["\'](.*?)["\']', blok, re.IGNORECASE)
                if media_thumb: resim = media_thumb.group(1)

            if not resim or len(resim) < 10:
                profesyonel_resim = resim_bul(haber_linki, headers)
                if profesyonel_resim: resim = profesyonel_resim

            tam_metin = ""
            try:
                site_cevap = requests.get(haber_linki, headers=headers, timeout=8)
                soup = BeautifulSoup(site_cevap.content, "html.parser")

                for trash in soup.find_all(['aside', 'nav', 'footer', 'script', 'style', 'header']):
                    trash.decompose()
                for trash in soup.find_all('div', class_=re.compile(
                        r'(related|popular|önerilen|ilgili|share|social|read-more|outbrain|taboola|widget|author|promo)',
                        re.I)):
                    trash.decompose()

                olasi_govdeler = soup.find_all(['article', 'main', 'section']) + soup.find_all('div', class_=re.compile(
                    r'(article|body|content|story|entry|page|detail|news|text)', re.I))

                article_body = soup
                max_p_sayisi = 0
                for govde in olasi_govdeler:
                    p_sayisi = len(govde.find_all('p'))
                    if p_sayisi > max_p_sayisi:
                        max_p_sayisi = p_sayisi
                        article_body = govde

                gecerli_paragraflar = []
                for etiket in article_body.find_all(['p', 'h2', 'h3']):
                    metin = etiket.text.strip()
                    link_etiketi = etiket.find('a')
                    if link_etiketi and len(metin) > 0:
                        if len(link_etiketi.text.strip()) / len(metin) > 0.7:
                            continue

                    if len(metin) > 25:
                        if not any(yasak.lower() in metin.lower() for yasak in kara_liste):
                            if metin not in gecerli_paragraflar:
                                gecerli_paragraflar.append(metin)

                tam_metin = "\n\n".join(gecerli_paragraflar)
            except:
                pass

            if len(tam_metin) < 150:
                ozet_bul = re.search(r'<description>(.*?)</description>', blok, re.IGNORECASE)
                tam_metin = re.sub(r'<[^>]+>', '', ozet_bul.group(1).replace('<![CDATA[', '').replace(']]>',
                                                                                                      '')).strip() if ozet_bul else ""

            if len(temiz_baslik) > 15:
                kategori = kaynak["varsayilan"]
                try:
                    imlec.execute(
                        "INSERT INTO haberler (baslik, icerik, link, kategori, resim_url, dil, kaynak) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (temiz_baslik, tam_metin, haber_linki, kategori, resim, kaynak["dil"], kaynak["ad"]))
                    baglanti.commit()
                    eski_basliklar.append(temiz_baslik)
                    print(f"   EKLENDİ [{kategori}]: {temiz_baslik[:40]}")
                    yeni_haber_sayisi += 1
                except sqlite3.IntegrityError:
                    pass

        if yeni_haber_sayisi == 0: print("️ Yeni gelişme yok.")
        print("\n💤 Tarama bitti. 5 dakika bekleniyor...\n")
        time.sleep(300)


if __name__ == "__main__":
    canli_akis_baslat()