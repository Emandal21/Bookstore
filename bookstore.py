# bookstore.py

import PySimpleGUI as sg
import psycopg2
import datetime
from memebers import *
from books import *

class bookstoreForm():
    def __init__(self):

        sg.theme('Reds')

        global data # data to be listed in the table
        global dateSelected # selected date
        global returnedSelected # binary variable to define if book is returned or not
        returnedSelected = False
        data = []

        # column names for table with all bookings
        colHeadings = ['Booking ID', 'Member ID', 'Full name', 'Book ID', 'Book title', 'Booking date', 'Returned']
        d0 = ['','','','','', '', '']
        data.append(d0)

        # menu actions
        self.menu_booking =     [
                                    ['Members',['Members']],
                                    ['Books', ['Books']],
                                    ['Actions', ['Pending Bookings', 'All Bookings']],
                                    ['Exit', ['Exit']]
                                ]
        # frame for members
        self.frame1 =   [
                            [sg.Text('BOOKSTORE MEMBERS', justification='center', size=(60,1))],
                            [sg.Text('')],
                            [sg.Text('First Name: ', size=(12,1)), sg.Input(size=(30,1), key='firstName', disabled=True),
                             sg.Text('', size=(12,1)), sg.Combo([], size=(20,1), enable_events=True, key='selMEMBER', readonly=True)],
                            [sg.Text('Last Name: ', size=(12,1)), sg.Input(size=(30,1), key='lastName', disabled=True)],
                            [sg.Text('Address: ', size=(12,1)), sg.Input(size=(30,1), key='address', disabled=True)],
                            [sg.Text('City: ', size=(12,1)), sg.Input(size=(30,1), key='city', disabled=True)],
                            [sg.Text('Country: ', size=(12,1)), sg.Input(size=(30,1), key='country', disabled=True)],
                            [sg.Text('Birthday: ', size=(12,1)), sg.In('', size=(30,1), key='birthday', disabled=True)],
                            [sg.Text('Gender: ', size=(12,1)), sg.Input(size=(30,1), key='gender', disabled=True)],
                            [sg.Text('Phone Number: ', size=(12, 1)), sg.Input(size=(30, 1), key='phoneNumber', disabled=True)],
                            [sg.Text('')],
                            [sg.Text('')]
                        ]
        # frame for books
        self.frame2 =   [
                            [sg.Text('BOOKS', justification='center', size=(60,1))],
                            [sg.Text('')],
                            [sg.Text('Title: ', size=(12,1)), sg.Input(size=(24,1), key='title', disabled=True), 
                             sg.Text(''), sg.Combo(values=[], size=(24,10), enable_events=True, key='selBOOK', readonly=True)],
                            [sg.Text('Author: ', size=(12,1)), sg.Input(size=(24,1), key='author', disabled=True)],
                            [sg.Text('Publisher: ', size=(12,1)), sg.Input(size=(24,1), key='publisher', disabled=True)],
                            [sg.Text('Genre: ', size=(12,1)), sg.Input(size=(24,1), key='genre', disabled=True)],
                            [sg.Text('Publishing Year: ', size=(12,1)), sg.Input(size=(24,1), key='pubYear', disabled=True)],
                            [sg.Text('')]
                        ]
        # frame for booking values
        self.frame3 =   [
                            [sg.CalendarButton('Select booking date', target='input1', key='date', format=None)],
                            [sg.In('', size=(20,1), key='input1'), sg.Button(button_text='OK', key='OK'), sg.Text('', size=(37, 1))],
                            [sg.Text('Book returned: ', size=(12,1), key='selReturned'), 
                             sg.Radio('Yes','R', size=(10,1), key='returnedYes'),
                             sg.Radio('No','R', size=(10,1), key='returnedNo', default = True)]
                        ]
        # frame for bookings
        self.frame4 =   [
                            [sg.Text('BOOKSTORE', justification='center', size=(60,1))],
                            [sg.Table(values=data[0:][:], headings=colHeadings, key='TABLE', num_rows=10, enable_events=True, justification='center',
                            auto_size_columns=True)],
                            [sg.Text('')],
                            [sg.Button(button_text='Add', key='ADD', size=(8,1)),
                             sg.Button(button_text='Update', key='UPDATE', size=(8,1)),
                             sg.Button(button_text='Delete', key='DELETE', size=(8,1))]
                        ]  
        self.frame5 =   [
                            [sg.Frame('', self.frame2)],
                            [sg.Frame('', self.frame3)]
                        ]
                   

        self.layout =   [
                            [sg.Menu(self.menu_booking, tearoff=False, visible=True)],
                            [sg.Frame('', self.frame1),sg.Frame('', self.frame5)],
                            [sg.Text('', size=(30,1)), 
                            sg.Frame('', self.frame4, title_color='blue', size=(10,1), element_justification='center')],
                            [sg.Text('')]
                        ]

        # Create the form
        self.window = sg.Window('Booking form').Layout(self.layout).Finalize()

        self.populateMembers()
        self.populateBooks()

        # Read the form
        while True:
            event, values = self.window.Read()

            if event == 'Members':
                MembersForm()
            elif event == 'Books':
                BooksForm()
            elif event == 'Exit':
                break
            if event == 'selMEMBER':
                self.memberSelected(values)
            elif event == 'selBOOK':
                self.bookSelected(values)
            elif event == 'returnedYes':
                returnedSelected = True
            elif event == 'returnedNo':
                returnedSelected = False
            elif event == 'OK':
                dateSelected = values['input1'][0:10]
            elif event == 'ADD':
                self.addBooking(values)
            elif event == 'TABLE':
                self.rowSelected(values)
            elif event == 'UPDATE':
                self.updateBooking(values)
            elif event == 'DELETE':
                self.deleteBooking(values)
            elif event == 'Pending Bookings':
                self.pendingBookings()
            elif event == 'All Bookings':
                self.allBookings()
        
        self.window.Close()

    #-------------------------------------------------------------------

    def populateMembers(self):
        dataM = [] # variable for storing all members
        conn = None

        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')

            # create a cursor
            cur = conn.cursor()

            # query to get all members from table Members
            selectMembers = "SELECT * FROM \"Bookstore\".\"Members\" order by \"memberID\""
            cur.execute(selectMembers)
            self.rowsM = cur.fetchall()

            dataM.clear()
            for row in self.rowsM:
                dataM.append(row)
            
            # getting id, first name and last name of all members
            dataSel = []
            for data in dataM:
                dataSel.append([data[0], data[8], data[1]])
            
            self.window.FindElement('selMEMBER').Update(values=dataSel)              
                
        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("Populate Members", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()

#-------------------------------------------------------------------

    def populateBooks(self):
        dataB = [] # variable for storing all books
        conn = None

        try:
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')
            cur = conn.cursor()

            # query to get all books from table Books
            selectBooks = "SELECT * FROM \"Bookstore\".\"Books\" ORDER BY \"bookID\""
            cur.execute(selectBooks)
            self.rowsB = cur.fetchall()

            dataB.clear()
            for row in self.rowsB:
                dataB.append(row[0:2])

            self.window.FindElement("selBOOK").Update(values=dataB)   
     
          
        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("Populate Books", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()

    #-------------------------------------------------------------------

    def memberSelected(self, values):
        global idSelectedM
        global nameSelectedM

        # get id and full name of the selected member
        idSelectedM = values['selMEMBER'][0]
        nameSelectedM = values['selMEMBER'][1] + ' ' + values['selMEMBER'][2]


        for row in self.rowsM:
            if (idSelectedM == row[0]):
                self.window.FindElement("firstName").Update(str(row[8]))
                self.window.FindElement("lastName").Update(str(row[1]))
                self.window.FindElement("address").Update(str(row[2]))
                self.window.FindElement("city").Update(str(row[3]))
                self.window.FindElement("country").Update(str(row[4]))
                self.window.FindElement("birthday").Update(str(row[5]))
                self.window.FindElement("phoneNumber").Update(str(row[6]))
                self.window.FindElement("gender").Update(str(row[7]))

                break

        self.tablePopulate()

    #------------------------------------------------------------------

    def bookSelected(self, values):
        global idSelectedB
        global titleSelectedB

        # get book id and book title
        idSelectedB = values['selBOOK'][0]
        titleSelectedB = values['selBOOK'][1]

        for row in self.rowsB:
            if (idSelectedB == row[0]):
                self.window.FindElement("title").Update(str(row[1]))
                self.window.FindElement("author").Update(str(row[2]))
                self.window.FindElement("publisher").Update(str(row[3]))
                self.window.FindElement("genre").Update(str(row[4]))
                self.window.FindElement("pubYear").Update(int(row[5]))
                break
        
    #------------------------------------------------------------------

    def tablePopulate(self):
        conn = None

        # empty the table
        data[:] = []
        self.window.Element('TABLE').Update(values=data)

        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')

            # create a cursor
            cur = conn.cursor()

            # query to get all bookings for one member
            selectMemberBookings = "SELECT * FROM \"Bookstore\".\"Bookstore\" WHERE \"memberID\" = %s ORDER BY \"bookingID\";"
            cur.execute(selectMemberBookings, (idSelectedM,))
            self.bookingRows = cur.fetchall()

            for row in self.bookingRows:
                # query get book name from table Books
                selectBook = "SELECT \"title\" FROM \"Bookstore\".\"Books\" WHERE \"bookID\"=%s"
                cur.execute(selectBook, (row[2],))
                rowBook = cur.fetchone()

                # creating a record for the table - element TABLE
                d = [row[0], idSelectedM, nameSelectedM, row[2], rowBook, row[3], row[4]]
                data.append(d)
            self.window.Element('TABLE').Update(values=data)

        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("Populate Table", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()

    #------------------------------------------------------------------

    def addBooking(self, values):
        
        conn = None

        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')

            # create a cursor
            cur = conn.cursor()

            idM = idSelectedM     # id of selected member
            idB = idSelectedB     # id of selected book
            bookingDate = dateSelected
            returned = returnedSelected

            # query to insert booking into new booking in the table Bookstore
            bookingtInsert = "INSERT INTO \"Bookstore\".\"Bookstore\" (\"memberID\", \"bookID\", \"bookingDate\", \"returned\") VALUES(%s, %s, %s, %s)"
            bookingRec = (idM, idB, bookingDate, returned)
            cur.execute(bookingtInsert, bookingRec)
            conn.commit()

            # call tablePopulate to update the shown table
            self.tablePopulate()

        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("Add Booking", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()

    #------------------------------------------------------------------
    def rowSelected(self, values):
        global rowInd
        global rowValues
        global dateSelectedUpdate

        # get index and values of selected row to be able to update them
        rowInd = values['TABLE'][0]
        rowValues = data[rowInd]
        dateSelectedUpdate = rowValues[5]


    # ----------------------------------------------- 

    def updateBooking(self, values):
        if (values['input1']):
            dateSelectedUpdate = values['input1'][0:10]
        else:
            dateSelectedUpdate = rowValues[5]
        rowValues[5] = dateSelectedUpdate   # updating date

        # updating variable returned
        if values['returnedYes'] == True:
            rowValues[6] = True
        else:
            rowValues[6] = False

        conn = None

        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')

            # create a cursor
            cur = conn.cursor()

            # query to update Bookstore table
            bookingUpdate = "UPDATE \"Bookstore\".\"Bookstore\" SET \"bookingDate\" = %s, returned = %s WHERE \"bookingID\" = %s" 
            cur.execute(bookingUpdate, (rowValues[5], rowValues[6], rowValues[0]))
            conn.commit()

            # update the row in form table
            data[rowInd] = rowValues
            self.window.Element('TABLE').Update(values=data)

        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("Update Booking", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()

    # ----------------------------------------------- 

    def deleteBooking(self, values):
        conn = None

        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')

            # create a cursor
            cur = conn.cursor()

            # quero to delete a row in Bookstore table
            bookingDelete = "DELETE FROM \"Bookstore\".\"Bookstore\" WHERE \"bookingID\"=%s" 
            cur.execute(bookingDelete, (rowValues[0],))
            conn.commit()

            # delete the row from form table
            del data[rowInd]
            self.window.Element('TABLE').Update(values=data)

        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("Delete Booking", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()
    
    # --------------------------------------------------
    # function to get all books that have not been returned
    def pendingBookings(self):
        conn = None

        # empty the table
        data[:] = []
        self.window.Element('TABLE').Update(values=data)

        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')

            # create a cursor
            cur = conn.cursor()

            # query to get all bookings that are pending (not returned)
            selectPendingBookings = "SELECT * FROM \"Bookstore\".\"Bookstore\" WHERE \"returned\" = False ORDER BY \"bookingID\";"
            cur.execute(selectPendingBookings)
            self.bookingRows = cur.fetchall()

            for row in self.bookingRows:
                # query to get book name from table Books
                selectBook = "SELECT \"title\" FROM \"Bookstore\".\"Books\" WHERE \"bookID\"=%s"
                cur.execute(selectBook, (row[2],))
                rowBook = cur.fetchone()

                # query to get full name of member with pending booking
                selectBook = "SELECT \"firstName\", \"lastName\" FROM \"Bookstore\".\"Members\" WHERE \"memberID\"=%s"
                cur.execute(selectBook, (row[1],))
                memberName = cur.fetchone()

                # creating a record for the table - element TABLE
                d = [row[0], row[1], memberName, row[2], rowBook, row[3], row[4]]
                data.append(d)
            self.window.Element('TABLE').Update(values=data)

        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("Pending Bookings ", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()

    # ------------------------------------------
    # function to get all bookings
    def allBookings(self):
        conn = None

        # empty the table
        data[:] = []
        self.window.Element('TABLE').Update(values=data)

        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')

            # create a cursor
            cur = conn.cursor()

            # query to get all bookings
            selectAllBookings = "SELECT * FROM \"Bookstore\".\"Bookstore\" ORDER BY \"bookingID\";"
            cur.execute(selectAllBookings)
            self.bookingRows = cur.fetchall()

            for row in self.bookingRows:
                # query to get book name from table Books
                selectBook = "SELECT \"title\" FROM \"Bookstore\".\"Books\" WHERE \"bookID\"=%s"
                cur.execute(selectBook, (row[2],))
                rowBook = cur.fetchone()

                # query to get full name of member with pending booking
                selectBook = "SELECT \"firstName\", \"lastName\" FROM \"Bookstore\".\"Members\" WHERE \"memberID\"=%s"
                cur.execute(selectBook, (row[1],))
                memberName = cur.fetchone()

                # creating a record for the table - element TABLE
                d = [row[0], row[1], memberName, row[2], rowBook, row[3], row[4]]
                data.append(d)
            self.window.Element('TABLE').Update(values=data)

        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("All Bookings ", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()

if __name__ == '__main__':
    bookstoreForm()
