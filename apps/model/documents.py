from apps.config import get_db_connection
import random

class Document:
    @staticmethod
    def get_documents_all(page, per_page):
        offset = (page - 1) * per_page
        query = "SELECT * FROM documents LIMIT %s OFFSET %s"
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, (per_page, offset))
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return rows

    @staticmethod
    def create_plagiarized_text(text):
        """Simulate plagiarized text by shuffling words."""
        words = text.split()
        if len(words) > 4:  # Shuffle if enough words
            random.shuffle(words)
        return ' '.join(words)

    @staticmethod
    def create(title, abstract,is_plagiarized):
        try:
            # Generate plagiarized versions of the title and abstract
            plagiarized_title = Document.create_plagiarized_text(title)
            plagiarized_abstract = Document.create_plagiarized_text(abstract)
            
            connection = get_db_connection()
            cursor = connection.cursor()

            # Insert the original and plagiarized versions into the database
            query = """
            INSERT INTO documents 
            (judul_asli, abstrak_asli, judul_plagiarisme, abstrak_plagiarisme, is_plagiarized) 
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (plagiarized_title, plagiarized_abstract, title, abstract, is_plagiarized))
            connection.commit()

            cursor.close()
            connection.close()

            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    @staticmethod
    def create_bulk(data):
        """
        Inserts multiple documents into the database with their plagiarized versions.
        Expects 'data' as a pandas DataFrame with 'title' and 'abstract' columns.
        """
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Prepare the query
            query = """
            INSERT INTO documents 
            (judul_asli, abstrak_asli, judul_plagiarisme, abstrak_plagiarisme, is_plagiarized) 
            VALUES (%s, %s, %s, %s, %s)
            """

            # Create plagiarized versions for each row
            data_to_insert = [
                (
                    row['judul_asli'], 
                    row['abstrak_asli'],
                    row['judul_plagiarisme'],
                    row['abstrak_plagiarisme'],
                    row['is_plagiarized']
                ) 
                for _, row in data.iterrows()
            ]

            # Bulk insert data
            cursor.executemany(query, data_to_insert)
            connection.commit()

            cursor.close()
            connection.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False


    @staticmethod
    def update(document_id, title, abstract, is_plagiarized):
        """
        Updates a document's title, abstract, and their plagiarized versions by ID.
        """
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Generate plagiarized versions
            plagiarized_title = Document.create_plagiarized_text(title)
            plagiarized_abstract = Document.create_plagiarized_text(abstract)

            # Prepare the query
            query = """
            UPDATE documents 
            SET judul_asli = %s, abstrak_asli = %s, 
                judul_plagiarisme = %s, abstrak_plagiarisme = %s ,
                is_plagiarized = %s
            WHERE id = %s
            """
            cursor.execute(query, (plagiarized_title, plagiarized_abstract,title, abstract,is_plagiarized, document_id))
            connection.commit()

            cursor.close()
            connection.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False


    @staticmethod
    def find_by_id(document_id):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            query = "SELECT * FROM documents WHERE id = %s"
            cursor.execute(query, (document_id,))
            
            document = cursor.fetchone()
            cursor.close()
            connection.close()
            
            return document
        except Exception as e:
            print(f"Error: {e}")
            return None

    @staticmethod
    def delete(document_id):
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("DELETE FROM documents WHERE id = %s", (document_id,))
            connection.commit()

            cursor.close()
            connection.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
