from apps import mysql

class Document:
    @staticmethod
    def get_documents_all():

        connection = mysql.connect()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM documents")
        documents = cursor.fetchall()

        cursor.close()
        connection.close()

        return documents

    @staticmethod
    def create(title, abstract):
        try:
            connection = mysql.connect()
            cursor = connection.cursor()
            
            cursor.execute("INSERT INTO documents (title, abstract) VALUES (%s, %s)", (title, abstract))
            connection.commit()

            cursor.close()
            connection.close()

            return True
        except Exception as e:
            print(e)
            return False
    
    # @staticmethod