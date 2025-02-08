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
    # if target in ['REAL 2024', 'TARGET 2024']:
    if target in ['REAL 2024']:
        return None
    elif target in ['TARGET 2024']:
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
    if (target == 'Sertipikat Baru'):
        return 'sertifikat_baru'
    elif (target == 'Sertipikat Perpanjangan/Pembaharuan'):
        return 'sertifikat_perpanjangan'


def clean_nama_permasalahan(nama_permasalahan):
    if isinstance(nama_permasalahan, str):  # Pastikan input adalah string
        # Menghapus angka di awal dan juga karakter '.' dan spasi
        cleaned = re.sub(r'^\d+\.\s*', '', nama_permasalahan)
        return cleaned.strip()  # Menghapus spasi di awal dan akhir
    return nama_permasalahan  # Kembalikan nilai asli jika bukan string


def format_date(date_str):
    """Convert a date string from various formats to YYYY-MM-DD.
    Handles malformed inputs and returns the default date '2022-02-12' if it cannot be parsed.
    """
    try:
        # Normalize the string: remove unexpected characters and spaces
        normalized_date_str = re.sub(r'[^0-9/]', '', date_str)

        # Handle common cases of malformed date strings
        if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', normalized_date_str):
            return datetime.strptime(normalized_date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        elif re.match(r'^\d{1,2}/\d{1,2}/\d{2}$', normalized_date_str):
            # Fix 2-digit year cases (assume year 2000+ for 2-digit years)
            return datetime.strptime(normalized_date_str, "%d/%m/%y").strftime("%Y-%m-%d")
        elif re.match(r'^\d{1,2}[.]/\d{1,2}/\d{4}$', date_str):
            # Handle cases like '13.01/2052'
            normalized_date_str = date_str.replace('.', '/').strip()
            return datetime.strptime(normalized_date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        elif re.match(r'^\d{1,2}/\d{1,2}/\d{3}$', normalized_date_str):
            # Handle cases like '18/04/202'
            fixed_date_str = normalized_date_str[:-
                                                 3] + '0' + normalized_date_str[-3:]
            return datetime.strptime(fixed_date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        elif re.match(r'^\d{1,2}/\d{2}\d{4}$', normalized_date_str):
            # Handle cases like '11/022054'
            fixed_date_str = normalized_date_str[:2] + '/' + \
                normalized_date_str[2:4] + '/' + normalized_date_str[4:]
            return datetime.strptime(fixed_date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        elif re.match(r'^HP no\. \d+ Th \d{4}$', date_str, re.IGNORECASE):
            # Handle cases like 'HP no. 6 Th 1986'
            year = re.search(r'\d{4}', date_str).group()
            number = re.search(r'\d+', date_str).group()
            return f"{year}-06-{int(number):02d}"
        elif re.match(r'^\d{1,2}[.]\d{1,2}[.]\d{4}$', date_str):
            # Handle cases like '24.12.2052'
            normalized_date_str = date_str.replace('.', '/').strip()
            return datetime.strptime(normalized_date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        pass

    # Return default date if conversion fails
    return "2022-02-12"


def sanitize_value(value):
    """Convert input to integer or return 0 if invalid.

    Args:
        value: The input value to sanitize, which may be a string, number, or other type.

    Returns:
        int: The sanitized integer value or 0 if input is invalid or negative.
    """
    try:
        # Attempt to convert the value to an integer
        integer_value = int(value)

        # Ensure the integer value is non-negative
        return max(0, integer_value)
    except (ValueError, TypeError):
        # Return 0 for any value that cannot be converted to an integer
        return 0


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

        # Mengembalikan ID jika ditemukan
        return result['id'] if result else None
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


def replace_nan(value, default=None):
    return default if pd.isna(value) else value


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
    data = pd.read_excel(file_path, sheet_name=2,
                         header=None)  # Coba tanpa header
    print("\nSeluruh DataFrame:")
    print(data)
    count_data= 0;
    cont_255 =0;
    count_2023 =0
    # Iterasi melalui setiap baris di DataFrame
    for index in range(data.shape[0]):  # Iterasi berdasarkan jumlah baris
        row_data = data.iloc[index]  # Mengambil data dari baris tertentu

        # print(f"ID untuk '{index}' adalah: {row_data[index]}")
        # # Ganti NaN dengan None
        lokasi = row_data[16] if not pd.isna(
            row_data[16]) else "Default Lokasi"  # Atau None jika ingin skip
        unit_id_value = row_data[5]
        unit_id = cekunit_id(unit_id_value) if not pd.isna(
            unit_id_value) and isinstance(unit_id_value, (int, float)) else None




        dataToInsert = {
            'unit_induk': 1,
            'lokasi': lokasi,
            'nama_aset': replace_nan(row_data[4]),
            'unit_id': unit_id,
            'nomor_sap': replace_nan(row_data[6], 1111),
            'luas': replace_nan(row_data[7]),
            'status': replace_nan(row_data[8]),
            'harga_perolehan': replace_nan(row_data[9]),
            'tahun_perolehan': replace_nan(format_date(row_data[10])),
            'nilai_saat_ini': replace_nan(sanitize_value(row_data[11])),
            'tanggal_penilaian': replace_nan(format_date(row_data[12])),
            'sumber_perolehan': replace_nan(row_data[13]),
            'latitude': replace_nan(row_data[14]),
            'longitude': replace_nan(row_data[15]),
            'alamat': replace_nan(row_data[16]),
            'nomor_asset': replace_nan(row_data[23]),
            'tanggal_berlaku_sertifikat_dari': replace_nan(format_date(row_data[24]), '2022-03-01'),
            'tanggal_berlaku_sertifikat_sampai': replace_nan(format_date(row_data[25]), '2022-03-01'),
            'penguasaan_tanah': replace_nan(row_data[26]),
            'jenis_bangunan': replace_nan(row_data[27]),
            'permasalahan_id': replace_nan(checkPermasalahan(row_data[28])),
            'narasi_permasalahan_aset': replace_nan(row_data[29]),
            'kantah_bpn_sertifikasi': replace_nan(row_data[41]),
            'wilayah_bpn_sertifikasi': replace_nan(row_data[42]),
            'tipe_aset': 'sertifikat',
            'jenis': replace_nan(checkJenis(row_data[50])),
            'tahun_target': replace_nan(chekTahunTarge(row_data[40])),
            'bulan_realisasi': replace_nan(row_data[49]),
        }

        dataid = insert_ass(dataToInsert)

        if dataid:  # Pastikan dataid tidak None
            progres = {
                'pemberkasan': replace_nan(chekStarus(row_data[51])),
                'pendaftaran_pengukuran': replace_nan(chekStarus(row_data[52])),
                'sps1_terbayar': replace_nan(chekStarus(row_data[53])),
                'pengukuran': replace_nan(chekStarus(row_data[54])),
                'terbit_peta_bidang': replace_nan(chekStarus(row_data[55])),
                'pendaftaran_permohonan_hak': replace_nan(chekStarus(row_data[56])),
                'sps2_terbayar': replace_nan(chekStarus(row_data[57])),
                'kegiatan_panitia_a': replace_nan(chekStarus(row_data[58])),
                'terbit_sk_hak': replace_nan(chekStarus(row_data[59])),
                'pendaftaran_sk_hak': replace_nan(chekStarus(row_data[60])),
                'sps3_terbayar': replace_nan(chekStarus(row_data[61])),
                'aset_id': dataid
            }

            insert_progress(progres)

        # print(row_data[4])

        # datas  =  chekTahunTarge(row_data[40])

   
        # if(datas == 2024):
        #     count_data += 1

        # if(datas == 2023):
        #     count_2023 += 1

        # if(datas == 2025):
        #     cont_255 += 1

        # print(f"2024: {count_data}, 2023: {count_2023}, 2025: {cont_255}")

except Exception as e:
    print(f"Terjadi kesalahan: {e}")
