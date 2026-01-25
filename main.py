# =============================================================================
# SECTION 1: THE IMPORTS (Hiring the Departments)
# =============================================================================
# We import the "Workers" (Components)
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

# We import the "Instruction Manuals" (Configs)
from networksecurity.entity.config_entity import (
    DataIngestionConfig, DataValidationConfig, 
    DataTransformationConfig, ModelTrainerConfig, TrainingPipelineConfig
)

# We import our safety tools
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import sys

# =============================================================================
# SECTION 2: THE EXECUTION (The Factory Floor)
# =============================================================================
if __name__ == '__main__':
    try:
        # STEP 0: Create the Global Project Plan (Timestamps, Folder Roots)
        trainingpipelineconfig = TrainingPipelineConfig()

        # ---------------------------------------------------------------------
        # STEP 1: DATA INGESTION (Raw Materials)
        # Goal: Get data from MongoDB and split into Train/Test CSVs.
        # ---------------------------------------------------------------------
        dataingestionconfig = DataIngestionConfig(trainingpipelineconfig)
        data_ingestion = DataIngestion(dataingestionconfig)
        
        logging.info("Initiate the data ingestion")
        dataingestionartifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data Initiation Completed")
        print(dataingestionartifact)

        # ---------------------------------------------------------------------
        # STEP 2: DATA VALIDATION (Quality Control)
        # Goal: Check if columns match the Schema and check for Data Drift.
        # ---------------------------------------------------------------------
        data_validation_config = DataValidationConfig(trainingpipelineconfig)
        data_validation = DataValidation(dataingestionartifact, data_validation_config)
        
        logging.info("Initiate the data Validation")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("data Validation Completed")
        print(data_validation_artifact)

        # ---------------------------------------------------------------------
        # STEP 3: DATA TRANSFORMATION (Processing)
        # Goal: Clean the data, handle missing values, and convert to numbers.
        # ---------------------------------------------------------------------
        data_transformation_config = DataTransformationConfig(trainingpipelineconfig)
        logging.info("data Transformation started")
        
        # We pass the VALIDATION receipt here to ensure we only transform good data
        data_transformation = DataTransformation(data_validation_artifact, data_transformation_config)
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        
        print(data_transformation_artifact)
        logging.info("data Transformation completed")

        # ---------------------------------------------------------------------
        # STEP 4: MODEL TRAINING (The Brain)
        # Goal: Train the AI model and save it as a .pkl file.
        # ---------------------------------------------------------------------
        logging.info("Model Training started")
        model_trainer_config = ModelTrainerConfig(trainingpipelineconfig)
        
        # We pass the TRANSFORMATION receipt so the trainer knows where the clean numbers are
        model_trainer = ModelTrainer(
            model_trainer_config=model_trainer_config,
            data_transformation_artifact=data_transformation_artifact
        )
        model_trainer_artifact = model_trainer.initiate_model_trainer()

        logging.info("Model Training artifact created")
        print(model_trainer_artifact)
        
    except Exception as e:
        # If any step above fails, the whole pipeline stops and reports the error
        raise NetworkSecurityException(e, sys)