import pandas as pd
import mysql.connector
from datetime import datetime
from mysql.connector import Error
import re
import numpy as np  # Untuk memeriksa NaN

# Path ke file Excel asal
file_path = "datarakon2.xls"

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "db_asset"
}

def chekTahunTarge(target):
    if target in ['REAL 2024']:
        return None
    elif target in ['TARGET 2024']:
        return None
    elif target in ['TERBIT PKS']:
        return 2024
    elif target == 'REAL 2023':
        return 2023
    else:
        return None 

def cekunit_id(unit_id):
    mapping = {
        3611: 3,
        3612: 4,
        3613: 5,
        3614: 6,
        3615: 7,
        3616: 8
    }
    return mapping.get(unit_id, unit_id) 

def checkJenis(target):
    if(target == 'Perjanjian Kerja Sama'):
            return 'perjanjian_kerja_sama'
    elif(target == 'PPKH'):
            return 'ppkh'
    else:
            return None

def clean_nama_permasalahan(nama_permasalahan):
    if isinstance(nama_permasalahan, str):  # Pastikan input adalah string
        # Menghapus angka di awal dan juga karakter '.' dan spasi
        cleaned = re.sub(r'^\d+\.\s*', '', nama_permasalahan)  
        return cleaned.strip()  # Menghapus spasi di awal dan akhir
    return nama_permasalahan # Kembalikan nilai asli jika bukan string

def format_date(date_str):
    """Convert a date string from DD/MM/YYYY to YYYY-MM-DD."""
    if date_str in ['00:00:00', '', None]:  # Tangani nilai waktu dan nilai kosong
        return None  # Atau bisa mengembalikan string kosong '' jika diperlukan
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None # Return original value if conversion fails

def checkPermasalahan(nama_permasalahan):
    connection = None
    cursor = None
    try:
        nama_permasalahan = clean_nama_permasalahan(nama_permasalahan)

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        query = "SELECT id FROM permasalahan WHERE klaster_permasalahan = %s"
        cursor.execute(query, (nama_permasalahan,))
        result = cursor.fetchone()  # Mengambil satu hasil
        
        return result['id'] if result else None  # Mengembalikan ID jika ditemukan
    except Error as e:
        print(f"Error selama proses: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def chekStarus(target):
        return 1 if target == 'Sudah' else 0

def insert_ass(data):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        table_name = "aset"
        
        # Insert data into MySQL table
        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(sql_query, tuple(data.values()))

        # Commit changes
        connection.commit()
        
        # Mengembalikan ID dari entri yang baru saja dimasukkan
        return cursor.lastrowid

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None  # Mengembalikan None jika terjadi kesalahan
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def insert_progress(data):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        table_name = "progress_sertifikasi"
        
        # Insert data into MySQL table
        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(sql_query, tuple(data.values()))

        # Commit changes
        connection.commit()
        print(f"{cursor.rowcount} rows inserted into {table_name}.")  

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

try:
    # Membaca file Excel, sheet kedua tanpa header
    print("\nMembaca file Excel...")
    data = pd.read_excel(file_path, sheet_name=5, header=None)  # Coba tanpa header
    print("\nSeluruh DataFrame:")
    print(data)

    # Ganti NaN dengan None
    data = data.where(pd.notnull(data), None)
    count_data= 0;
    cont_255 =0;
    count_2023 =0
    count_pks=0

    # Iterasi melalui setiap baris di DataFrame
    for index in range(data.shape[0]):  # Iterasi berdasarkan jumlah baris
        row_data = data.iloc[index]  # Mengambil data dari baris tertentu
        # print(f"ID untuk '{index}' adalah: {row_data[index]}")
        lokasi = row_data[16] if row_data[16] is not None else "Default Lokasi"  # Default jika None
        unit_id_value = row_data[5]
        unit_id = cekunit_id(unit_id_value) if unit_id_value is not None and isinstance(unit_id_value, (int, float)) else None
        
        dataToInsert = {
            'unit_induk': 1,
            'lokasi': lokasi,
            'nama_aset': row_data[4],
            'unit_id': unit_id,
            'nomor_sap': row_data[8] or 1111,
            'luas': row_data[9] or 0.0,
            'status': row_data[10],
            'harga_perolehan': row_data[11],
            'tahun_perolehan': format_date(row_data[12]),
            'nilai_saat_ini': row_data[13],
            'tanggal_penilaian': format_date(row_data[14]),
            'sumber_perolehan': row_data[15],
            'latitude': row_data[16],
            'longitude': row_data[17],
            'alamat': row_data[19],
            'nomor_asset': row_data[26],
            'tanggal_berlaku_sertifikat_dari': format_date(row_data[27]),
            'tanggal_berlaku_sertifikat_sampai': format_date(row_data[28]) or '2022-03-01',
            'penguasaan_tanah': row_data[29],
            'jenis_bangunan': row_data[30],
            'permasalahan_id': checkPermasalahan(row_data[31]),
            'narasi_permasalahan_aset': row_data[32],
            'kantah_bpn_sertifikasi': row_data[41],
            'wilayah_bpn_sertifikasi': row_data[42],
            'tipe_aset': 'dokumen-legal',
            'jenis': checkJenis(row_data[53]),
            'tahun_target': chekTahunTarge(row_data[43]),
            'bulan_realisasi': row_data[52],
        }

        # Filter dataToInsert untuk None values
        dataToInsert = {k: (v if v is not None else None) for k, v in dataToInsert.items()}
        
        insert_ass(dataToInsert)

    #     datas = chekTahunTarge(row_data[43])

    #     if(datas == 2024):
    #         count_data += 1

    #     if(datas == 2023):
    #         count_2023 += 1

    #     if(datas == 2025):
    #         cont_255 += 1
        
    #     if(datas == 2026):
    #         count_pks += 1

    # print(f"2024: {count_data}, 2023: {count_2023}, 2025: {cont_255}, 2026: {count_pks}")

except Exception as e:
    print(f"Terjadi kesalahan: {e}")

