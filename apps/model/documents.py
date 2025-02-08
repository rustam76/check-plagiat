from apps.config import get_db_connection

class Document:
    @staticmethod
    def get_documents_all(self, page, per_page):
        offset = (page - 1) * per_page
        query = "SELECT * FROM documents LIMIT %s OFFSET %s"
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, (per_page, offset))
        rows = cursor.fetchall()
        return rows

    @staticmethod
    def create(title, abstract):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            cursor.execute("INSERT INTO documents (title, abstract) VALUES (%s, %s)", (title, abstract))
            connection.commit()

            cursor.close()
            connection.close()

            return True
        except Exception as e:
            print(e)
            return False
    
    @staticmethod
    def create_bulk(data):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            query = "INSERT INTO documents (title, abstract) VALUES (%s, %s)"    
            data_to_insert = list(data[['title', 'abstract']].itertuples(index=False, name=None))
            
            cursor.executemany(query, data_to_insert)
            connection.commit()

            return True
        except Exception as e:
            print(e)
            return False
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def update(document_id, title, abstract):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
  
            query = "UPDATE documents SET title = %s, abstract = %s WHERE id = %s"
            cursor.execute(query, (title, abstract, document_id))
            connection.commit()

            return True
        except Exception as e:
            print(e)
            return False
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def find_by_id(document_id):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Query untuk mencari dokumen berdasarkan id
            query = "SELECT * FROM documents WHERE id = %s"
            cursor.execute(query, (document_id,))
            
            # Mendapatkan hasil query
            document = cursor.fetchone()
            
            # Jika tidak ada hasil, kembalikan None
            if document is None:
                return None
            
            return document
        except Exception as e:
            print(e)
            return None
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def delete(document_id):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Query untuk menghapus dokumen berdasarkan id
            cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
            connection.commit()

            cursor.close()
            connection.close()
            return True
        except Exception as e:
            print(e)
            return False