from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig

import sys

# FIXED: Removed the quotes from __name__ 
# This line now says: "If this file is being run directly, do the following:"
if __name__ == '__main__':
    try:
        # 1. SETUP THE CONFIGURATION
        # We first create the 'Plan' (the timestamps and folder names)
        trainingpipelineconfig = TrainingPipelineConfig()
        
        # 2. SETUP THE DATA INGESTION PLAN
        # We tell the system WHERE to put the data based on the plan above
        dataingestionconfig = DataIngestionConfig(trainingpipelineconfig)
        
        # 3. INITIALIZE THE WORKER
        # We create the 'Machine' (DataIngestion) and give it our plan
        data_ingestion = DataIngestion(dataingestionconfig)
        
        logging.info("Initiated the data ingestion process...")
        
        # 4. RUN THE MACHINE
        # This actually connects to MongoDB, downloads the data, and saves it.
        # It returns the 'Artifact' (the receipt)
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        
        # 5. SEE THE RESULTS
        # This will now print the location of your Train and Test files!
        print("--- Data Ingestion Successful ---")
        print(f"Train File Path: {data_ingestion_artifact.trained_file_path}")
        print(f"Test File Path: {data_ingestion_artifact.test_file_path}")
        
    except Exception as e:
        # If anything breaks (like MongoDB connection), this catches it
        raise NetworkSecurityException(e, sys)