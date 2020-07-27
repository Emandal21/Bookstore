# books.py

import PySimpleGUI as sg
import psycopg2

class BooksForm():
    def __init__(self):
        
        sg.theme('Reds')

        # form design
        self.frame_layout = [
	                            [sg.Text('Books', justification='Right', size=(45,1))],
	                            [sg.Text('Title: ', size=(12,1)), sg.Input(size=(24,1), key='title'), 
	                             sg.Text(''), sg.Combo(values=[], size=(24,10), enable_events=True, key='selBook', readonly=True)],
                                [sg.Text('Author: ', size=(12,1)), sg.Input(size=(24,1), key='author')],
                                [sg.Text('Publisher: ', size=(12,1)), sg.Input(size=(24,1), key='publisher')],
                                [sg.Text('Genre: ', size=(12,1)), 
                                 sg.Combo(['Action', 'Adventure', 'Biography', 'Comic Novel', 'Detective', 'Fantasy', 'Fiction', 'Horror', 'Romance', 'Sci-Fi', 'Thriller'], size=(22,1), key='genre')],
                                [sg.Text('Publishing Year: ', size=(12,1)), sg.Input(size=(24,1), key='pubYear')],
	                            [sg.Text('')]
                        	]

        self.layout =   [
        					[sg.Text('')],
                            [sg.Frame('', self.frame_layout, title_color='blue')],
                            [sg.Text('')],
                            [sg.Text('', size=(10,1)), 
                            sg.Button('Add', size=(8,1), key='add'),
                            sg.Button('Update', size=(8,1), key='update'),
                            sg.Button('Delete', size=(8,1), key='delete'),
                            sg.Button('Close', size=(8,1), key='close')]
                        ]

        # Create the form
        self.window = sg.Window('Books Form').Layout(self.layout).Finalize()

        self.populateBooks()

        # Read the form
        while True:
            event, values = self.window.Read()

            if event == 'add':
                self.addBook(values)  
            elif event == 'selBook':
                self.selectBooks(values)
            elif event == 'populate':
                self.populateBooks()
            elif event == 'update':
                self.updateBook(values)
            elif event == 'delete':
                self.deleteBook()     
            elif event == 'close':
                break
                

        self.window.Close()
    
    #------------------------------------------

    def addBook(self, values):
        conn = None

        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')

            # create a cursor
            cur = conn.cursor()

            # get values from the form
            title = str(values['title'])
            author = str(values['author'])
            publisher = str(values['publisher'])
            genre = str(values['genre'])
            pubYear = int(values['pubYear'])

            # query for inserting a book in the database table Books
            bookInsert = "INSERT INTO \"Bookstore\".\"Books\" (\"title\", \"author\", \"publisher\", \"genre\", \"pubYear\") VALUES(%s, %s, %s, %s, %s);"
            bookRec = (title, author, publisher, genre, pubYear)
            cur.execute(bookInsert, bookRec)
            conn.commit()

            # popup for successfull insertion
            x = "Book " + title + " is inserted"
            sg.Popup(x)

            # clear
            self.clearFields()
            self.populateBooks()

        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("addBook", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()
    
    #------------------------------------------------

    def populateBooks(self):
        data = []
        conn = None

        try:
            # Connect to PostgreSQL database and creating cursor
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')
            cur = conn.cursor()

            #query for getting all records from table Books
            selectBooks = "SELECT * FROM \"Bookstore\".\"Books\" ORDER BY \"bookID\""
            cur.execute(selectBooks)
            self.rows = cur.fetchall()

            data.clear()
            for row in self.rows:
                data.append(row[0:2])

            self.window.FindElement("selBook").Update(values=data)   

            self.clearFields()        
          
        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("Populate", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()
    # ---------------------------------------------------------------------

    def selectBooks(self, values):
        global idbSelected

        # get ID of the selected book
        idbSelected = values['selBook'][0]

        # update fields of the form with data about selected book
        for row in self.rows:
            if (idbSelected == row[0]):
                self.window.FindElement("title").Update(str(row[1]))
                self.window.FindElement("author").Update(str(row[2]))
                self.window.FindElement("publisher").Update(str(row[3]))
                self.window.FindElement("genre").Update(str(row[4]))
                self.window.FindElement("pubYear").Update(int(row[5]))
                break

    # ---------------------------------------------------------------------
    def updateBook(self, values):
        conn = None

        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')

            # create a cursor
            cur = conn.cursor()

            selectBook = "SELECT * FROM \"Bookstore\".\"Books\" WHERE \"bookID\"=%s"
            cur.execute(selectBook, (idbSelected,))
            self.row = cur.fetchone()

            title = str(values['title'])
            author = str(values['author'])
            publisher = str(values['publisher'])
            genre = str(values['genre'])
            pubYear = int(values['pubYear'])

            # query for updating a certain record
            bookUpdate = "UPDATE \"Bookstore\".\"Books\" SET \"title\"=%s, \"author\"=%s, \"publisher\"=%s, \"genre\"=%s, \"pubYear\"=%s WHERE \"bookID\"=%s"
            bookRec = (title, author, publisher, genre, pubYear, idbSelected)
            cur.execute(bookUpdate, bookRec)
            conn.commit()

            # popup after successful update
            x = "Book " + title + " is updated"
            sg.Popup(x)

            self.clearFields()
            self.populateBooks()

        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("Update", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()

    # ---------------------------------------------------------------------

    def deleteBook(self):
        conn = None

        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')

            # create a cursor
            cur = conn.cursor()
            
            # query for deleting a selected record from table Books
            bookDelete = "DELETE FROM \"Bookstore\".\"Books\" WHERE \"bookID\"=%s"
            cur.execute(bookDelete, (idbSelected,))
            conn.commit()

            # popup after successfully deleting a record
            sg.Popup("Record is deleted")
            self.clearFields()
            self.populateBooks()

        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("Delete", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()

    # ---------------------------------------------------------------------
    def clearFields(self):

        self.window.FindElement("title").Update("")
        self.window.FindElement("author").Update("")
        self.window.FindElement("publisher").Update("")
        self.window.FindElement("genre").Update("")
        self.window.FindElement("pubYear").Update("")
    
    # ---------------------------------------------------------------------



if __name__ == '__main__':
    BooksForm()