# memebers.py

import PySimpleGUI as sg
import psycopg2

class MembersForm():
    def __init__(self):

        sg.theme('Reds')

        # form design
        self.frame_layout =     [
                                    [sg.Text('Bookstore members', justification='center', size=(60,1))],
                                    [sg.Text('First Name: ', size=(12,1)), sg.Input(size=(30,1), key='firstName'),
                                    sg.Text('', size=(12,1)), sg.Combo([], size=(20,1), enable_events=True, key='selMember', readonly=True)],
                                    [sg.Text('Last Name: ', size=(12,1)), sg.Input(size=(30,1), key='lastName')],
                                    [sg.Text('Address: ', size=(12,1)), sg.Input(size=(30,1), key='address')],
                                    [sg.Text('City: ', size=(12,1)), sg.Input(size=(30,1), key='city')],
                                    [sg.Text('Country: ', size=(12,1)), sg.Input(size=(30,1), key='country')],
                                    [sg.Text('Birthday: ', size=(12,1)), sg.In('', size=(20,1), key='birthday', disabled=True), sg.CalendarButton(button_text='Select', target='birthday', key='for_birthday', format=None)],
                                    [sg.Text('Gender: ', size=(12,1)), 
                                    sg.Radio('Female','R', size=(10,1), key='female', default=False),
                                    sg.Radio('Male','R', size=(10,1), key='male', default=False)],
                                    [sg.Text('Phone Number: ', size=(12, 1)), sg.Input(size=(20, 1), key='phoneNumber')],
                                    [sg.Text('')] 
                                ]

        self.layout =   [
                            [sg.Frame('', self.frame_layout, title_color='blue')],
                            [sg.Text('')],
                            [sg.Text('', size=(17,1)), 
                            sg.Button('Add', size=(8,1), key='add'),
                            sg.Button('Update', size=(8,1), key='update'),
                            sg.Button('Delete', size=(8,1), key='delete'),
                            sg.Button('Close', size=(8,1), key='close')],
                            [sg.Text('')]
                        ]

        # create the form
        self.window = sg.Window('Bookstore members').Layout(self.layout).Finalize()

        self.populateMembers()

        # Read the form
        while True:
            event, values = self.window.Read()

            if event == 'add':
                self.addMember(values)  
            elif event == 'selMember':
                self.selectMember(values)
            elif event == 'populate':
                self.populateMembers()
            elif event == 'update':
                self.updateMember(values)
            elif event == 'delete':
                self.deleteMember()     
            elif event == 'close':
                break
                

        self.window.Close()

    # ---------------------------------------------------------------------

    def addMember(self, values):
        conn = None

        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')

            # create a cursor
            cur = conn.cursor()

            # get values from the form
            firstName = str(values['firstName'])
            lastName = str(values['lastName'])
            address = str(values['address'])
            city = str(values['city'])
            country = str(values['country'])
            birthday = values['birthday'][0:10]
            phoneNumber = values['phoneNumber']

            if values['female']:
                gender = "Female"
            elif values['male']:
                gender = "Male"

            # query for inserting a member in the database table Members
            memberInsert = "INSERT INTO \"Bookstore\".\"Members\" (\"firstName\",\"lastName\",\"address\",\"city\",\"country\",\"birthday\",\"gender\",\"phoneNumber\") VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            memberRec = (firstName, lastName, address, city, country, birthday, gender, phoneNumber)
            cur.execute(memberInsert, memberRec)
            conn.commit()

            # popup after successful insertion

            x = "Member " + firstName + " " + lastName + " is inserted"
            sg.Popup(x)

            # clear
            self.clearFields()
            self.populateMembers()

        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("addMember", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()

    def populateMembers(self):
        data = []
        conn = None

        try:
            # connecting to database and creating cursor
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')
            cur = conn.cursor()

            # query to get all record from table Members
            selectMembers = "SELECT * FROM \"Bookstore\".\"Members\" order by \"memberID\""
            cur.execute(selectMembers)
            self.rows = cur.fetchall()

            
            data.clear()
            for row in self.rows:
                data.append(row)
            
            # Getting id, first name and last name 
            dataSelMem = []
            for d in data:
                dataSelMem.append([d[0], d[8], d[1]])

            self.window.FindElement("selMember").Update(values=dataSelMem)   

            self.clearFields()        
          
        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("Populate", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()
    # ---------------------------------------------------------------------

    def selectMember(self, values):
        global idSelected

        idSelected = values['selMember'][0]

        # updating fields with data of selected member
        for row in self.rows:
            if (idSelected == row[0]):
                self.window.FindElement("firstName").Update(str(row[8]))
                self.window.FindElement("lastName").Update(str(row[1]))
                self.window.FindElement("address").Update(str(row[2]))
                self.window.FindElement("city").Update(str(row[3]))
                self.window.FindElement("country").Update(str(row[4]))
                self.window.FindElement("birthday").Update(str(row[5]))
                self.window.FindElement("phoneNumber").Update(str(row[6]))
                if str(row[7]) == "Female":
                    self.window.FindElement("female").Update(value="True")
                elif str(row[7]) == "Male":
                    self.window.FindElement("male").Update(value="True")

                break

    # ---------------------------------------------------------------------

    def updateMember(self, values):
        conn = None

        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')

            # create a cursor
            cur = conn.cursor()

            # query to ger record from table Members with selected id
            selectMember = "SELECT * FROM \"Bookstore\".\"Members\" WHERE \"memberID\"=%s"
            cur.execute(selectMember, (idSelected,))
            self.row = cur.fetchone()

            firstName = str(values['firstName'])
            lastName = str(values['lastName'])
            address = str(values['address'])
            city = str(values['city'])
            country = str(values['country'])
            birthday = values['birthday'][0:10]
            phoneNumber = str(values['phoneNumber'])

            if values['female']:
                gender = "Female"
            elif values['male']:
                gender = "Male"

            # query to update selected record
            memberUpdate = "UPDATE \"Bookstore\".\"Members\" SET \"firstName\"=%s, \"lastName\"=%s, \"address\"=%s, \"city\"=%s, \"country\"=%s, \"birthday\"=%s, \"phoneNumber\"=%s, \"gender\"=%s WHERE \"memberID\"=%s"
            cur.execute(memberUpdate, (firstName, lastName, address, city, country, birthday, phoneNumber, gender, idSelected))
            conn.commit()

            # popup after successfully updating record
            x = "Record " + firstName + " " + lastName + " is updated"
            sg.Popup(x)
            self.clearFields()
            self.populateMembers()

        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("Update", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()

    # ---------------------------------------------------------------------

    def deleteMember(self):
        conn = None

        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(host="localhost",database="BookstoreDB",user="postgres", password="ema-mandal",port='5432')

            # create a cursor
            cur = conn.cursor()

            # query to delete a record form table Members
            memberDelete = "DELETE FROM \"Bookstore\".\"Members\" WHERE \"memberID\"=%s"
            cur.execute(memberDelete, (idSelected,))
            conn.commit()

            # popup after successfully deleting a record
            sg.Popup("Record is deleted")
            self.clearFields()
            self.populateMembers()

        except (Exception, psycopg2.DatabaseError) as error:
            sg.Popup("Delete", str(error))

        finally:
            if conn is not None:
                cur.close()
                conn.close()

    # ---------------------------------------------------------------------
    def clearFields(self):

        self.window.FindElement("firstName").Update("")
        self.window.FindElement("lastName").Update("")
        self.window.FindElement("address").Update("")
        self.window.FindElement("city").Update("")
        self.window.FindElement("country").Update("")
        self.window.FindElement("birthday").Update("")
        self.window.FindElement("phoneNumber").Update("")
        self.window.FindElement("female").Update(value="True")
        # ---------------------------------------------------------------------







if __name__ == '__main__':
    MembersForm()