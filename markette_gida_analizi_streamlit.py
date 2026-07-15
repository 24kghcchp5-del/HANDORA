#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markette Gıda Analizi - Streamlit Web Versiyonu (v2.1 Web)
Hem bilgisayar hem cep telefonu için optimize edilmiştir.
Kullanıcılar tarayıcıdan açar, "Ana Ekrana Ekle" ile uygulama gibi kullanabilir.

Kurulum:
    pip install streamlit pandas matplotlib requests

Çalıştırma:
    streamlit run markette_gida_analizi_streamlit.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
import re
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="🛒 Markette Gıda Analizi",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# VERİ VE OTURUM DURUMU
# ============================================
if "sepet" not in st.session_state:
    st.session_state.sepet = []

# Demo ürün veritabanı (kısaltılmış hali)
products_data = [
    {"id": 1, "ad": "Tam Yağlı İnek Sütü (1 L)", "kategori": "Süt ve Süt Ürünleri", "barkod": "8690526001234",
     "fiyat_tl": 34.90, "paket_agirlik_g": 1000, "kcal_100g": 64, "protein_100g": 3.3, "karb_100g": 4.8,
     "yag_100g": 3.6, "seker_100g": 4.8, "lif_100g": 0.0, "tuz_100g": 0.1, "alerjenler": "Süt (laktoz)"},
    {"id": 2, "ad": "Tam Buğday Ekmeği (500 g)", "kategori": "Fırın ve Tahıl Ürünleri", "barkod": "8690123456789",
     "fiyat_tl": 18.50, "paket_agirlik_g": 500, "kcal_100g": 240, "protein_100g": 9.5, "karb_100g": 42.0,
     "yag_100g": 2.5, "seker_100g": 2.0, "lif_100g": 6.0, "tuz_100g": 1.0, "alerjenler": "Gluten (Buğday)"},
    {"id": 3, "ad": "Tavuk Göğsü (1 kg)", "kategori": "Et ve Tavuk", "barkod": "8699876543210",
     "fiyat_tl": 115.00, "paket_agirlik_g": 1000, "kcal_100g": 110, "protein_100g": 23.0,
     "karb_100g": 0.0, "yag_100g": 1.5, "seker_100g": 0.0, "lif_100g": 0.0, "tuz_100g": 0.1, "alerjenler": "Yok"},
    {"id": 4, "ad": "Elma (1 kg)", "kategori": "Meyve ve Sebze", "barkod": "8691111222233",
     "fiyat_tl": 24.90, "paket_agirlik_g": 1000, "kcal_100g": 52, "protein_100g": 0.3, "karb_100g": 14.0,
     "yag_100g": 0.2, "seker_100g": 10.0, "lif_100g": 2.4, "tuz_100g": 0.0, "alerjenler": "Yok"},
    {"id": 5, "ad": "Muz (1 kg)", "kategori": "Meyve ve Sebze", "barkod": "8692222333344",
     "fiyat_tl": 32.50, "paket_agirlik_g": 1000, "kcal_100g": 89, "protein_100g": 1.1, "karb_100g": 23.0,
     "yag_100g": 0.3, "seker_100g": 12.0, "lif_100g": 2.6, "tuz_100g": 0.0, "alerjenler": "Yok"},
    {"id": 6, "ad": "Doğal Yoğurt (1 kg)", "kategori": "Süt ve Süt Ürünleri", "barkod": "8693333444455",
     "fiyat_tl": 42.00, "paket_agirlik_g": 1000, "kcal_100g": 62, "protein_100g": 4.0, "karb_100g": 5.0,
     "yag_100g": 3.5, "seker_100g": 4.5, "lif_100g": 0.0, "tuz_100g": 0.1, "alerjenler": "Süt (laktoz)"},
    {"id": 7, "ad": "Beyaz Pirinç (1 kg)", "kategori": "Temel Gıda", "barkod": "8694444555566",
     "fiyat_tl": 38.90, "paket_agirlik_g": 1000, "kcal_100g": 360, "protein_100g": 7.0, "karb_100g": 78.0,
     "yag_100g": 0.6, "seker_100g": 0.5, "lif_100g": 1.5, "tuz_100g": 0.0, "alerjenler": "Yok"},
    {"id": 8, "ad": "Makarna (500 g)", "kategori": "Temel Gıda", "barkod": "8695555666677",
     "fiyat_tl": 19.90, "paket_agirlik_g": 500, "kcal_100g": 355, "protein_100g": 12.0, "karb_100g": 70.0,
     "yag_100g": 1.5, "seker_100g": 2.5, "lif_100g": 3.0, "tuz_100g": 0.5, "alerjenler": "Gluten (Buğday)"},
    {"id": 9, "ad": "Dana Kıyma (500 g)", "kategori": "Et ve Tavuk", "barkod": "8696666777788",
     "fiyat_tl": 95.00, "paket_agirlik_g": 500, "kcal_100g": 250, "protein_100g": 18.0,
     "karb_100g": 0.0, "yag_100g": 20.0, "seker_100g": 0.0, "lif_100g": 0.0, "tuz_100g": 0.1, "alerjenler": "Yok"},
    {"id": 10, "ad": "Kaşar Peyniri (250 g)", "kategori": "Süt ve Süt Ürünleri", "barkod": "8697777888899",
     "fiyat_tl": 65.00, "paket_agirlik_g": 250, "kcal_100g": 340, "protein_100g": 25.0, "karb_100g": 1.0,
     "yag_100g": 26.0, "seker_100g": 0.5, "lif_100g": 0.0, "tuz_100g": 1.8, "alerjenler": "Süt (laktoz)"},
]

df_products = pd.DataFrame(products_data)

def get_product_by_id(pid):
    matches = df_products[df_products["id"] == pid]
    return matches.iloc[0].to_dict() if not matches.empty else None

# ============================================
# OPEN FOOD FACTS FONKSİYONLARI
# ============================================
def fetch_product_from_off(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    params = {"fields": "product_name,brands,categories_tags,quantity,nutriments,allergens_tags"}
    try:
        r = requests.get(url, params=params, timeout=8, headers={"User-Agent": "GidaAnalizWeb/2.1"})
        if r.status_code != 200:
            return None, f"API hatası ({r.status_code})"
        data = r.json()
        if data.get("status") != 1 or "product" not in data:
            return None, "Ürün Open Food Facts'te bulunamadı."
        p = data["product"]
        name = p.get("product_name") or p.get("brands", "Bilinmeyen Ürün")
        qty_str = str(p.get("quantity", "")).lower()
        package_g = 100
        m = re.search(r'(\d+[\.,]?\d*)\s*(g|ml|kg)', qty_str)
        if m:
            val = float(m.group(1).replace(",", "."))
            if m.group(2) == "kg": package_g = int(val * 1000)
            else: package_g = int(val)
        n = p.get("nutriments", {})
        def gn(k, d=0.0): 
            v = n.get(k)
            return float(v) if v is not None else d
        kcal = gn("energy-kcal_100g")
        if kcal == 0 and gn("energy_100g") > 0:
            kcal = gn("energy_100g") / 4.184
        all_tags = p.get("allergens_tags", []) or []
        alerjen = ", ".join([t.replace("en:", "").replace("tr:", "").title() for t in all_tags]) if all_tags else "Yok"
        cat = (p.get("categories_tags", []) or [""])[0].replace("en:", "").replace("-", " ").title() or "Diğer"
        return {
            "name": name, "kategori": cat, "package_g": package_g,
            "kcal_100g": round(kcal, 1), "protein_100g": round(gn("proteins_100g"), 1),
            "karb_100g": round(gn("carbohydrates_100g"), 1), "yag_100g": round(gn("fat_100g"), 1),
            "seker_100g": round(gn("sugars_100g"), 1), "lif_100g": round(gn("fiber_100g"), 1),
            "tuz_100g": round(gn("salt_100g"), 1), "alerjenler": alerjen
        }, None
    except Exception as e:
        return None, f"Bağlantı hatası: {str(e)}"

def search_off_by_name(query):
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {"search_terms": query, "json": 1, "page_size": 6,
              "fields": "product_name,brands,code,categories_tags"}
    try:
        r = requests.get(url, params=params, timeout=8, headers={"User-Agent": "GidaAnalizWeb/2.1"})
        if r.status_code != 200: return []
        return r.json().get("products", [])
    except:
        return []

# ============================================
# SEPET İŞLEMLERİ
# ============================================
def add_to_sepet(pid, qty=1):
    for item in st.session_state.sepet:
        if item["id"] == pid:
            item["miktar"] += qty
            return
    st.session_state.sepet.append({"id": pid, "miktar": qty})

def remove_from_sepet(pid):
    st.session_state.sepet = [item for item in st.session_state.sepet if item["id"] != pid]

def calculate_nutrition():
    if not st.session_state.sepet:
        return None
    totals = {"fiyat": 0.0, "agirlik_g": 0.0, "kcal": 0.0, "protein": 0.0,
              "karb": 0.0, "yag": 0.0, "seker": 0.0, "lif": 0.0, "tuz": 0.0}
    alerjen_set = set()
    details = []
    for item in st.session_state.sepet:
        prod = get_product_by_id(item["id"])
        if not prod: continue
        mult = (item["miktar"] * prod["paket_agirlik_g"]) / 100.0
        totals["fiyat"] += prod["fiyat_tl"] * item["miktar"]
        totals["agirlik_g"] += item["miktar"] * prod["paket_agirlik_g"]
        totals["kcal"] += prod["kcal_100g"] * mult
        totals["protein"] += prod["protein_100g"] * mult
        totals["karb"] += prod["karb_100g"] * mult
        totals["yag"] += prod["yag_100g"] * mult
        totals["seker"] += prod["seker_100g"] * mult
        totals["lif"] += prod["lif_100g"] * mult
        totals["tuz"] += prod["tuz_100g"] * mult
        if prod["alerjenler"] != "Yok":
            alerjen_set.add(prod["alerjenler"])
        details.append({
            "ad": prod["ad"], "miktar": item["miktar"],
            "kcal": round(prod["kcal_100g"] * mult, 1),
            "protein": round(prod["protein_100g"] * mult, 1),
            "fiyat": round(prod["fiyat_tl"] * item["miktar"], 2)
        })
    daily = {"kcal": 2000, "protein": 60, "karb": 250, "yag": 70, "seker": 50, "tuz": 5}
    perc = {k: min(100, round((totals[k] / daily[k]) * 100, 1)) for k in ["kcal", "protein", "karb", "yag"]}
    return {"totals": totals, "perc": perc, "daily": daily, "alerjenler": list(alerjen_set), "details": details}

# ============================================
# ARAYÜZ
# ============================================
st.title("🛒 Markette Gıda Analizi")
st.caption("Web versiyonu • Cep telefonunda da rahat çalışır • Open Food Facts entegrasyonlu")

# Sidebar - Hızlı Sepet Özeti
with st.sidebar:
    st.header("🛍️ Sepet Özeti")
    if st.session_state.sepet:
        total_cost = sum(
            get_product_by_id(item["id"])["fiyat_tl"] * item["miktar"] 
            for item in st.session_state.sepet if get_product_by_id(item["id"])
        )
        st.metric("Toplam Tutar", f"{total_cost:,.2f} ₺")
        st.write(f"**{len(st.session_state.sepet)}** farklı ürün")
        if st.button("Sepeti Temizle", type="secondary"):
            st.session_state.sepet = []
            st.rerun()
    else:
        st.info("Sepet boş")

# Ana Sekmeler
tab1, tab2, tab3, tab4 = st.tabs(["📋 Ürünler & Sepete Ekle", "📡 Open Food Facts'ten Ekle", "🛒 Sepetim", "📊 Besin Analizi"])

# --- Sekme 1: Yerel Ürünler ---
with tab1:
    st.subheader("Yerel Ürün Veritabanı")
    search_term = st.text_input("Ürün ara (isim veya kategori)", placeholder="süt, ekmek, elma...")
    
    filtered = df_products
    if search_term:
        mask = (df_products["ad"].str.contains(search_term, case=False, na=False) |
                df_products["kategori"].str.contains(search_term, case=False, na=False))
        filtered = df_products[mask]
    
    for _, row in filtered.iterrows():
        col1, col2, col3 = st.columns([5, 2, 2])
        with col1:
            st.write(f"**{row['ad']}**")
            st.caption(f"{row['kategori']} • {row['barkod']}")
        with col2:
            st.write(f"**{row['fiyat_tl']:.2f} ₺** / {row['paket_agirlik_g']}g")
        with col3:
            qty = st.number_input(f"Adet_{row['id']}", min_value=1, value=1, step=1, 
                                  label_visibility="collapsed", key=f"qty_{row['id']}")
            if st.button("Sepete Ekle", key=f"add_{row['id']}", use_container_width=True):
                add_to_sepet(row["id"], qty)
                st.success(f"{qty} x {row['ad']} sepete eklendi!")
                st.rerun()

# --- Sekme 2: Open Food Facts ---
with tab2:
    st.subheader("Open Food Facts'ten Gerçek Ürün Ekle")
    
    method = st.radio("Yöntem seçin:", ["Barkod ile", "İsim ile ara"], horizontal=True)
    
    if method == "Barkod ile":
        barcode = st.text_input("Barkod numarası", placeholder="8690526001234")
        if st.button("Ürünü Getir", type="primary") and barcode:
            with st.spinner("Open Food Facts'ten veri alınıyor..."):
                prod, err = fetch_product_from_off(barcode)
            if err:
                st.error(err)
            else:
                st.success("Ürün bulundu!")
                st.json(prod)
                pkg = st.number_input("Paket ağırlığı (g)", value=prod["package_g"], step=10)
                price = st.number_input("Fiyat (₺)", value=25.0, step=0.5)
                qty = st.number_input("Kaç adet?", value=1, min_value=1)
                if st.button("Sepete Ekle (API Ürünü)"):
                    new_id = 100 + len(df_products)
                    new_row = {
                        "id": new_id, "ad": prod["name"][:60], "kategori": prod["kategori"],
                        "barkod": barcode, "fiyat_tl": price, "paket_agirlik_g": pkg,
                        "kcal_100g": prod["kcal_100g"], "protein_100g": prod["protein_100g"],
                        "karb_100g": prod["karb_100g"], "yag_100g": prod["yag_100g"],
                        "seker_100g": prod["seker_100g"], "lif_100g": prod["lif_100g"],
                        "tuz_100g": prod["tuz_100g"], "alerjenler": prod["alerjenler"]
                    }
                    global df_products
                    df_products = pd.concat([df_products, pd.DataFrame([new_row])], ignore_index=True)
                    add_to_sepet(new_id, qty)
                    st.success("Ürün sepete eklendi!")
                    st.rerun()
    
    else:  # İsim ile ara
        query = st.text_input("Ürün ismi veya marka yazın", placeholder="süt, çikolata, yoğurt...")
        if st.button("Ara") and query:
            with st.spinner("Open Food Facts'te aranıyor..."):
                results = search_off_by_name(query)
            if not results:
                st.warning("Sonuç bulunamadı.")
            else:
                for i, p in enumerate(results):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"**{p.get('product_name', 'Bilinmeyen')}**")
                        st.caption(f"{p.get('brands', '')} • Barkod: {p.get('code', '')}")
                    with col2:
                        if st.button("Seç", key=f"select_{i}"):
                            barcode = p.get("code")
                            if barcode:
                                prod, err = fetch_product_from_off(barcode)
                                if prod:
                                    st.session_state["selected_off_product"] = prod
                                    st.session_state["selected_barcode"] = barcode
                                    st.rerun()
    
    # Seçilen OFF ürününü ekleme formu
    if "selected_off_product" in st.session_state:
        prod = st.session_state["selected_off_product"]
        st.divider()
        st.subheader("Seçilen Ürün")
        st.write(f"**{prod['name']}**")
        pkg = st.number_input("Paket ağırlığı (g)", value=prod["package_g"], key="pkg_final")
        price = st.number_input("Fiyat (₺)", value=20.0, key="price_final")
        qty = st.number_input("Adet", value=1, min_value=1, key="qty_final")
        if st.button("Sepete Ekle"):
            new_id = 100 + len(df_products)
            new_row = {**prod, "id": new_id, "ad": prod["name"][:60], "fiyat_tl": price, "paket_agirlik_g": pkg, "barkod": st.session_state.get("selected_barcode", "")}
            df_products = pd.concat([df_products, pd.DataFrame([new_row])], ignore_index=True)
            add_to_sepet(new_id, qty)
            del st.session_state["selected_off_product"]
            st.success("Ürün sepete eklendi!")
            st.rerun()

# --- Sekme 3: Sepet ---
with tab3:
    st.subheader("Sepetiniz")
    if not st.session_state.sepet:
        st.info("Sepetiniz boş. Ürün ekleyin.")
    else:
        for item in st.session_state.sepet:
            prod = get_product_by_id(item["id"])
            if not prod: continue
            col1, col2, col3, col4 = st.columns([4, 1.5, 1.5, 1])
            with col1:
                st.write(f"**{prod['ad']}**")
            with col2:
                st.write(f"{item['miktar']} adet")
            with col3:
                st.write(f"{prod['fiyat_tl'] * item['miktar']:.2f} ₺")
            with col4:
                if st.button("Sil", key=f"del_{item['id']}", type="secondary"):
                    remove_from_sepet(item["id"])
                    st.rerun()
        st.divider()
        total = sum(get_product_by_id(i["id"])["fiyat_tl"] * i["miktar"] for i in st.session_state.sepet if get_product_by_id(i["id"]))
        st.metric("Sepet Toplamı", f"{total:,.2f} ₺")

# --- Sekme 4: Analiz ---
with tab4:
    st.subheader("Besin Analizi")
    data = calculate_nutrition()
    if not data:
        st.info("Analiz için sepete ürün ekleyin.")
    else:
        t = data["totals"]
        p = data["perc"]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Toplam Kalori", f"{t['kcal']:.0f} kcal", f"{p['kcal']}%")
        col2.metric("Protein", f"{t['protein']:.1f} g", f"{p['protein']}%")
        col3.metric("Karbonhidrat", f"{t['karb']:.1f} g", f"{p['karb']}%")
        col4.metric("Yağ", f"{t['yag']:.1f} g", f"{p['yag']}%")
        
        st.write(f"**Toplam Tutar:** {t['fiyat']:.2f} ₺ | **Ağırlık:** {t['agirlik_g']:.0f} g")
        
        # Uyarılar
        warnings = []
        if t["seker"] > 35: warnings.append("⚠️ Şeker miktarı yüksek!")
        if t["tuz"] > 4: warnings.append("⚠️ Tuz miktarı yüksek!")
        if t["protein"] < 30 and t["agirlik_g"] > 600: warnings.append("ℹ️ Protein alımı düşük görünüyor.")
        if warnings:
            for w in warnings:
                st.warning(w)
        
        if data["alerjenler"]:
            st.error(f"🚨 Alerjen: {', '.join(data['alerjenler'])}")
        
        # Basit grafik
        fig, ax = plt.subplots(figsize=(6, 4))
        macros = [t["protein"]*4, t["karb"]*4, t["yag"]*9]
        labels = ["Protein", "Karbonhidrat", "Yağ"]
        ax.pie(macros, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.set_title("Makro Dağılımı (Kalori Bazında)")
        st.pyplot(fig)
        
        # Rapor indirme
        if st.button("CSV Raporu İndir"):
            df_report = pd.DataFrame(data["details"])
            csv = df_report.to_csv(index=False).encode("utf-8")
            st.download_button("İndir", csv, "gida_analiz_raporu.csv", "text/csv")

st.caption("Bu web versiyonu bilgilendirme amaçlıdır. Gerçek ürün etiketlerini kontrol edin.")