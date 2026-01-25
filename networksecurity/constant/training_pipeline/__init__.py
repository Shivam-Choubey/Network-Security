import os  # Used for interacting with the operating system (creating folders, joining paths)
import sys # Used to manipulate different parts of the Python runtime environment
import pandas as pd # The standard library for data manipulation (DataFrames)
import numpy as np  # Used for mathematical operations and handling arrays

# =============================================================================
# GLOBAL PIPELINE CONSTANTS
# =============================================================================
# These variables define the "Who, What, and Where" of the entire project.

# This is the 'Answer' column in your data. Our model will try to predict this.
TARGET_COLUMN = "Result"

# The name of the overall project/pipeline.
PIPELINE_NAME: str = "NetworkSecurity"

# 'Artifacts' are things created by the code (like models or cleaned data).
# This variable defines the name of the folder where those things will be stored.
ARTIFACT_DIR: str = "Artifacts"

# The name of the primary raw dataset we are working with.
FILE_NAME: str = "phisingData.csv"

# Names for the files after we split our data into two parts.
TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"

SCHEMA_FILE_PATH = os.path.join("data_schema", "schema.yaml")

SAVED_MODEL_DIR =os.path.join("saved_models")t
MODEL_FILE_NAME = "model.pkl"


# =============================================================================
# DATA INGESTION RELATED CONSTANTS
# =============================================================================
# 'Data Ingestion' is the process of getting data from a source (like a database)
# and bringing it into our environment to work on it.

# The specific collection (table) name in the database.
DATA_INGESTION_COLLECTION_NAME: str = "NetworkData"

# The name of the database where the raw data is currently sitting.
DATA_INGESTION_DATABASE_NAME: str = "NetworkSecurityDatabase"

# The folder inside 'Artifacts' where all ingestion-related files will go.
DATA_INGESTION_DIR_NAME: str = "data_ingestion"

# Feature Store: A place to keep the 'features' (the data we use to make predictions).
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_score"

# The sub-folder where the finalized train/test files will be saved.
DATA_INGESTION_INGESTION_DIR: str = "ingested"

# Split Ratio: This means we take 20% of the data and hide it from the AI.
# We use that 20% later to 'test' the AI and see if it actually learned anything.
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2

PREPROCESSING_OBJECT_FILE_NAME = "preprocessing.pkl"


'''
Data Validation related constant start with the DATA_VALIDATION VAR NAME
'''
DATA_VALIDATION_DIR_NAME:str = "data_validation"
DATA_VALIDATION_VALID_DIR:str = "validation"
DATA_VALIDATION_INVALID_DIR:str = "invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR:str = "dirft_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME:str = "report.yaml"

"""
Data Transformation related constant start with DATA_TRANSFORMATION VAR NAME
"""
DATA_TRANSFORMATION_DIR_NAME: str = "data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR: str = "transformed"
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR: str = "transformed_object"

## kkn imputer to replace nan values
DATA_TRANSFORMATION_IMPUTER_PARAMS: dict = {
    "missing_values": np.nan,
    "n_neighbors": 3,
    "weights": "uniform",
}
DATA_TRANSFORMATION_TRAIN_FILE_PATH: str = "train.npy"

DATA_TRANSFORMATION_TEST_FILE_PATH: str = "test.npy"

"""
Model Trainer ralated constant start with MODE TRAINER VAR NAME
"""

MODEL_TRAINER_DIR_NAME: str = "model_trainer"
MODEL_TRAINER_TRAINED_MODEL_DIR: str = "trained_model"
MODEL_TRAINER_TRAINED_MODEL_NAME: str = "model.pkl"
MODEL_TRAINER_EXPECTED_SCORE: float = 0.6
MODEL_TRAINER_OVER_FIITING_UNDER_FITTING_THRESHOLD: float = 0.05

TRAINING_BUCKET_NAME = "netwworksecurity"



