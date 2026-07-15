import streamlit as st
import pandas as pd
import requests
import re
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="🛒 Markette Gıda Analizi", page_icon="🛒", layout="wide")

# Oturum durumu
if "sepet" not in st.session_state:
    st.session_state.sepet = []

# Demo ürünler
data = [
    {"id": 1, "ad": "Tam Yağlı İnek Sütü (1 L)", "kategori": "Süt ve Süt Ürünleri", "barkod": "8690526001234", "fiyat_tl": 34.90, "paket_agirlik_g": 1000, "kcal_100g": 64, "protein_100g": 3.3, "karb_100g": 4.8, "yag_100g": 3.6, "seker_100g": 4.8, "lif_100g": 0.0, "tuz_100g": 0.1, "alerjenler": "Süt (laktoz)"},
    {"id": 2, "ad": "Tam Buğday Ekmeği (500 g)", "kategori": "Fırın ve Tahıl Ürünleri", "barkod": "8690123456789", "fiyat_tl": 18.50, "paket_agirlik_g": 500, "kcal_100g": 240, "protein_100g": 9.5, "karb_100g": 42.0, "yag_100g": 2.5, "seker_100g": 2.0, "lif_100g": 6.0, "tuz_100g": 1.0, "alerjenler": "Gluten (Buğday)"},
    {"id": 3, "ad": "Tavuk Göğsü (1 kg)", "kategori": "Et ve Tavuk", "barkod": "8699876543210", "fiyat_tl": 115.00, "paket_agirlik_g": 1000, "kcal_100g": 110, "protein_100g": 23.0, "karb_100g": 0.0, "yag_100g": 1.5, "seker_100g": 0.0, "lif_100g": 0.0, "tuz_100g": 0.1, "alerjenler": "Yok"},
    {"id": 4, "ad": "Elma (1 kg)", "kategori": "Meyve ve Sebze", "barkod": "8691111222233", "fiyat_tl": 24.90, "paket_agirlik_g": 1000, "kcal_100g": 52, "protein_100g": 0.3, "karb_100g": 14.0, "yag_100g": 0.2, "seker_100g": 10.0, "lif_100g": 2.4, "tuz_100g": 0.0, "alerjenler": "Yok"},
    {"id": 5, "ad": "Muz (1 kg)", "kategori": "Meyve ve Sebze", "barkod": "8692222333344", "fiyat_tl": 32.50, "paket_agirlik_g": 1000, "kcal_100g": 89, "protein_100g": 1.1, "karb_100g": 23.0, "yag_100g": 0.3, "seker_100g": 12.0, "lif_100g": 2.6, "tuz_100g": 0.0, "alerjenler": "Yok"},
    {"id": 6, "ad": "Doğal Yoğurt (1 kg)", "kategori": "Süt ve Süt Ürünleri", "barkod": "8693333444455", "fiyat_tl": 42.00, "paket_agirlik_g": 1000, "kcal_100g": 62, "protein_100g": 4.0, "karb_100g": 5.0, "yag_100g": 3.5, "seker_100g": 4.5, "lif_100g": 0.0, "tuz_100g": 0.1, "alerjenler": "Süt (laktoz)"},
]

df_products = pd.DataFrame(data)

def get_product_by_id(pid):
    matches = df_products[df_products["id"] == pid]
    return matches.iloc[0].to_dict() if not matches.empty else None

def fetch_product_from_off(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    params = {"fields": "product_name,brands,categories_tags,quantity,nutriments,allergens_tags"}
    try:
        r = requests.get(url, params=params, timeout=8, headers={"User-Agent": "GidaAnalizWeb/2.1"})
        if r.status_code != 200: return None, "API hatası"
        data = r.json()
        if data.get("status") != 1 or "product" not in data: return None, "Ürün bulunamadı"
        p = data["product"]
        name = p.get("product_name") or p.get("brands", "Bilinmeyen")
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
        kcal = gn("energy-kcal_100g") or (gn("energy_100g") / 4.184 if gn("energy_100g") else 0)
        all_tags = p.get("allergens_tags", []) or []
        alerjen = ", ".join([t.replace("en:", "").replace("tr:", "").title() for t in all_tags]) if all_tags else "Yok"
        cat = (p.get("categories_tags", []) or [""])[0].replace("en:", "").replace("-", " ").title() or "Diğer"
        return {"name": name, "kategori": cat, "package_g": package_g, "kcal_100g": round(kcal, 1), "protein_100g": round(gn("proteins_100g"), 1), "karb_100g": round(gn("carbohydrates_100g"), 1), "yag_100g": round(gn("fat_100g"), 1), "seker_100g": round(gn("sugars_100g"), 1), "lif_100g": round(gn("fiber_100g"), 1), "tuz_100g": round(gn("salt_100g"), 1), "alerjenler": alerjen}, None
    except:
        return None, "Bağlantı hatası"

def add_to_sepet(pid, qty=1):
    for item in st.session_state.sepet:
        if item["id"] == pid:
            item["miktar"] += qty
            return
    st.session_state.sepet.append({"id": pid, "miktar": qty})

def calculate_nutrition():
    if not st.session_state.sepet: return None
    totals = {"fiyat": 0.0, "agirlik_g": 0.0, "kcal": 0.0, "protein": 0.0, "karb": 0.0, "yag": 0.0, "seker": 0.0, "lif": 0.0, "tuz": 0.0}
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
        if prod["alerjenler"] != "Yok": alerjen_set.add(prod["alerjenler"])
        details.append({"ad": prod["ad"], "miktar": item["miktar"], "kcal": round(prod["kcal_100g"] * mult, 1), "protein": round(prod["protein_100g"] * mult, 1), "fiyat": round(prod["fiyat_tl"] * item["miktar"], 2)})
    daily = {"kcal": 2000, "protein": 60, "karb": 250, "yag": 70, "seker": 50, "tuz": 5}
    perc = {k: min(100, round((totals[k] / daily[k]) * 100, 1)) for k in ["kcal", "protein", "karb", "yag"]}
    return {"totals": totals, "perc": perc, "daily": daily, "alerjenler": list(alerjen_set), "details": details}

# Arayüz
st.title("🛒 Markette Gıda Analizi")
st.caption("Telefonunda da çalışır • Open Food Facts entegrasyonlu")

tab1, tab2, tab3, tab4 = st.tabs(["📋 Ürünler", "📡 OFF'tan Ekle", "🛒 Sepet", "📊 Analiz"])

with tab1:
    search = st.text_input("Ürün ara", placeholder="süt, ekmek...")
    filtered = df_products
    if search:
        filtered = df_products[df_products["ad"].str.contains(search, case=False, na=False) | df_products["kategori"].str.contains(search, case=False, na=False)]
    for _, row in filtered.iterrows():
        col1, col2, col3 = st.columns([5,2,2])
        with col1: st.write(f"**{row['ad']}**")
        with col2: st.write(f"{row['fiyat_tl']:.2f} ₺")
        with col3:
            qty = st.number_input("Adet", min_value=1, value=1, key=f"q{row['id']}")
            if st.button("Sepete Ekle", key=f"add{row['id']}"):
                add_to_sepet(row["id"], qty)
                st.success("Eklendi!")
                st.rerun()

with tab2:
    st.subheader("Open Food Facts'ten Ekle")
    bc = st.text_input("Barkod gir")
    if st.button("Getir") and bc:
        prod, err = fetch_product_from_off(bc)
        if err: st.error(err)
        else:
            st.success(prod["name"])
            pkg = st.number_input("Paket ağırlığı (g)", value=prod["package_g"])
            price = st.number_input("Fiyat (₺)", value=25.0)
            qty = st.number_input("Adet", value=1)
            if st.button("Sepete Ekle"):
                new_id = 100 + len(df_products)
                new_row = {**prod, "id": new_id, "ad": prod["name"][:60], "fiyat_tl": price, "paket_agirlik_g": pkg, "barkod": bc}
                df_products = pd.concat([df_products, pd.DataFrame([new_row])], ignore_index=True)
                add_to_sepet(new_id, qty)
                st.success("Eklendi!")
                st.rerun()

with tab3:
    st.subheader("Sepet")
    if not st.session_state.sepet:
        st.info("Sepet boş")
    else:
        for item in st.session_state.sepet:
            prod = get_product_by_id(item["id"])
            if prod:
                st.write(f"{prod['ad']} x {item['miktar']} - {prod['fiyat_tl']*item['miktar']:.2f} ₺")
        if st.button("Sepeti Temizle"):
            st.session_state.sepet = []
            st.rerun()

with tab4:
    st.subheader("Besin Analizi")
    data = calculate_nutrition()
    if data:
        t = data["totals"]
        p = data["perc"]
        st.metric("Toplam Kalori", f"{t['kcal']:.0f} kcal", f"{p['kcal']}%")
        fig, ax = plt.subplots()
        ax.pie([t["protein"]*4, t["karb"]*4, t["yag"]*9], labels=["Protein","Karb","Yağ"], autopct="%1.1f%%")
        st.pyplot(fig)
    else:
        st.info("Sepete ürün ekle")

st.caption("Başarılı denemeler dileriz!")