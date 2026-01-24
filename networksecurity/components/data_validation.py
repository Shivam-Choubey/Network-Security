"""
SECTION 1: IMPORTS & TOOLS
This section brings in the mathematical and system tools needed to verify data.
"""
# Artifacts & Configs (The instructions and receipts)
from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig

# Error Handling & Logging (The communication tools)
from networksecurity.exception.exception import NetworkSecurityException 
from networksecurity.logging.logger import logging 

# Constants & Math (The rules and the calculator)
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from scipy.stats import ks_2samp # Kolmogorov-Smirnov test: Detects if data patterns changed
import pandas as pd             # The "Excel" of Python
import os, sys                  # For computer folders and system errors

# Utils (Small helper functions for reading files)
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file

# =============================================================================

class DataValidation:
    """
    PURPOSE: This class checks if the data we downloaded from MongoDB is 'healthy'.
    It checks two things: 
    1. Structure: Does it have the right number of columns?
    2. Distribution: Does the testing data look like the training data? (Data Drift)
    """

    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_config: DataValidationConfig):
        """
        CONSTRUCTOR: Initializes the 'Validation Machine'.
        - Takes the output from the Ingestion stage.
        - Loads the 'Schema' (the master blueprint of how the data SHOULD look).
        """
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            # Load the YAML blueprint that defines our expected columns
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # -------------------------------------------------------------------------
    # SECTION 2: HELPER METHODS (The Tools)
    # -------------------------------------------------------------------------

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        """Simply reads a CSV file from a path and returns a table."""
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        """
        CHECK: Does the CSV have the exact number of columns we expected?
        If MongoDB was changed and a column is missing, this will return False.
        """
        try:
            expected_count = len(self._schema_config)
            actual_count = len(dataframe.columns)
            
            logging.info(f"Checking columns... Expected: {expected_count}, Got: {actual_count}")
            
            # Comparison check
            if actual_count == expected_count:
                return True 
            return False 
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # -------------------------------------------------------------------------
    # SECTION 3: DATA DRIFT DETECTION (The Math)
    # -------------------------------------------------------------------------

    def detect_dataset_drift(self, base_df, current_df, threshold=0.05) -> bool:
        """
        CHECK: Is the new data (Test) statistically similar to the old data (Train)?
        
        Why this matters: If your model was trained on people aged 20-30, but 
        the new data is for people aged 60-70, the AI will make mistakes. 
        This 'Drift' detection catches that difference.
        """
        try:
            status = True # We start by assuming there is no drift
            report = {}   # We will save the math results for every column here
            
            for column in base_df.columns:
                train_data = base_df[column]
                test_data = current_df[column]
                
                # KS Test: A math test that checks if two groups follow the same pattern.
                # It gives us a 'p-value'.
                drift_test = ks_2samp(train_data, test_data)
                
                # If p-value is VERY small (less than 0.05), the data has drifted.
                if threshold <= drift_test.pvalue:
                    drift_found = False
                else:
                    drift_found = True
                    status = False # Even if ONE column drifts, the whole set is flagged
                
                # Store results for this column in our report dictionary
                report.update({column: {
                    "p_value": float(drift_test.pvalue),
                    "drift_status": drift_found
                }})
            
            # Save the math report to a YAML file so you can check it later
            drift_report_path = self.data_validation_config.drift_report_file_path
            os.makedirs(os.path.dirname(drift_report_path), exist_ok=True)
            write_yaml_file(file_path=drift_report_path, content=report)
            
            return status
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # -------------------------------------------------------------------------
    # SECTION 4: MAIN EXECUTION (The Workflow)
    # -------------------------------------------------------------------------

    def initiate_data_validation(self) -> DataValidationArtifact:
        """
        The 'Start' Button. It runs all checks in order:
        1. Read Files -> 2. Check Columns -> 3. Check Drift -> 4. Export Artifact
        """
        try:
            # 1. Get file paths from the Ingestion stage receipt
            train_path = self.data_ingestion_artifact.trained_file_path
            test_path = self.data_ingestion_artifact.test_file_path

            # 2. Load the data into tables
            train_df = self.read_data(train_path)
            test_df = self.read_data(test_path)

            # 3. Perform Column Check
            # We check both files to make sure they follow the Blueprint (Schema)
            if not self.validate_number_of_columns(dataframe=train_df):
                logging.warning("Training columns do not match the Schema!")
            
            if not self.validate_number_of_columns(dataframe=test_df):
                logging.warning("Testing columns do not match the Schema!")

            # 4. Perform Data Drift Check
            # Compares Training vs Testing mathematically
            drift_status = self.detect_dataset_drift(base_df=train_df, current_df=test_df)

            # 5. Save the 'Validated' files to their new home in the Artifacts folder
            valid_train_path = self.data_validation_config.valid_train_file_path
            os.makedirs(os.path.dirname(valid_train_path), exist_ok=True)
            
            train_df.to_csv(valid_train_path, index=False, header=True)
            test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False, header=True)

            # 6. RETURN THE RECEIPT (Artifact)
            # This tells the NEXT step (Transformation) where the good data is.
            return DataValidationArtifact(
                validation_status=drift_status,
                valid_train_file_path=valid_train_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)