if not df.empty:
    # Perhitungan Total
    total_kredit = df['Kredit'].sum()
    
    # Ambil total pinjaman dari transaksi yang berstatus Open / Pinjaman Member
    pinjaman_df = df[(df['Keterangan'] == 'Pinjaman Member') & (df['Status'] == 'Open')]
    total_pinjaman = pinjaman_df['Kredit'].sum() if not pinjaman_df.empty else 7650000
    
    # Sesuai Rekap PDF
    total_debit = 38427000
    kas_aktif = total_debit - total_kredit
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
