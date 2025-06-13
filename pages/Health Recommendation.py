import streamlit as st
import pandas as pd

if not st.session_state.get('authenticated'):
    st.warning('Please login first.')
    st.stop()


def calculate_bmi(tinggi, berat):
    """Menghitung Body Mass Index (BMI) dari tinggi (cm) dan berat (kg)."""
    if tinggi > 0:
        return berat / ((tinggi / 100) ** 2)
    return 0

def display_bmi_scale(bmi):
    """Menampilkan visualisasi skala BMI dan menyorot kategori pengguna."""
    st.write("---")
    st.subheader("Skala Kategori BMI")
    
    # Menentukan kategori dan warna berdasarkan nilai BMI
    if bmi < 18.5:
        category = "Underweight"
        colors = ["#3498db", "#ecf0f1", "#ecf0f1", "#ecf0f1"]
        text_colors = ["white", "black", "black", "black"]
        border_styles = ["3px solid black", "1px solid #dcdcdc", "1px solid #dcdcdc", "1px solid #dcdcdc"]
    elif 18.5 <= bmi < 25:
        category = "Normal"
        colors = ["#ecf0f1", "#2ecc71", "#ecf0f1", "#ecf0f1"]
        text_colors = ["black", "white", "black", "black"]
        border_styles = ["1px solid #dcdcdc", "3px solid black", "1px solid #dcdcdc", "1px solid #dcdcdc"]
    elif 25 <= bmi < 30:
        category = "Overweight"
        colors = ["#ecf0f1", "#ecf0f1", "#f39c12", "#ecf0f1"]
        text_colors = ["black", "black", "white", "black"]
        border_styles = ["1px solid #dcdcdc", "1px solid #dcdcdc", "3px solid black", "1px solid #dcdcdc"]
    else: # bmi >= 30
        category = "Obese"
        colors = ["#ecf0f1", "#ecf0f1", "#ecf0f1", "#e74c3c"]
        text_colors = ["black", "black", "black", "white"]
        border_styles = ["1px solid #dcdcdc", "1px solid #dcdcdc", "1px solid #dcdcdc", "3px solid black"]

    st.write(f"BMI Anda **{bmi:.2f}** termasuk dalam kategori **{category}**.")

    # Membuat 4 kolom untuk skala
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f'<div style="background-color:{colors[0]}; color:{text_colors[0]}; padding: 10px; border-radius: 7px; text-align:center; border: {border_styles[0]};"><strong>Underweight</strong><br>&lt; 18.5</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div style="background-color:{colors[1]}; color:{text_colors[1]}; padding: 10px; border-radius: 7px; text-align:center; border: {border_styles[1]};"><strong>Normal</strong><br>18.5 - 24.9</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div style="background-color:{colors[2]}; color:{text_colors[2]}; padding: 10px; border-radius: 7px; text-align:center; border: {border_styles[2]};"><strong>Overweight</strong><br>25.0 - 29.9</div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div style="background-color:{colors[3]}; color:{text_colors[3]}; padding: 10px; border-radius: 7px; text-align:center; border: {border_styles[3]};"><strong>Obese</strong><br>&ge; 30.0</div>', unsafe_allow_html=True)

def generate_recommendations(age, bmi, sbp, dbp, blood_sugar, is_smoker, is_drinker):
    """Menghasilkan daftar rekomendasi berdasarkan data kesehatan pengguna."""
    recommendations = []
    if bmi >= 25:
        recommendations.append("**Manajemen Berat Badan**: BMI Anda menunjukkan berat badan berlebih. Atur pola makan seimbang dan tingkatkan aktivitas fisik.")
    if sbp >= 140 or dbp >= 90:
        recommendations.append("**Kontrol Tekanan Darah**: Tekanan darah Anda tinggi. Sangat disarankan untuk mengurangi asupan garam (natrium), menghindari stres, dan berkonsultasi dengan dokter.")
    if blood_sugar >= 126:
        recommendations.append("**Waspada Diabetes**: Kadar gula darah puasa Anda tinggi. Kurangi konsumsi gula dan konsultasikan dengan dokter.")
    if age >= 60:
        recommendations.append("**Aktivitas untuk Lansia**: Lakukan aktivitas fisik ringan secara teratur seperti jalan kaki atau senam ringan.")
    if is_smoker == "Ya":
        recommendations.append("**Keuntungan Berhenti Merokok**: Berhenti merokok akan mengurangi risiko penyakit jantung, stroke, dan kanker secara drastis.")
    if is_drinker == "Ya":
        recommendations.append("**Kurangi Konsumsi Alkohol**: Mengurangi alkohol bermanfaat bagi kesehatan hati dan mengurangi risiko penyakit kronis.")
    if not recommendations:
        recommendations.append("**Kondisi Anda Baik!**: Pertahankan terus gaya hidup sehat Anda!")
    return recommendations

def get_relevant_health_news(is_smoker, is_drinker, bmi, age, sbp, dbp):
    """Memilih berita kesehatan yang relevan berdasarkan kondisi pengguna."""
    news_database = [
        {
            "id": "smoking",
            "title": "Manfaat Berhenti Merokok Terasa Lebih Cepat dari Dugaan",
            "summary": "Studi menunjukkan perbaikan signifikan pada fungsi paru-paru hanya dalam beberapa minggu setelah berhenti merokok.",
            "link": "https://www.who.int/news-room/spotlight/more-than-100-reasons-to-quit-tobacco",
            "icon": "🚭"
        },
        {
            "id": "hypertension",
            "title": "Diet DASH: Solusi Efektif untuk Mengontrol Hipertensi",
            "summary": "Menerapkan pola makan Dietary Approaches to Stop Hypertension (DASH) terbukti ampuh menurunkan tekanan darah tinggi.",
            "link": "https://www.kemkes.go.id/article/view/22082500001/pola-makan-dash-untuk-penderita-hipertensi.html",
            "icon": "🩺"
        },
        {
            "id": "general",
            "title": "Pentingnya Tidur Cukup untuk Kesehatan Jangka Panjang",
            "summary": "Tidur berkualitas selama 7-8 jam setiap malam dapat meningkatkan imunitas, fungsi kognitif, dan kesehatan mental.",
            "link": "https://yankes.kemkes.go.id/view_artikel/205/manfaat-tidur-cukup-bagi-kesehatan-tubuh",
            "icon": "😴"
        },
        {
            "id": "drinking",
            "title": "Manfaat Berhenti Minum Alkohol Selama Satu Bulan",
            "summary": "Jika ingin melakukan perubahan ke arah yang lebih positif, berhenti minum alkohol dalam satu bulan mungkin dapat membantu memperbaiki kecanduan hingga meningkatkan kesadaran soal kesehatan.",
            "link": "https://lifestyle.kompas.com/read/2023/01/05/094304920/7-efek-pada-tubuh-saat-berhenti-minum-alkohol-selama-satu-bulan?page=all",
            "icon": "🍺"
        },
        {
            "id": "bmi",
            "title": "Waspadai Obesitas! Ketahui Penyebab dan Dampaknya yang Mengancam Kesehatan Anda",
            "summary": "Obesitas memiliki dampak yang signifikan tidak hanya pada kesehatan fisik serta mental dan emosional, tetapi juga pada kualitas hidup dan umur harapan hidup seseorang.",
            "link": "https://heartology.id/health-library/content/waspadai-obesitas-ketahui-penyebab-dan-dampaknya-yang-mengancam-kesehatan-anda/",
            "icon": "😯"
        },
        {
            "id": "lansia",
            "title": "Berbagai Jenis Olahraga untuk Lansia Beserta Manfaatnya",
            "summary": "Meski di usia yang tak lagi muda, para lansia dianjurkan untuk rutin melakukan aktivitas fisik. Nah, ada beberapa jenis olahraga untuk lansia yang dapat dilakukan untuk menjaga kebugaran tubuh dan menurunkan risiko berbagai penyakit akibat penuaan.",
            "link": "https://www.alodokter.com/olah-tubuh-bagi-lansia#:~:text=Manfaat%20Olahraga%20bagi%20Lansia&text=Memperkuat%20otot%20dan%20sendi,gangguan%20pada%20otak%2C%20seperti%20demensia",
            "icon": "🧘🏻"
        }
    ]

def get_relevant_health_news(is_smoker,is_drinker,bmi,age, sbp, dbp):
    """Memilih berita kesehatan yang relevan berdasarkan kondisi pengguna."""
    news_database = [
        {"id": "smoking", "title": "Manfaat Berhenti Merokok Terasa Lebih Cepat dari Dugaan", "summary": "Studi menunjukkan perbaikan signifikan pada fungsi paru-paru hanya dalam beberapa minggu setelah berhenti merokok.", "link": "https://www.who.int/news-room/spotlight/more-than-100-reasons-to-quit-tobacco", "icon": "🚭"},
        {"id": "hypertension", "title": "Diet DASH: Solusi Efektif untuk Mengontrol Hipertensi", "summary": "Menerapkan pola makan Dietary Approaches to Stop Hypertension (DASH) terbukti ampuh menurunkan tekanan darah tinggi.", "link": "https://www.kemkes.go.id/article/view/22082500001/pola-makan-dash-untuk-penderita-hipertensi.html", "icon": "🩺"},
        {"id": "general", "title": "Pentingnya Tidur Cukup untuk Kesehatan Jangka Panjang", "summary": "Tidur berkualitas selama 7-8 jam setiap malam dapat meningkatkan imunitas, fungsi kognitif, dan kesehatan mental.", "link": "https://yankes.kemkes.go.id/view_artikel/205/manfaat-tidur-cukup-bagi-kesehatan-tubuh", "icon": "😴"},
        {"id": "drinking", "title": "Manfaat Berhenti Minum Alkohol Selama Satu Bulan", "summary": "Jika ingin melakukan perubahan ke arah yang lebih positif, berhenti minum alkohol dalam satu bulan mungkin dapat membantu memperbaiki kecanduan hingga meningkatkan kesadaran soal kesehatan.", "link": "https://lifestyle.kompas.com/read/2023/01/05/094304920/7-efek-pada-tubuh-saat-berhenti-minum-alkohol-selama-satu-bulan?page=all", "icon": "🍺"},
        {"id": "bmi", "title": "Waspadai Obesitas! Ketahui Penyebab dan Dampaknya yang Mengancam Kesehatan Anda", "summary": "Obesitas memiliki dampak yang signifikan tidak hanya pada kesehatan fisik serta mental dan emosional, tetapi juga pada kualitas hidup dan umur harapan hidup seseorang.", "link": "https://heartology.id/health-library/content/waspadai-obesitas-ketahui-penyebab-dan-dampaknya-yang-mengancam-kesehatan-anda/", "icon": "😯"},
        {"id": "lansia", "title": "Berbagai Jenis Olahraga untuk Lansia Beserta Manfaatnya", "summary": "Meski di usia yang tak lagi muda, para lansia dianjurkan untuk rutin melakukan aktivitas fisik. Nah, ada beberapa jenis olahraga untuk lansia yang dapat dilakukan untuk menjaga kebugaran tubuh dan menurunkan risiko berbagai penyakit akibat penuaan.", "link": "https://www.alodokter.com/olah-tubuh-bagi-lansia#:~:text=Manfaat%20Olahraga%20bagi%20Lansia&text=Memperkuat%20otot%20dan%20sendi,gangguan%20pada%20otak%2C%20seperti%20demensia", "icon": "🧘🏻"}
    ]
    relevant_news = []
    if is_smoker == "Ya":
        relevant_news.append(next(item for item in news_database if item["id"] == "smoking"))
    if sbp >= 140 or dbp >= 90:
        relevant_news.append(next(item for item in news_database if item["id"] == "hypertension"))
    if is_drinker == "Ya":
        relevant_news.append(next(item for item in news_database if item["id"] == "drinking"))
    if bmi >= 25:
        relevant_news.append(next(item for item in news_database if item["id"] == "bmi"))
    if age >= 60:
        relevant_news.append(next(item for item in news_database if item["id"] == "lansia"))
    relevant_news.append(next(item for item in news_database if item["id"] == "general"))
    
    # Menghapus duplikat
    unique_news = []
    seen_ids = set()
    for news_item in relevant_news:
        if news_item['id'] not in seen_ids:
            unique_news.append(news_item)
            seen_ids.add(news_item['id'])
    return unique_news

# --- Tampilan Aplikasi Streamlit ---
st.set_page_config(page_title="Rekomendasi Kesehatan Personal", page_icon="❤️‍🩹", layout="centered")
st.title("Rekomendasi Kesehatan & Berita")
st.markdown("Masukkan data kesehatan Anda untuk mendapatkan saran gaya hidup dan berita kesehatan yang relevan.")

with st.form("health_input_form"):
    st.header("Formulir Data Kesehatan")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Usia (Tahun)", 1, 120, 30)
        height = st.number_input("Tinggi Badan (cm)", 50, 250, 170)
        sbp = st.number_input("Tekanan Darah Sistolik (SBP)", 70, 250, 120)
        blood_sugar = st.number_input("Gula Darah Puasa (mg/dL)", 50, 500, 90)
        is_smoker = st.selectbox("Apakah Anda seorang perokok?", ("Tidak", "Ya"))
    with col2:
        weight = st.number_input("Berat Badan (kg)", 10, 200, 65)
        st.write(" ")
        dbp = st.number_input("Tekanan Darah Diastolik (DBP)", 40, 200, 80)
        st.write(" ")
        is_drinker = st.selectbox("Apakah Anda mengonsumsi alkohol?", ("Tidak", "Ya"))
    submitted = st.form_submit_button("Dapatkan Hasil")

if submitted:
    bmi = calculate_bmi(height, weight)
    recommendations_list = generate_recommendations(age, bmi, sbp, dbp, blood_sugar, is_smoker, is_drinker)
    news_list = get_relevant_health_news(is_smoker, is_drinker, bmi, age, sbp, dbp)

    st.markdown("---")
    st.subheader("Hasil Analisis Kesehatan Anda")
    
    display_bmi_scale(bmi)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Rekomendasi Personal Untuk Anda")
    for rec in recommendations_list:
        st.success(rec, icon="✅")

    st.markdown("---")
    st.subheader("Berita Kesehatan Terkait")
    for news in news_list:
        with st.container(border=True):
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"<p style='font-size: 52px; text-align: center;'>{news['icon']}</p>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{news['title']}**")
                st.write(news['summary'])
                st.page_link(news['link'], label="Baca Selengkapnya...", icon="➡️")