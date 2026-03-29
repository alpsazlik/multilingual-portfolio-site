import requests
import re
import pandas as pd
import time
import os

# --- VERSİYON 3.0: MEGA VERİ CANAVARI ---
# Dünyanın en büyük haber kaynaklarını ekledik!
RSS_KAYNAKLARI = {
    0: [  # SPOR (MARCA ve AS eklendi - Real Madrid'i ezberlemesi için!)
        "https://www.ntv.com.tr/spor.rss",
        "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/seccion/deportes/portada",
        "https://e00-marca.uecdn.es/rss/futbol/primera-division.xml",
        "https://as.com/rss/futbol/primera.xml",
        "http://feeds.bbci.co.uk/sport/football/rss.xml"
    ],
    1: [  # TÜRKİYE
        "https://www.ntv.com.tr/turkiye.rss",
        "https://www.trthaber.com/gundem_articles.rss"
    ],
    2: [  # TEKNOLOJİ
        "https://www.ntv.com.tr/teknoloji.rss",
        "http://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/seccion/tecnologia/portada",
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
    ],
    3: [  # EKONOMİ
        "https://www.ntv.com.tr/ekonomi.rss",
        "http://feeds.bbci.co.uk/news/business/rss.xml",
        "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/seccion/economia/portada",
        "https://search.cnbc.com/rs/search/combinedcms/view.xml?id=10000664"
    ],
    4: [  # SAĞLIK
        "https://www.ntv.com.tr/saglik.rss",
        "http://feeds.bbci.co.uk/news/health/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml"
    ],
    5: [  # DÜNYA
        "https://www.ntv.com.tr/dunya.rss",
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/seccion/internacional/portada",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://www.elmundo.es/rss/internacional.xml"
    ]
}


def egitim_verisi_topla():
    tum_haberler = []
    print("🌍 MEGA VERİ CANAVARI BAŞLATILDI! (Dünya Hortumlanıyor...)")
    print("-" * 60)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for kategori_id, linkler in RSS_KAYNAKLARI.items():
        for link in linkler:
            print(f"📡 Tarayıcı hücum ediyor (Kategori {kategori_id}): {link}")
            try:
                cevap = requests.get(link, headers=headers, timeout=10)
                basliklar = re.findall(r'<title>(.*?)</title>', cevap.text, re.IGNORECASE)

                for baslik in basliklar:
                    temiz_baslik = baslik.replace('<![CDATA[', '').replace(']]>', '').strip()
                    # Çöp başlıkları filtrele
                    if len(temiz_baslik) > 15 and "BBC" not in temiz_baslik and "NTV" not in temiz_baslik:
                        tum_haberler.append({'text': temiz_baslik, 'label': kategori_id})
            except Exception as e:
                pass  # Hatayı ekrana basıp vakit kaybetmeyelim, direkt devam!

            time.sleep(0.5)

    df = pd.DataFrame(tum_haberler)
    df = df.drop_duplicates(subset=['text'])

    print("\n" + "=" * 60)
    print(f"✅ GÖREV TAMAMLANDI! {len(df)} adet kusursuz veri çekildi.")

    os.makedirs("data/processed", exist_ok=True)
    # DİKKAT: Dosya adını v3 yaptık!
    kayit_yolu = "data/processed/cok_dilli_haberler_v3.csv"
    df.to_csv(kayit_yolu, index=False)
    print(f"💾 Mega Veri Seti '{kayit_yolu}' dosyasına başarıyla kaydedildi.")


if __name__ == "__main__":
    egitim_verisi_topla()