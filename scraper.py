import requests
import xml.etree.ElementTree as ET
import sqlite3
import time
import os
from datetime import datetime

os.makedirs("data", exist_ok=True)

conn = sqlite3.connect("data/otomatik_haberler.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS haberler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        baslik TEXT UNIQUE,
        yapay_zeka_kategorisi TEXT,
        kayit_zamani TEXT
    )
''')
conn.commit()


API_URL = "http://127.0.0.1:8000/tahmin/"


RSS_LINKLERI = [
    "https://www.ntv.com.tr/spor.rss",
    "https://www.trthaber.com/bilim_teknoloji_articles.rss",
    "https://www.ntv.com.tr/ekonomi.rss",
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"
]


def otonom_botu_baslat():
    print(" Otonom Haber Avcısı Başlatıldı! İnternet taranıyor...")

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    yeni_haber_sayisi = 0

    for link in RSS_LINKLERI:
        print(f" Taranıyor: {link}")
        try:
            cevap = requests.get(link, headers=headers, timeout=10)
            root = ET.fromstring(cevap.content)

            for item in root.findall('.//item'):
                title = item.find('title')
                if title is not None and title.text:
                    baslik = title.text.strip()

                    if len(baslik) > 15:

                        cursor.execute("SELECT id FROM haberler WHERE baslik=?", (baslik,))
                        if cursor.fetchone() is None:

                            try:
                                api_cevabi = requests.post(API_URL, json={"metin": baslik}, timeout=5)

                                if api_cevabi.status_code == 200:
                                    yz_kategorisi = api_cevabi.json()["tahmin_edilen_kategori"]
                                    anlik_zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


                                    cursor.execute(
                                        "INSERT INTO haberler (baslik, yapay_zeka_kategorisi, kayit_zamani) VALUES (?, ?, ?)",
                                        (baslik, yz_kategorisi, anlik_zaman)
                                    )
                                    conn.commit()
                                    yeni_haber_sayisi += 1

                                    print(f" Yeni Haber Eklendi: [{yz_kategorisi}] -> {baslik[:60]}...")
                            except Exception as e:
                                print(f" API'ye ulaşılamadı (API çalışıyor mu?): {e}")

        except Exception as e:
            print(f" Kaynak okunamadı ({link}): {e}")

        time.sleep(2)

    print("=" * 60)
    print(
        f" Tur tamamlandı! Toplam {yeni_haber_sayisi} YENİ haber bulundu, yapay zeka ile etiketlendi ve veritabanına işlendi.")


if __name__ == "__main__":
    bekleme_suresi_dakika = 5
    print(f"Sistem Tam Otomatik Moda Geçti!")
    print(f"Bot arka planda sürekli çalışacak ve her {bekleme_suresi_dakika} dakikada bir uyanıp haber arayacak.")

    try:
        while True:
            print("=" * 50)
            otonom_botu_baslat()
            print("=" * 50)
            print(f"Bot görevini bitirdi ve uykuya daldı. {bekleme_suresi_dakika} dakika sonra tekrar uyanacak.")
            print("Durdurmak istersen terminaldeyken CTRL+C tuşlarına basasbilirsin. \n")

            time.sleep(bekleme_suresi_dakika * 60)

    except KeyboardInterrupt:
        print("\n Sistem manuel olarak durduruldu. Kapanıyor...")
    finally:
        conn.close()
        print("Veritabanı bağlantısı güvenlice kapatıldı.")