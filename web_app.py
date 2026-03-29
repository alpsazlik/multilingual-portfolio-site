import flet as ft
import sqlite3
import json
import os
import webbrowser
import threading
import time

AYARLAR_DOSYASI = "ayarlar.json"


def ayarlari_oku():
    if os.path.exists(AYARLAR_DOSYASI):
        try:
            with open(AYARLAR_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"diller": ["TR"], "tema": "dark", "bildirim_acik": True, "favoriler": []}


def ayarlari_yaz(diller, tema, bildirim_acik, favoriler):
    with open(AYARLAR_DOSYASI, "w", encoding="utf-8") as f:
        json.dump({"diller": diller, "tema": tema, "bildirim_acik": bildirim_acik, "favoriler": favoriler}, f)


def web_ekrani(page: ft.Page):
    page.title = "GUNDEM GLOBAL"
    page.padding = 0
    page.horizontal_alignment = "center"
    page.scroll = "auto"

    ayarlar = ayarlari_oku()
    aktif_dil = "TR"
    kayitli_tema = ayarlar.get("tema", "dark")
    kayitli_favoriler = ayarlar.get("favoriler", [])

    page.theme_mode = ft.ThemeMode.DARK if kayitli_tema == "dark" else ft.ThemeMode.LIGHT
    page.bgcolor = "#0F172A" if page.theme_mode == ft.ThemeMode.DARK else "#F3F4F6"

    aktif_kategori = "Tümü"
    arama_metni = ""

    tercumeler = {
        "TR": ["Tümü", "Türkiye", "Teknoloji", "Spor", "Ekonomi", "Dünya", "Sağlık"],
        "EN": ["All", "Turkey", "Technology", "Sports", "Economy", "World", "Health"],
        "ES": ["Todos", "Turquía", "Tecnología", "Deportes", "Economía", "Mundo", "Salud"]
    }

    ui_metinleri = {
        "TR": {"ara": "Ara...", "geri": "Geri", "ozet_baslik": "Yapay Zeka Ozeti", "ozet_btn": "Ozet",
               "kaynak": "Kaynak", "orijinal_gor": "Orijinalini Gor", "islem": "Islem yapiliyor...",
               "hata": "Hata olustu.", "tercume_edildi": "Tercume Edildi.", "haberi_oku": "Haberi Oku"},
        "EN": {"ara": "Search...", "geri": "Back", "ozet_baslik": "AI Summary", "ozet_btn": "Summary",
               "kaynak": "Source", "orijinal_gor": "View Original", "islem": "Processing...", "hata": "Error occurred.",
               "tercume_edildi": "Translated.", "haberi_oku": "Read Article"},
        "ES": {"ara": "Buscar...", "geri": "Atras", "ozet_baslik": "Resumen de IA", "ozet_btn": "Resumen",
               "kaynak": "Fuente", "orijinal_gor": "Ver Original", "islem": "Procesando...",
               "hata": "Ocurrio un error.", "tercume_edildi": "Traducido.", "haberi_oku": "Leer Articulo"}
    }

    def text_color():
        return "white" if page.theme_mode == ft.ThemeMode.DARK else "#111827"

    def subtext_color():
        return "#9CA3AF" if page.theme_mode == ft.ThemeMode.DARK else "#4B5563"

    def card_bg():
        return "#1E293B" if page.theme_mode == ft.ThemeMode.DARK else "white"

    def border_col():
        return "#334155" if page.theme_mode == ft.ThemeMode.DARK else "#E5E7EB"

    def verileri_cek():
        try:
            baglanti = sqlite3.connect("haberler.db")
            imlec = baglanti.cursor()
            imlec.execute(
                "SELECT id, baslik, icerik, link, kategori, resim_url, dil, kaynak FROM haberler ORDER BY id DESC LIMIT 200")
            ver = imlec.fetchall()
            baglanti.close()
            return ver
        except:
            return []

    def metni_temizle(ham_metin):
        if not ham_metin: return ""
        yasaklar = ["tiklayiniz", "amazon.", "http", "www"]
        temiz_satirlar = [s.strip() for s in ham_metin.split('\n') if
                          s.strip() and not any(y in s.lower() for y in yasaklar)]
        return "\n\n".join(temiz_satirlar)

    def favori_islem(e):
        h_id = e.control.data
        if h_id in kayitli_favoriler:
            kayitli_favoriler.remove(h_id)
        else:
            kayitli_favoriler.append(h_id)
        ayarlari_yaz([aktif_dil], page.theme_mode.name.lower(), True, kayitli_favoriler)
        haberleri_goster_web()

    def haber_karti_olustur(h_id, baslik, icerik, link, kategori, resim, dil, kaynak):
        gecerli_resim = resim if (resim and len(resim) > 10) else f"https://picsum.photos/seed/{h_id}/700/350"
        is_fav = h_id in kayitli_favoriler

        try:
            kat_idx = tercumeler["TR"].index(kategori)
            gosterilecek_kategori = tercumeler[aktif_dil][kat_idx]
        except:
            gosterilecek_kategori = kategori

        return ft.Container(
            bgcolor=card_bg(), border_radius=12, border=ft.border.all(1, border_col()),
            padding=20, on_click=haberi_oku_web, ink=True,
            data={"id": h_id, "baslik": baslik, "icerik": icerik, "link": link, "resim": gecerli_resim,
                  "kategori": gosterilecek_kategori, "kaynak": kaynak, "dil": dil},
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(gosterilecek_kategori.upper(), size=10, weight="bold", color="white"),
                            bgcolor="#3B82F6", padding=ft.padding.symmetric(6, 12), border_radius=4),
                        ft.Text(f"{kaynak}", color=subtext_color(), size=12)
                    ], spacing=10),
                    ft.IconButton(icon=ft.Icons.BOOKMARK if is_fav else ft.Icons.BOOKMARK_BORDER,
                                  icon_color="#3B82F6" if is_fav else subtext_color(), on_click=favori_islem, data=h_id)
                ], alignment="spaceBetween"),
                ft.Text(baslik, size=22, weight="w900", color=text_color()),
                ft.Image(src=gecerli_resim, width=float('inf'), height=350, fit="cover", border_radius=8,
                         error_content=ft.Container(bgcolor="#334155", content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED))),
                ft.Container(content=ft.Row([ft.Icon(ft.Icons.MENU_BOOK, size=18, color="white"),
                                             ft.Text(ui_metinleri[aktif_dil]["haberi_oku"], weight="bold",
                                                     color="white")], alignment="center"), bgcolor="#2563EB",
                             padding=12, border_radius=8)
            ], spacing=15)
        )

    def haberleri_goster_web():
        veriler = verileri_cek()
        haber_listesi.controls.clear()
        for h in veriler:
            if h[6] == aktif_dil:
                idx = tercumeler[aktif_dil].index(aktif_kategori) if aktif_kategori in tercumeler[aktif_dil] else 0
                tr_kategori = tercumeler["TR"][idx]
                if tr_kategori == "Tümü" or h[4] == tr_kategori:
                    if not arama_metni or arama_metni in h[1].lower():
                        haber_listesi.controls.append(
                            haber_karti_olustur(h[0], h[1], h[2], h[3], h[4], h[5], h[6], h[7]))
        page.update()

    def dil_degistir(e):
        nonlocal aktif_dil, aktif_kategori
        aktif_dil = e.control.data
        aktif_kategori = tercumeler[aktif_dil][0]

        for btn in dil_secici.controls:
            btn.bgcolor = "#2563EB" if btn.data == aktif_dil else "transparent"
            btn.content.color = "white" if btn.data == aktif_dil else subtext_color()

        arama_kutusu_web.hint_text = ui_metinleri[aktif_dil]["ara"]
        btn_geri.text = ui_metinleri[aktif_dil]["geri"]
        ozet_baslik_metni.value = ui_metinleri[aktif_dil]["ozet_baslik"]
        btn_ozet_metin.value = ui_metinleri[aktif_dil]["ozet_btn"]
        btn_orijinal_git_metin.value = ui_metinleri[aktif_dil]["kaynak"]
        btn_orijinal_metin.value = ui_metinleri[aktif_dil]["orijinal_gor"]

        kategori_butonlarini_guncelle()
        haberleri_goster_web()

    def kategori_secildi(e):
        nonlocal aktif_kategori
        aktif_kategori = e.control.data
        for btn in kategori_satiri.controls:
            btn.bgcolor = "#3B82F6" if btn.data == aktif_kategori else "transparent"
            btn.content.color = "white" if btn.data == aktif_kategori else subtext_color()
        haberleri_goster_web()

    def kategori_butonlarini_guncelle():
        kategori_satiri.controls.clear()
        for kat in tercumeler[aktif_dil]:
            kategori_satiri.controls.append(
                ft.Container(
                    content=ft.Text(kat, weight="bold", color="white" if kat == aktif_kategori else subtext_color()),
                    padding=ft.padding.symmetric(10, 20), border_radius=20,
                    bgcolor="#3B82F6" if kat == aktif_kategori else "transparent",
                    data=kat, on_click=kategori_secildi, ink=True
                )
            )
        page.update()

    def haberi_oku_web(e):
        h = e.control.data
        detay_resim.src = h["resim"]
        detay_baslik.value = h["baslik"]
        temiz_icerik = metni_temizle(h["icerik"])
        detay_icerik.value = temiz_icerik
        detay_kaynak.value = f"{ui_metinleri[aktif_dil]['kaynak']}: {h['kaynak']}"
        btn_orijinal.data = h["link"]

        btn_ozet.data = h["icerik"]
        btn_cevir_tr.data = h["icerik"]
        btn_cevir_en.data = h["icerik"]
        btn_cevir_es.data = h["icerik"]

        btn_cevir_tr.visible = h["dil"] != "TR"
        btn_cevir_en.visible = h["dil"] != "EN"
        btn_cevir_es.visible = h["dil"] != "ES"

        btn_orijinal_metin_kutu.data = temiz_icerik
        btn_orijinal_metin_kutu.visible = False
        ozet_kutusu.visible = False

        ana_akis.visible = False
        detay_sayfasi.visible = True
        page.scroll_to(0)
        page.update()

    def orijinali_goster(e):
        detay_icerik.value = e.control.data
        btn_orijinal_metin_kutu.visible = False
        ozet_kutusu.visible = False
        page.update()

    def yapay_zeka_islem(e, mod, hedef_dil):
        ozet_kutusu.visible = True
        ozet_metni.value = ui_metinleri[aktif_dil]["islem"]
        page.update()

        def baslat():
            try:
                if mod == "ozet":
                    time.sleep(1)
                    ozet_metni.value = e.control.data[:400] + "..."
                else:
                    from deep_translator import GoogleTranslator
                    ceviri = GoogleTranslator(source='auto', target=hedef_dil).translate(e.control.data[:1000])
                    detay_icerik.value = ceviri
                    ozet_metni.value = ui_metinleri[aktif_dil]["tercume_edildi"]
                    btn_orijinal_metin_kutu.visible = True
            except:
                ozet_metni.value = ui_metinleri[aktif_dil]["hata"]
            page.update()

        threading.Thread(target=baslat).start()

    dil_secici = ft.Row([
        ft.Container(content=ft.Text(d, weight="bold", color="white" if d == "TR" else subtext_color()), padding=10,
                     border_radius=8, data=d, on_click=dil_degistir, bgcolor="#2563EB" if d == "TR" else "transparent")
        for d in ["TR", "EN", "ES"]
    ], alignment="center", spacing=20)

    arama_kutusu_web = ft.TextField(hint_text=ui_metinleri[aktif_dil]["ara"], width=250, border_radius=20,
                                    content_padding=10, on_change=lambda e: setattr(page, 'arama_metni',
                                                                                    e.control.value.lower()) or haberleri_goster_web())

    ust_bar = ft.Container(
        bgcolor=card_bg(), padding=20, border=ft.border.only(bottom=ft.border.BorderSide(1, border_col())),
        content=ft.Row([
            ft.Text("GUNDEM.", size=26, weight="w900", color="#3B82F6"),
            arama_kutusu_web,
            dil_secici
        ], alignment="spaceBetween")
    )

    kategori_satiri = ft.Row(alignment="center", spacing=10, wrap=True)
    haber_listesi = ft.Column(width=700)
    ana_akis = ft.Column([ft.Container(kategori_satiri, padding=20), haber_listesi], horizontal_alignment="center")

    detay_resim = ft.Image(src="", width=float('inf'), height=400, fit="cover", border_radius=10)
    detay_baslik = ft.Text(size=30, weight="bold")
    detay_icerik = ft.Text(size=18)
    detay_kaynak = ft.Text(color=subtext_color())

    ozet_baslik_metni = ft.Text(ui_metinleri[aktif_dil]["ozet_baslik"], weight="bold", color="#FBBF24", size=16)
    ozet_metni = ft.Text(color="#FBBF24", italic=True)
    ozet_kutusu = ft.Container(
        content=ft.Column([ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME, color="#FBBF24"), ozet_baslik_metni]), ozet_metni]),
        visible=False, bgcolor="#1E293B", padding=20, border_radius=10)

    btn_ozet_metin = ft.Text(ui_metinleri[aktif_dil]["ozet_btn"], color="white")
    btn_ozet = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.AUTO_AWESOME, color="white"), btn_ozet_metin], alignment="center"),
        bgcolor="#2563EB", padding=10, border_radius=8, on_click=lambda e: yapay_zeka_islem(e, "ozet", ""), data="")

    btn_cevir_tr = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.TRANSLATE, color="white"), ft.Text("TR Cevir", color="white")],
                       alignment="center"), bgcolor="#16A34A", padding=10, border_radius=8,
        on_click=lambda e: yapay_zeka_islem(e, "cevir", "tr"), data="")
    btn_cevir_en = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.TRANSLATE, color="white"), ft.Text("EN Translate", color="white")],
                       alignment="center"), bgcolor="#9333EA", padding=10, border_radius=8,
        on_click=lambda e: yapay_zeka_islem(e, "cevir", "en"), data="")
    btn_cevir_es = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.TRANSLATE, color="white"), ft.Text("ES Traducir", color="white")],
                       alignment="center"), bgcolor="#E11D48", padding=10, border_radius=8,
        on_click=lambda e: yapay_zeka_islem(e, "cevir", "es"), data="")

    btn_orijinal_git_metin = ft.Text(ui_metinleri[aktif_dil]["kaynak"], color="white")
    btn_orijinal = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.OPEN_IN_NEW, color="white"), btn_orijinal_git_metin], alignment="center"),
        bgcolor="#475569", padding=10, border_radius=8, on_click=lambda e: webbrowser.open(e.control.data), data="")

    btn_orijinal_metin = ft.Text(ui_metinleri[aktif_dil]["orijinal_gor"], color="white")
    btn_orijinal_metin_kutu = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.RESTORE, color="white"), btn_orijinal_metin], alignment="center"),
        bgcolor="#F59E0B", padding=10, border_radius=8, on_click=orijinali_goster, data="", visible=False)

    butonlar_satiri = ft.Row(
        [btn_ozet, btn_cevir_tr, btn_cevir_en, btn_cevir_es, btn_orijinal_metin_kutu, btn_orijinal], wrap=True)

    btn_geri = ft.TextButton(ui_metinleri[aktif_dil]["geri"],
                             on_click=lambda _: [setattr(detay_sayfasi, 'visible', False),
                                                 setattr(ana_akis, 'visible', True), page.update()])

    detay_sayfasi = ft.Container(
        visible=False, width=700, padding=40,
        content=ft.Column([
            btn_geri,
            detay_baslik, detay_resim,
            butonlar_satiri,
            ozet_kutusu, detay_icerik, detay_kaynak
        ], spacing=20)
    )

    page.add(ust_bar, ana_akis, detay_sayfasi)
    kategori_butonlarini_guncelle()
    haberleri_goster_web()


if __name__ == "__main__":
    ft.run(main=web_ekrani, view=ft.AppView.WEB_BROWSER)