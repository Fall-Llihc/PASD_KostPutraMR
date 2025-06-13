import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from user_manager import get_all_health_data, delete_all_health_data # Import fungsi untuk mendapatkan data kesehatan

import io

if not st.session_state.get('authenticated'):
    st.warning('Silakan login terlebih dahulu.')
    st.stop()

st.set_page_config(layout="wide")

st.title("Dashboard Kebiasaan Merokok dan Minum")

# --- Pemilihan Cakupan Data ---
data_scope = st.radio(
    "Pilih Cakupan Data:",
    options=["Statistik Pengguna", "Semua Statistik Data"],
    index=0  # Default ke "Statistik Pengguna"
)

# --- Pemuatan dan Pra-pemrosesan Data ---
current_user = st.session_state.user
df_filtered = pd.DataFrame() # Inisialisasi df_filtered

if data_scope == "Statistik Pengguna":
    user_health_data_raw = get_all_health_data(current_user) # Dapatkan data untuk pengguna saat ini

    if not user_health_data_raw:
        st.info("Tidak ada riwayat data kesehatan untuk ditampilkan. Silakan masukkan data Anda di halaman 'Smoking and Alcohol Prediction' terlebih dahulu.")
        st.stop() # Hentikan eksekusi lebih lanjut jika tidak ada data spesifik pengguna

    # Definisikan kolom untuk data spesifik pengguna
    columns = ['age', 'sex', 'height', 'weight', 'gamma_GTP', 'smoking', 'drinking', 'SBP', 'DBP', 'BLDS', 'timestamp']
    df = pd.DataFrame(user_health_data_raw, columns=columns)

    # Konversi 'timestamp' menjadi objek datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Sidebar Filter Tanggal (hanya untuk data spesifik pengguna)
    st.sidebar.header("Filter Data Berdasarkan Tanggal")
    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()

    date_range = st.sidebar.date_input(
        "Pilih Rentang Tanggal:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_filter"
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        # Filter DataFrame berdasarkan rentang tanggal yang dipilih
        df_filtered = df[(df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)]
    else:
        df_filtered = df.copy() # Tidak ada filter yang diterapkan jika rentang tanggal tidak lengkap

    if df_filtered.empty:
        st.warning("Tidak ada data untuk rentang tanggal yang dipilih. Sesuaikan filter tanggal atau masukkan data baru.")
        st.stop() # Hentikan eksekusi lebih lanjut jika tidak ada data setelah pemfilteran

    # --- Tombol Hapus Riwayat (hanya untuk data spesifik pengguna) ---
    st.sidebar.markdown("---")
    st.sidebar.header("Kelola Riwayat")
    st.sidebar.warning("Tindakan ini akan menghapus semua riwayat data kesehatan Anda secara permanen. Tidak dapat dibatalkan.")
    if st.sidebar.button("Hapus Semua Riwayat Data"):
        st.session_state.confirm_delete = True

    if st.session_state.get('confirm_delete'):
        st.sidebar.info("Anda yakin ingin menghapus semua riwayat data kesehatan?")
        col_confirm_yes, col_confirm_no = st.sidebar.columns(2)
        if col_confirm_yes.button("Ya, Hapus Sekarang", key="confirm_yes"):
            delete_all_health_data(current_user)
            st.session_state.confirm_delete = False
            st.success("Semua riwayat data kesehatan telah dihapus.")
            st.rerun()
        if col_confirm_no.button("Tidak, Batalkan", key="confirm_no"):
            st.session_state.confirm_delete = False
            st.info("Penghapusan riwayat data dibatalkan.")
            st.rerun()
    # --- Akhir Tombol Hapus Riwayat ---

else: # data_scope == "Semua Statistik Data"
    st.header("Statistik Data Global dari 'smoking_and_drinkin_100k.csv'")
    try:
        # Membaca data dari file CSV
        df = pd.read_csv('smoking_drinkin_100k.csv')

        # Menyesuaikan nama kolom jika diperlukan (contoh: jika CSV memiliki 'sex_M' bukan 'sex')
        # Jika CSV Anda memiliki 'total_cholesterol' dan Anda ingin menggunakannya untuk 'tot_chole' gauge:
        if 'total_cholesterol' in df.columns:
            df.rename(columns={'total_cholesterol': 'tot_chole'}, inplace=True)
        # Jika kolom 'sex' di CSV adalah 0 dan 1, pastikan konsisten dengan 'Laki-laki'/'Perempuan'
        if 'sex' in df.columns:
             df['sex'] = df['sex'].map({'Male': 'Laki-laki', 'Female': 'Perempuan'}) # Sesuaikan jika nilai di CSV berbeda

        st.sidebar.markdown("---")
        st.sidebar.info("Filter tanggal, hapus riwayat, dan manajemen data spesifik pengguna tidak tersedia untuk 'Semua Statistik Data'.")
        
        # Karena tidak ada kolom timestamp di CSV, kita langsung gunakan df sebagai df_filtered
        df_filtered = df.copy() 

        if df_filtered.empty:
            st.warning("Data global kosong. Harap periksa file CSV Anda.")
            st.stop()

    except FileNotFoundError:
        st.error("File 'smoking_and_drinkin_100k.csv' tidak ditemukan. Harap pastikan file tersebut berada di direktori yang sama dengan aplikasi.")
        st.stop()
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat data global: {e}")
        st.stop()


# --- Pra-pemrosesan Umum (Berlaku untuk data pengguna dan semua data) ---
# Konversi 'smoking' dan 'drinking' ke label yang lebih deskriptif (0/1 menjadi 'Tidak'/'Ya')
# Asumsi 0 adalah "Tidak" dan 1 adalah "Ya"
if 'smoking' in df_filtered.columns:
    df_filtered['smoking'] = df_filtered['smoking'].map({1: 'Tidak', 2: 'Tidak', 3: 'Ya'})
if 'drinking' in df_filtered.columns:
    df_filtered['drinking'] = df_filtered['drinking'].map({'Y': 'Tidak', 'N': 'Ya'})

# Hitung BMI menggunakan 'height' (cm) dan 'weight' (kg) untuk data yang difilter
if 'height' in df_filtered.columns and 'weight' in df_filtered.columns:
    df_filtered['height_m'] = df_filtered['height'] / 100 # Konversi cm ke meter
    df_filtered['bmi'] = df_filtered['weight'] / (df_filtered['height_m'] ** 2)

# Buat kelompok usia untuk data yang difilter
if 'age' in df_filtered.columns:
    bins = [0, 18, 30, 45, 60, 100]
    labels = ['<18', '18-30', '31-45', '46-60', '>60']
    df_filtered['age_group'] = pd.cut(df_filtered['age'], bins=bins, labels=labels, right=False)

# --- Tombol Unduh sebagai CSV (Diperbarui untuk mencerminkan cakupan data) ---
st.sidebar.markdown("---")
st.sidebar.header("Unduh Data")
csv_buffer = io.StringIO()
df_filtered.to_csv(csv_buffer, index=False)
csv_data = csv_buffer.getvalue().encode('utf-8')

download_filename = f"{current_user if data_scope == 'Statistik Pengguna' else 'all_users'}_health_data_filtered_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
st.sidebar.download_button(
    label="Unduh Data yang Difilter (.csv)",
    data=csv_data,
    file_name=download_filename,
    mime="text/csv",
    help=f"Unduh data kesehatan yang saat ini ditampilkan dalam format CSV ({data_scope})."
)
# --- Akhir Tombol Unduh sebagai CSV ---


# --- Tata Letak Aplikasi Streamlit (menggunakan df_filtered) ---
st.header(f"Metrik Kesehatan Utama ({data_scope}) 🎯")

# Definisikan konfigurasi gauge untuk metrik yang berbeda
gauge_configs = {
    'Rata-rata Gula Darah Puasa (BLDS)': {
        'column': 'BLDS',
        'value_type': 'mean',
        'title': 'Rata-rata Gula Darah Puasa (BLDS)',
        'range': [0, 200],
        'steps': [
            {'range': [0, 99], 'color': "lightgreen"},
            {'range': [100, 125], 'color': "gold"},
            {'range': [126, 200], 'color': "salmon"}
        ],
        'unit': ' mg/dL'
    },
    'Rata-rata BMI': {
        'column': 'bmi',
        'value_type': 'mean',
        'title': 'Rata-rata BMI',
        'range': [0, 40],
        'steps': [
            {'range': [0, 18.5], 'color': "salmon"},
            {'range': [18.5, 24.9], 'color': "lightgreen"},
            {'range': [25, 29.9], 'color': "gold"},
            {'range': [30, 40], 'color': "salmon"}
        ],
        'unit': ''
    },
    'Persentase Perokok': {
        'column': 'smoking',
        'value_type': 'percentage_yes',
        'title': 'Persentase Perokok',
        'range': [0, 100],
        'steps': [
            {'range': [0, 20], 'color': "lightgreen"},
            {'range': [20, 40], 'color': "gold"},
            {'range': [40, 100], 'color': "salmon"}
        ],
        'unit': '%'
    },
    'Persentase Peminum': {
        'column': 'drinking',
        'value_type': 'percentage_yes',
        'title': 'Persentase Peminum',
        'range': [0, 100],
        'steps': [
            {'range': [0, 20], 'color': "lightgreen"},
            {'range': [20, 40], 'color': "gold"},
            {'range': [40, 100], 'color': "salmon"}
        ],
        'unit': '%'
    },
    'Rata-rata Tekanan Darah Sistolik (SBP)': {
        'column': 'SBP',
        'value_type': 'mean',
        'title': 'Rata-rata Tekanan Darah Sistolik (SBP)',
        'range': [0, 180],
        'steps': [
            {'range': [0, 119], 'color': "lightgreen"},
            {'range': [120, 139], 'color': "gold"},
            {'range': [140, 180], 'color': "salmon"}
        ],
        'unit': ' mmHg'
    },
    'Rata-rata Tekanan Darah Diastolik (DBP)': {
        'column': 'DBP',
        'value_type': 'mean',
        'title': 'Rata-rata Tekanan Darah Diastolik (DBP)',
        'range': [0, 120],
        'steps': [
            {'range': [0, 79], 'color': "lightgreen"},
            {'range': [80, 89], 'color': "gold"},
            {'range': [90, 120], 'color': "salmon"}
        ],
        'unit': ' mmHg'
    },
    'Rata-rata Gamma GTP (gamma_GTP)': {
        'column': 'gamma_GTP',
        'value_type': 'mean',
        'title': 'Rata-rata Gamma GTP',
        'range': [0, 100], # Rentang umum, sesuaikan jika perlu
        'steps': [
            {'range': [0, 60], 'color': "lightgreen"}, # Contoh rentang normal
            {'range': [61, 80], 'color': "gold"},
            {'range': [81, 100], 'color': "salmon"}
        ],
        'unit': ' U/L'
    },
    'Rata-rata Total Kolesterol (tot_chole)': {
        'column': 'tot_chole',
        'value_type': 'mean',
        'title': 'Rata-rata Total Kolesterol',
        'range': [0, 300],
        'steps': [
            {'range': [0, 199], 'color': "lightgreen"},
            {'range': [200, 239], 'color': "gold"},
            {'range': [240, 300], 'color': "salmon"}
        ],
        'unit': ' mg/dL'
    }
}

# Filter opsi gauge berdasarkan kolom yang tersedia di df_filtered
available_gauge_options = {}
for k, v in gauge_configs.items():
    if v['column'] in df_filtered.columns and not df_filtered[v['column']].empty and not df_filtered[v['column']].isnull().all():
        if v['value_type'] == 'percentage_yes':
            if 'Ya' in df_filtered[v['column']].unique() or 'Tidak' in df_filtered[v['column']].unique():
                available_gauge_options[k] = v
        else:
            available_gauge_options[k] = v

if available_gauge_options:
    selected_gauge_metric_name = st.selectbox(
        "Pilih Metrik untuk Gauge Meter:",
        options=list(available_gauge_options.keys()),
        index=0,
        key="gauge_select"
    )

    config = available_gauge_options[selected_gauge_metric_name]
    metric_column = config['column']
    metric_value = None

    if config['value_type'] == 'mean':
        if metric_column in df_filtered.columns and not df_filtered[metric_column].isnull().all():
            metric_value = df_filtered[metric_column].mean()
    elif config['value_type'] == 'percentage_yes':
        if metric_column in df_filtered.columns and not df_filtered[metric_column].isnull().all():
            metric_value = (df_filtered[metric_column] == 'Ya').mean() * 100

    if metric_value is not None:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metric_value,
            title={'text': config['title']},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': config['range'], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'steps': config['steps'],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': metric_value
                }
            },
            number={'suffix': config['unit']}
        ))
        fig_gauge.update_layout(height=450)
        st.plotly_chart(fig_gauge, use_container_width=True)
    else:
        st.warning(f"Data untuk '{selected_gauge_metric_name}' tidak tersedia atau nol dalam rentang tanggal yang dipilih.")
else:
    st.warning("Tidak ada metrik yang tersedia untuk gauge meter dalam rentang tanggal yang dipilih.")

# Baris 1: Diagram Pie
col1, col2 = st.columns(2)

with col1:
    st.header("Distribusi Kebiasaan Merokok")
    if 'smoking' in df_filtered.columns and not df_filtered['smoking'].empty and df_filtered['smoking'].nunique() > 0:
        smoking_counts = df_filtered['smoking'].value_counts().reset_index()
        smoking_counts.columns = ['Smoking Status', 'Count']
        fig_smoking = px.pie(smoking_counts, values='Count', names='Smoking Status', title='Proporsi Perokok')
        st.plotly_chart(fig_smoking, use_container_width=True)
    else:
        st.warning("Kolom 'smoking' tidak ditemukan, kosong, atau tidak memiliki variasi data.")

with col2:
    st.header("Distribusi Kebiasaan Minum")
    if 'drinking' in df_filtered.columns and not df_filtered['drinking'].empty and df_filtered['drinking'].nunique() > 0:
        drinking_counts = df_filtered['drinking'].value_counts().reset_index()
        drinking_counts.columns = ['Drinking Status', 'Count']
        fig_drinking = px.pie(drinking_counts, values='Count', names='Drinking Status', title='Proporsi Peminum')
        st.plotly_chart(fig_drinking, use_container_width=True)
    else:
        st.warning("Kolom 'drinking' tidak ditemukan, kosong, atau tidak memiliki variasi data.")

# Baris 2: Bagan Batang Jenis Kelamin vs Merokok/Minum
st.header("Merokok vs Minum berdasarkan Jenis Kelamin")
if 'sex' in df_filtered.columns and 'smoking' in df_filtered.columns and 'drinking' in df_filtered.columns and not df_filtered.empty and df_filtered['sex'].nunique() > 0:
    gender_behavior = df_filtered.groupby(['sex', 'smoking', 'drinking']).size().reset_index(name='Count')
    fig_gender_behavior = px.bar(gender_behavior, x='sex', y='Count', color='smoking',
                                    pattern_shape='drinking',
                                    title='Merokok dan Minum berdasarkan Jenis Kelamin',
                                    labels={'sex': 'Jenis Kelamin', 'Count': 'Jumlah Orang'},
                                    barmode='group')
    st.plotly_chart(fig_gender_behavior, use_container_width=True)
else:
    st.warning("Kolom 'sex', 'smoking', atau 'drinking' tidak ditemukan, kosong, atau tidak memiliki variasi data yang cukup.")

# Baris 3: Korelasi Metrik Kesehatan
st.header("Korelasi Kebiasaan dengan Metrik Kesehatan")

health_metrics_options = [
    'SBP', 'DBP', 'BLDS', 'bmi', 'gamma_GTP', 'tot_chole' # Sertakan tot_chole
]

available_metrics = [col for col in health_metrics_options if col in df_filtered.columns and not df_filtered[col].isnull().all() and not df_filtered[col].empty]

if available_metrics and 'smoking' in df_filtered.columns and 'drinking' in df_filtered.columns and not df_filtered.empty:
    selected_metric = st.selectbox(
        "Pilih Metrik Kesehatan:",
        options=available_metrics,
        index=available_metrics.index('BLDS') if 'BLDS' in available_metrics else 0,
        key="health_metric_select"
    )

    fig_health_metric = px.box(df_filtered, x='smoking', y=selected_metric, color='drinking',
                                    title=f'Distribusi {selected_metric.replace("_", " ").title()} berdasarkan Kebiasaan Merokok dan Minum',
                                    labels={'smoking': 'Merokok', selected_metric: selected_metric.replace('_', ' ').title(), 'drinking': 'Minum'})
    st.plotly_chart(fig_health_metric, use_container_width=True)
else:
    st.warning("Tidak cukup kolom untuk menampilkan korelasi metrik kesehatan atau kolom kebiasaan dalam rentang tanggal yang dipilih.")

st.header("Perilaku Merokok & Minum berdasarkan Kelompok Usia 📊")

if 'age_group' in df_filtered.columns and 'smoking' in df_filtered.columns and 'drinking' in df_filtered.columns and not df_filtered.empty and df_filtered['age_group'].nunique() > 0:
    age_behavior = df_filtered.groupby(['age_group', 'smoking', 'drinking']).size().reset_index(name='Jumlah')

    fig_age_behavior = px.bar(
        age_behavior,
        x='age_group',
        y='Jumlah',
        color='smoking',
        barmode='stack',
        facet_col='drinking',
        title="Distribusi Merokok Berdasarkan Usia dan Status Minum",
        labels={'age_group': 'Kelompok Usia', 'smoking': 'Merokok', 'drinking': 'Minum'}
    )
    st.plotly_chart(fig_age_behavior, use_container_width=True)
else:
    st.warning("Kolom 'age_group', 'smoking', atau 'drinking' tidak ditemukan dalam rentang tanggal yang dipilih, kosong, atau tidak memiliki variasi data yang cukup. Tidak dapat menampilkan visualisasi kelompok usia.")

st.write(df_filtered) # Tampilkan DataFrame yang difilter