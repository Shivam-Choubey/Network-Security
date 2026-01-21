# =========================================================================================
# LIBRARY IMPORTS: Bringing in the tools we need
# =========================================================================================
import os                      # Operating System: Used to read file paths and environment variables
import sys                     # System: Used to access Python interpreter details (needed for our error handler)
import json                    # JSON: A data format (JavaScript Object Notation) used to exchange data between Python and MongoDB

# dotenv: Helps keep secrets (like database passwords) safe by loading them from a separate .env file
from dotenv import load_dotenv
load_dotenv()                  # This command looks for the file named '.env' and prepares the variables inside it

# os.getenv: This looks inside your .env file and finds the value labeled "MONGO_DB_URL"
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)            # Helpful for beginners to see if the connection string was actually found


# certifi: MongoDB Atlas (Cloud) requires a secure SSL connection. 
# This library provides 'Root Certificates' to prove our computer is a trusted source.
import certifi
ca = certifi.where()           # 'ca' is the path to the certificate file on your computer

import pandas as pd            # Pandas: The industry standard for handling data in tables (DataFrames)
import numpy as np             # Numpy: Handles complex math; Pandas uses this behind the scenes
import pymongo                 # PyMongo: The official bridge that allows Python to "talk" to MongoDB
from networksecurity.exception.exception import NetworkSecurityException # Your custom error "reporter"
from networksecurity.logging.logger import logging                       # Your custom "diary" to record what the script does


# =========================================================================================
# THE CLASS: Blueprint for our data pipeline
# =========================================================================================
class NetworkDataExtract():
    """
    This class is like a specialized worker whose only job is to:
    1. Read a CSV file.
    2. Convert it into a MongoDB-friendly format.
    3. Upload it to the cloud.
    """
    def __init__(self):
        """ This runs automatically when we create 'networkobj' """
        try:
            pass               # No special setup needed right now, so we just pass through
        except Exception as e:
            # If the class fails to even start, our custom exception captures the error (e) and sys info
            raise NetworkSecurityException(e, sys)
    
    def csv_to_json_converter(self, file_path):
        """
        TRANSFORMATION LOGIC: MongoDB does not understand CSV files (rows/columns).
        It understands 'Documents' (Key-Value pairs). We must convert them.
        """
        try:
            # pd.read_csv: Reads your .csv file and turns it into a 'DataFrame' (like an Excel sheet)
            data = pd.read_csv(file_path)
            
            # reset_index: Sometimes CSVs have hidden index columns. This removes them so the data is clean.
            data.reset_index(drop=True, inplace=True)
            
            # THE TRANSFORMATION STEPS:
            # 1. data.T -> 'Transpose'. This flips the table sideways.
            # 2. to_json() -> Turns that flipped table into a long string of text in JSON format.
            # 3. json.loads() -> Turns that long string of text back into a Python Dictionary.
            # 4. .values() -> Grabs only the data rows, ignoring the headers.
            # 5. list() -> Wraps everything in a list so we can send it all at once.
            records = list(json.loads(data.T.to_json()).values())
            
            return records     # This is now a 'list of dictionaries', which MongoDB loves
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self, records, database, collection):
        """
        DATABASE INGESTION: This sends the prepared data to the cloud.
        """
        try:
            # We store these variables inside the class ('self') so they can be accessed easily
            self.database = database
            self.collection = collection
            self.records = records
            
            # MongoClient: This starts the actual connection to your cloud cluster
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            
            # Select the specific Database inside your Cluster
            self.database = self.mongo_client[self.database]
            
            # Select the specific Collection (like a sheet/table) inside that Database
            self.collection = self.database[self.collection]
            
            # insert_many: This is a 'Bulk Operation'. Instead of sending rows one-by-one, 
            # it sends the entire list at once. This is much faster.
            self.collection.insert_many(self.records)
            
            # Return the count (how many rows we just pushed)
            return (len(self.records))
        except Exception as e:
            # If the internet fails or database is full, this tells us exactly where it happened
            raise NetworkSecurityException(e, sys)
            

# =========================================================================================
# MAIN EXECUTION: This is where the code actually starts running
# =========================================================================================
if __name__=='__main__':
    # 1. SETUP: Tell the code where the data is and where it should go
    FILE_PATH = r"Network_Data\phisingData.csv" # 'r' means 'Raw String' so Python doesn't get confused by backslashes
    DATABASE = "NetworkSecurityDatabase"        # The name you want for your DB in MongoDB Atlas
    Collection = "NetworkData"                  # The name for the table inside the DB
    
    # 2. INITIALIZE: Create the worker object
    networkobj = NetworkDataExtract()
    
    # 3. CONVERT: Turn the CSV file into Python-friendly records
    records = networkobj.csv_to_json_converter(file_path=FILE_PATH)
    
    # 4. PREVIEW: Let's see what the first few records look like in the terminal
    print(records)
    
    # 5. UPLOAD: Push the records to MongoDB and save the returned number to 'no_of_records'
    no_of_records = networkobj.insert_data_mongodb(records, DATABASE, Collection)

    # 6. FINAL REPORT: Tell the user the job is done!
    print(f"Success! {no_of_records} records have been pushed to MongoDB.")