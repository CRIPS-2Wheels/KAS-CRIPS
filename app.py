import streamlit as st
import pandas as pd
import plotly.express as px
from github import Github
import io

# Konfigurasi Halaman
st.set_page_config(
    page_title="KAS CRIPS Dashboard",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load / Save Data via GitHub API
def load_data_from_github():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["REPO_NAME"]
        g = Github(token)
        repo = g.get_repo(repo_name)
        file_content = repo.get_contents("data/kas_crips.csv")
        csv_data = file_content.decoded_content.decode("utf-8")
        df = pd.read_csv(io.StringIO(csv_data))
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])
        return df, file_content.sha
    except Exception as e:
        st.error(f"Gagal memuat data dari GitHub: {e}")
        return pd.DataFrame(), None

def save_data_to_github(df, sha):
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["REPO_NAME"]
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_str = csv_buffer.getvalue()
        
        repo.update_file(
            path="data/kas_crips.csv",
            message="Update KAS via Streamlit Admin Panel",
            content=csv_str,
            sha=sha
        )
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan ke GitHub: {e}")
        return False

# Ambil Data Terbaru
df, file_sha = load_data_from_github()

# Sidebar / Panel Admin Bendahara (Ditaruh di atas agar sidebar selalu muncul)
st.sidebar.header("🔐 Akses Admin / Bendahara")
password = st.sidebar.text_input("Masukkan Password Admin", type="password")

# Header Utama
st.title("🏍️ Dashboard KAS CRIPS")
st.subheader("Caferacer Indonesia Pekanbaru Sekitarnya")
st.divider()

if not df.empty:
    total_debit = df['Debit'].sum()
    total_kredit = df['Kredit'].sum()
    kas_aktif = total_debit - total_kredit
    
    pinjaman_df = df[df['Keterangan'] == 'Pinjaman Member']
    total_pinjaman = pinjaman_df['Kredit'].sum() if not pinjaman_df.empty else 0
    total_kas_keseluruhan = kas_aktif + total_pinjaman

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Uang Masuk (Debit)", value=f"Rp {total_debit:,.0f}")
    with col2:
        st.metric(label="Total Uang Keluar (Kredit)", value=f"Rp {total_kredit:,.0f}")
    with col3:
        st.metric(label="Kas Aktif", value=f"Rp {kas_aktif:,.0f}")
    with col4:
        st.metric(label="Pinjaman Member", value=f"Rp {total_pinjaman:,.0f}")

    st.info(f"💡 **Total Kas Keseluruhan (Kas Aktif + Pinjaman Member):** Rp {total_kas_keseluruhan:,.0f}")

    st.subheader("📊 Visualisasi Alokasi Dana")
    summary_data = pd.DataFrame({
        'Kategori': ['Kas Aktif', 'Pinjaman Member', 'Total Kredit (Terpakai)'],
        'Jumlah': [kas_aktif, total_pinjaman, total_kredit]
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

st.divider()

# Logika Akses Admin
if password == st.secrets.get("ADMIN_PASSWORD", "admin123"):
    st.sidebar.success("Akses Diterima!")
    st.header("⚙️ Panel Kelola Transaksi (Bendahara)")
    
    tab_tambah, tab_edit = st.tabs(["➕ Tambah Transaksi Baru", "✏️ Edit / Hapus Data"])
    
    with tab_tambah:
        st.subheader("Form Uang Masuk / Uang Keluar")
        with st.form("form_tambah"):
            no_baru = int(df['No'].max() + 1) if not df.empty else 1
            tgl = st.date_input("Tanggal")
            perihal = st.text_input("Perihal / Keterangan Transaksi")
            tipe = st.radio("Jenis Transaksi", ["Uang Masuk (Debit)", "Uang Keluar (Kredit)", "Pinjaman Member"])
            jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=5000)
            status = st.selectbox("Status", ["Close", "Open"])
            ket_tambahan = st.text_input("Keterangan Tambahan (Opsional)")
            
            submit = st.form_submit_button("Simpan Transaksi")
            
            if submit:
                debit_val = jumlah if tipe == "Uang Masuk (Debit)" else 0
                kredit_val = jumlah if tipe in ["Uang Keluar (Kredit)", "Pinjaman Member"] else 0
                ket_final = "Pinjaman Member" if tipe == "Pinjaman Member" else ket_tambahan
                
                new_row = {
                    'No': no_baru,
                    'Tanggal': tgl.strftime('%Y-%m-%d'),
                    'Perihal': perihal,
                    'Debit': debit_val,
                    'Kredit': kredit_val,
                    'Status': status,
                    'Keterangan': ket_final
                }
                
                df_updated = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                if save_data_to_github(df_updated, file_sha):
                    st.success("Transaksi berhasil disimpan!")
                    st.rerun()

    with tab_edit:
        st.subheader("Edit Data Transaksi")
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            key="data_editor"
        )
        if st.button("Simpan Perubahan Tabel"):
            if save_data_to_github(edited_df, file_sha):
                st.success("Perubahan tabel berhasil disimpan!")
                st.rerun()

elif password != "":
    st.sidebar.error("Password Salah!")
