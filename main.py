import streamlit as st
from user_manager import login, logout, init_db

def main():
    # Initialize login state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # MAIN SECTION
    if not st.session_state.authenticated:
        st.title("🔒 Login Required")
        init_db()
        if login():
            st.rerun()
    else:
        st.sidebar.success(f"Logged in as {st.session_state.user}.")
        st.sidebar.button("Logout", on_click=logout)

        # Header
        st.markdown("# Aplikasi Dashboard Kesehatan")
        st.markdown("Selamat datang! Aplikasi ini menyediakan berbagai fitur analisis dan prediksi kesehatan. Silakan gunakan **sidebar di sebelah kiri** untuk mengakses fitur-fitur berikut:")

        st.markdown("---")

        st.markdown("### Fitur yang Tersedia")

        st.markdown("""
        #### Dashboard
        Melihat ringkasan data kesehatan, statistik, dan riwayat penggunaan Anda.
        _(Akses di sidebar: Dashboard)_

        ---

        #### Prediksi Risiko Penyakit
        Gunakan data pribadi untuk memprediksi kemungkinan risiko penyakit tertentu.
        _(Akses di sidebar: Disease Risk)_

        ---

        #### Rekomendasi Kesehatan
        Dapatkan rekomendasi pola hidup sehat yang dipersonalisasi berdasarkan input Anda.
        _(Akses di sidebar: Health Recommendation)_

        ---

        #### Prediksi Merokok & Alkohol
        Prediksi kemungkinan kebiasaan merokok atau konsumsi alkohol.
        _(Akses di sidebar: Smoking and Alcohol Prediction)_
        """)

        st.markdown("---")
        st.info("Silakan pilih fitur dari sidebar untuk mulai menggunakan aplikasi.")

main()

