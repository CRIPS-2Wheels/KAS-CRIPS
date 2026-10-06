import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="KAS CRIPS Dashboard",
    page_icon="🏍️",
    layout="wide"
)

st.title("🏍️ Dashboard KAS CRIPS 2023–2026")
st.subheader("Caferacer Indonesia Pekanbaru Sekitarnya")
st.divider()

# Metric Ringkasan Kas Utama
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Uang Masuk (Debit)", value="Rp 38.427.000")

with col2:
    st.metric(label="Total Uang Keluar (Kredit)", value="Rp 33.061.733")

with col3:
    st.metric(label="Kas Aktif", value="Rp 5.365.267")

with col4:
    st.metric(label="Pinjaman Member", value="Rp 7.650.000")

st.info("💡 **Total Kas Keseluruhan (Kas Aktif + Pinjaman Member):** Rp 13.015.267")

@st.cache_data
def load_data():
    df = pd.read_csv("data/kas_crips.csv")
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    return df

try:
    df = load_data()

    st.subheader("📊 Visualisasi Alokasi Dana")
    summary_data = pd.DataFrame({
        'Kategori': ['Kas Aktif', 'Pinjaman Member', 'Total Kredit (Terpakai)'],
        'Jumlah': [5365267, 7650000, 33061733]
    })

    fig = px.pie(
        summary_data, 
        values='Jumlah', 
        names='Kategori', 
        title='Alokasi Total Dana CRIPS',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📜 Riwayat Transaksi Kas")
    st.dataframe(
        df.style.format({'Debit': 'Rp {:,.0f}', 'Kredit': 'Rp {:,.0f}'}),
        use_container_width=True
    )

except Exception as e:
    st.error(f"Gagal memuat data: {e}")
