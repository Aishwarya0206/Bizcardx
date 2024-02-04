import mysql.connector
import datetime
import pandas as pd

class dataHandler:
    #Constructor
    def __init__(self, sql):
        self.host = sql["host"]
        self.user = sql["user"]
        self.password = sql["password"]
        self.database = sql["database"]

    #Connection to database
    def connect_db(self):
        try:
            db_conn = mysql.connector.connect(host=self.host,user=self.user,password=self.password,database=self.database,auth_plugin='mysql_native_password')
            cursor_db=db_conn.cursor()
            return({"cursor": cursor_db, "conn": db_conn})
        except Exception as e:
            return ("Error connecting to MySQL database: "+str(e))

    def execute_ddl(self, cursor_db, db_conn):
        try:
            bizcard_table = '''CREATE TABLE IF NOT EXISTS BusinessCardInfo (CompanyName VARCHAR(500), CardHolderName VARCHAR(150), Designation VARCHAR(200), MobileNumber VARCHAR(255), Email VARCHAR(500), Website VARCHAR(500), Area VARCHAR(255), City VARCHAR(255), State VARCHAR(255), Pincode VARCHAR(10), ImageName VARCHAR(100))'''
            cursor_db.execute(bizcard_table)
            db_conn.commit()
            #self.close_connection(cursor_db, db_conn)
            return("Table created")
        except Exception as e:
            db_conn.rollback()
            return("Error in execute_ddl "+str(e))

    def insert_bizcardx(self, cursor_db, db_conn, data):
        try:
            #print(data['Details']['Company_name'], data['Details']['Card_holder'], data['Details']['Designation'], data['image'])
            Mobile_number = self.change_list_to_string(data['Details']['Mobile_number']) if('Mobile_number' in data['Details'] and data['Details']['Mobile_number'] is not None) else None
            Email = self.change_list_to_string(data['Details']['Email']) if('Email' in data['Details'] and data['Details']['Email'] is not None) else None
            Website = self.change_list_to_string(data['Details']['Website']) if('Website' in data['Details'] and data['Details']['Website'] is not None) else None
            Area = self.change_list_to_string(data['Details']['Area']) if('Area' in data['Details'] and data['Details']['Area'] is not None) else None
            City = self.change_list_to_string(data['Details']['City']) if('City' in data['Details'] and data['Details']['City'] is not None) else None
            State = self.change_list_to_string(data['Details']['State']) if('State' in data['Details'] and data['Details']['State'] is not None) else None
            Pincode = self.change_list_to_string(data['Details']['Pin_code']) if('Pin_code' in data['Details'] and data['Details']['Pin_code'] is not None) else None
            print("Company Name " + data['Details']['Company_name'] if(data['Details']['Company_name'] is not None) else None  + "\nCard Holder " + data['Details']['Card_holder'] if(data['Details']['Card_holder'] is not None) else None+ "\nDesignation "+ data['Details']['Designation'] if(data['Details']['Designation'] is not None) else None + "\nMobile Number " + Mobile_number+ "\nEmail " + Email + "\nWebsite " + Website + "\nArea "+ Area + "\nCity " + City + "\nState " + State + "\nPincode "+Pincode +"\nImage "+data['image'])
            bizcard_table = '''INSERT INTO BusinessCardInfo (CompanyName, CardHolderName, Designation, MobileNumber, Email, Website, Area, City, State, Pincode, ImageName) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
            cursor_db.execute(bizcard_table, (data['Details']['Company_name'].replace(',', '') if('Company_name' in data['Details']) else None, data['Details']['Card_holder'] if('Card_holder' in data['Details']) else None, data['Details']['Designation'] if('Designation' in data['Details']) else None, Mobile_number, Email, Website, Area, City, State, Pincode, data['image']))
            print(cursor_db)
            db_conn.commit()
            #self.close_connection(cursor_db, db_conn)
            return("Bizcardx Data Added")
        except Exception as e:
            db_conn.rollback()
            return("Error in insert_bizcardx "+str(e))

    def change_list_to_string(self, list_of_values):
        try:
            return(', '.join(list_of_values) if len(list_of_values) > 1 else list_of_values[0])
        except Exception as e:
            return("Error in change_list_to_string "+str(e))

    def select_from_bizcardx(self, cursor_db, db_conn):
        try:
            select_query = '''SELECT CompanyName, CardHolderName AS CardHolder, Designation, MobileNumber, Email, Website, Area, City, State, Pincode FROM BusinessCardInfo'''
            bizCardxResult = pd.read_sql_query(select_query, db_conn)
            #self.close_connection(cursor_db, db_conn)
            return bizCardxResult
        except Exception as e:
            return("Error in fetching select_from_table : "+str(e))