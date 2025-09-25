from apps.model.documents import Document
import pandas as pd

class DocumentsController:

    def create_data(title, abstract):
        try:
            docum = Document()
            if not title or not abstract:
                return False 
             
            docum.create(title, abstract)

            return True
        except Exception as e:
            print(e)
            return False

    def create_data_bulk(self,file_path):
        try:
            docum = Document()

            data = read_data(file_path)

            # if not validate_data(data):
            #     print("Data tidak valid")
            #     return False
             
            docum.create_bulk(data)
            return True
        except Exception as e:
            print(e)
            return False

    def get_data(self, page, per_page):
        try:
            return Document.get_documents_all(page, per_page)
        except Exception as e:
            print(f"Document tidak valid: {e}")
            return []
    

    def update_data(self, document_id, title, abstract):
        try:
            # Periksa apakah parameter title dan abstract kosong
            if not title or not abstract:
                return False
            
            docum = Document()
            # Cari dokumen berdasarkan document_id
            documbyid = docum.find_by_id(document_id)
            if not documbyid:
                return False  # Dokumen tidak ditemukan
            
            # Update data dokumen
            docum.update(document_id=document_id, title=title, abstract=abstract)

            return True
        except Exception as e:
            print(e)
            return False
    
    def delete_data(self, document_id):
        try:
            docum = Document()
            # Cari dokumen berdasarkan document_id
            documbyid = docum.find_by_id(document_id)
            if not documbyid:
                return False  # Dokumen tidak ditemukan
            
            # Hapus dokumen
            return docum.delete(document_id)
        except Exception as e:
            print(e)
            return False


def validate_data(data):
    # Contoh validasi: cek apakah kolom 'title' dan 'abstract' tidak ada yang kosong
    if data['title'].isnull().any() or data['abstract'].isnull().any():
        return False
    return True



def read_data(file_path):
    # Cek ekstensi file
    if file_path.endswith('.xlsx'):
        data = pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
    else:
        raise ValueError("File harus berformat .xlsx atau .csv")
    
    return data

