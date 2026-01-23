# =============================================================================
# 1. IMPORTS: Bringing in our tools
# =============================================================================
# Custom tools for error tracking and progress logging
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

# 'Entities' act as organized containers for our folder paths (Config) 
# and our finished results (Artifact)
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

import os      # To handle file paths and create folders
import sys     # To get technical details if an error occurs
import numpy as np   # For mathematical operations
import pandas as pd  # To handle data in table format (DataFrames)
import pymongo       # The driver to connect to MongoDB database
from typing import List
from sklearn.model_selection import train_test_split # Tool to split data into Train/Test sets
from dotenv import load_dotenv # To read secret passwords/URLs from a .env file

# Load environment variables (like your MongoDB URL) so they aren't visible in code
load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

# =============================================================================
# 2. THE CLASS: The Machine that performs the work
# =============================================================================
class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        """
        Setup: This runs the moment the class is called. It takes the 'Config' 
        which is our instruction manual containing folder paths.
        """
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            # If initialization fails, raise our custom error with system details (sys)
            raise NetworkSecurityException(e, sys)
        
    def export_collection_as_dataframe(self):
        """
        Step 1: Connection. Pulling raw data from MongoDB and turning it 
        into a Python-friendly table (DataFrame).
        """
        try:
            # Get the database and collection names from our config instructions
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            
            # Connect to the database using our secret URL
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            collection = self.mongo_client[database_name][collection_name]

            # Convert the list of data from MongoDB into a Pandas Table
            df = pd.DataFrame(list(collection.find()))

            # MongoDB always adds a column called '_id'. We don't need it for AI, so we drop it.
            if "_id" in df.columns.to_list():
                df = df.drop(columns=["_id"], axis=1)
            
            # Replace 'na' text with 'NaN' (Not a Number) so Python understands it's missing data
            df.replace({"na": np.nan}, inplace=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_data_into_feature_store(self, dataframe: pd.DataFrame):
        """
        Step 2: Storage. Saving a raw copy of the data on your computer 
        as a 'Feature Store' (the master backup).
        """
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            
            # Find the folder name and create it if it doesn't exist yet
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            
            # Save the table as a CSV file on your hard drive
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            return dataframe
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        """
        Step 3: Preparation. Splitting the data into two parts: 
        one for the AI to learn from, and one to test it later.
        """
        try:
            # Split the data (e.g., 80% training, 20% testing)
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("Performed train test split on the dataframe")

            # Create the 'ingested' folder where these two files will live
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)
            
            logging.info("Exporting train and test files to CSV.")
            
            # Save the Training part to its path
            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )

            # Save the Testing part to its path
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )
            logging.info("Exported train and test files successfully.")

        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def initiate_data_ingestion(self):
        """
        The 'START' Button: This runs all the methods above in the correct order.
        """
        try:
            # 1. Get the data from DB
            dataframe = self.export_collection_as_dataframe()
            
            # 2. Save a raw copy to the Feature Store
            dataframe = self.export_data_into_feature_store(dataframe)
            
            # 3. Split it and save the Train/Test files
            self.split_data_as_train_test(dataframe)
            
            # 4. Create an 'Artifact' (A receipt) that tells the rest of the 
            # pipeline exactly where the new files are.
            dataingestionartifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )
            return dataingestionartifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)