import os
import sys

# --- 1. ERROR HANDLING & LOGGING ---
# These ensure we can track what the code is doing and catch bugs easily.
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

# --- 2. THE WORKER COMPONENTS ---
# These are the actual scripts that do the heavy lifting (Ingestion, Cleaning, Training).
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

# --- 3. THE CONFIGURATIONS (INPUTS) ---
# These files contain 'settings' (e.g., folder paths, database URLs).
from networksecurity.entity.config_entity import(
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
)

# --- 4. THE ARTIFACTS (OUTPUTS) ---
# These are 'receipts' or 'packages' created by one step to be used by the next.
from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact,
)

# --- 5. CONSTANTS ---
# Fixed values like the name of your AWS S3 bucket.
from networksecurity.constant.training_pipeline import TRAINING_BUCKET_NAME
from networksecurity.constant.training_pipeline import SAVED_MODEL_DIR

class TrainingPipeline:
    def __init__(self):
        """
        CONSTRUCTOR: Initializes the master configuration for the entire pipeline.
        This sets up things like the current timestamp and root artifact folders.
        """
        self.training_pipeline_config = TrainingPipelineConfig()

    # ==========================================
    # STEP 1: DATA INGESTION (Getting the Data)
    # ==========================================
    def start_data_ingestion(self):
        try:
            # 1.1 Load the specific settings for ingestion
            self.data_ingestion_config = DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Step 1: Starting data Ingestion (Downloading/Splitting data)")
            
            # 1.2 Initialize the component and run it
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            
            # 1.3 Return the 'Artifact' (this tells Step 2 where the files are)
            logging.info(f"Data Ingestion done. Artifact created at: {data_ingestion_artifact}")
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ==========================================
    # STEP 2: DATA VALIDATION (Checking the Data)
    # ==========================================
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact):
        try:
            # 2.1 Get settings for validation
            data_validation_config = DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            
            # 2.2 Link the output of Step 1 into this step
            data_validation = DataValidation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_config=data_validation_config
            )
            
            logging.info("Step 2: Starting data Validation (Checking columns/types)")
            data_validation_artifact = data_validation.initiate_data_validation()
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ==========================================
    # STEP 3: DATA TRANSFORMATION (Cleaning the Data)
    # ==========================================
    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact):
        try:
            # 3.1 Get settings for transformation
            data_transformation_config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            
            # 3.2 Pass the validated data into the transformer
            data_transformation = DataTransformation(
                data_validation_artifact=data_validation_artifact,
                data_transformation_config=data_transformation_config
            )
            
            logging.info("Step 3: Starting data Transformation (Imputing/Scaling)")
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ==========================================
    # STEP 4: MODEL TRAINING (The 'AI' Part)
    # ==========================================
    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        try:
            # 4.1 Get settings for the trainer (like algorithm choices)
            self.model_trainer_config: ModelTrainerConfig = ModelTrainerConfig(
                training_pipeline_config=self.training_pipeline_config
            )

            # 4.2 Use the transformed data to train the model
            model_trainer = ModelTrainer(
                data_transformation_artifact=data_transformation_artifact,
                model_trainer_config=self.model_trainer_config,
            )

            logging.info("Step 4: Starting Model Training")
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ==========================================
    # CLOUD SYNC: BACKING UP TO THE CLOUD (AWS)
    # ==========================================
    def sync_artifact_dir_to_s3(self):
        """Moves all intermediate files (data, logs) from your PC to AWS S3 bucket."""
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder=self.training_pipeline_config.artifact_dir, aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def sync_saved_model_dir_to_s3(self):
        """Moves the final 'best model' to AWS so it can be used for predictions."""
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/final_model/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder=self.training_pipeline_config.model_dir, aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ==========================================
    # THE MASTER SWITCH: RUN PIPELINE
    # ==========================================
    def run_pipeline(self):
        """
        This function connects all the steps above in a logical chain.
        """
        try:
            # 1. Get raw data
            data_ingestion_artifact = self.start_data_ingestion()
            
            # 2. Feed raw data output into Validation
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            
            # 3. Feed validated data output into Transformation
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            
            # 4. Feed cleaned data output into Model Trainer
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)
            
            # 5. Backup the results to AWS Cloud
            self.sync_artifact_dir_to_s3()
            self.sync_saved_model_dir_to_s3()
            
            # Final output: The trained model details!
            return model_trainer_artifact
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)