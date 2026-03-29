from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory="templates")

model_yolu = "./akilli_haber_modeli"
tokenizer = AutoTokenizer.from_pretrained(model_yolu)
model = AutoModelForSequenceClassification.from_pretrained(model_yolu)

kategoriler = ["Spor", "Türkiye", "Teknoloji", "Ekonomi", "Sağlık", "Dünya"]


class HaberIstegi(BaseModel):
    metin: str


@app.get("/")
async def ana_ekran(request: Request):
    try:
        baglanti = sqlite3.connect("haberler.db")
        imlec = baglanti.cursor()


        imlec.execute("SELECT baslik, kategori, resim_url FROM haberler ORDER BY id DESC LIMIT 50")
        kayitlar = imlec.fetchall()
        baglanti.close()


        haberler = [{"baslik": k[0], "kategori": k[1], "resim": k[2]} for k in kayitlar]
    except Exception as e:
        haberler = [{"baslik": "Henüz resimli haber yok. Botun çalışması bekleniyor...", "kategori": "Sistem",
                     "resim": "https://via.placeholder.com/300x200.png?text=Haber+Bekleniyor"}]

    return templates.TemplateResponse("index.html", {"request": request, "haberler": haberler})


@app.post("/tahmin/")
async def tahmin_et(istek: HaberIstegi):
    girdiler = tokenizer(istek.metin, return_tensors="pt", padding=True, truncation=True, max_length=128)
    ciktilar = model(**girdiler)
    tahmin_edilen_id = torch.argmax(ciktilar.logits, dim=1).item()
    kategori = kategoriler[tahmin_edilen_id]

    return {
        "orijinal_metin": istek.metin,
        "tahmin_edilen_kategori": kategori
    }