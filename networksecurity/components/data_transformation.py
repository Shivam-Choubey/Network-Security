import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

# --- Project Specific Imports ---
# These are 'settings' and 'blueprints' defined in other parts of your folder
from networksecurity.constant.training_pipeline import TARGET_COLUMN
from networksecurity.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS

from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact, # A blueprint for the output of this script
    DataValidationArtifact      # A blueprint for the input (from the previous step)
)

from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.exception.exception import NetworkSecurityException 
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import save_numpy_array_data, save_object

class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig):
        """
        CONSTRUCTOR: When you create this class, you must provide:
        1. data_validation_artifact: Where the clean raw data is located.
        2. data_transformation_config: Where the final processed data should be saved.
        """
        try:
            self.data_validation_artifact = data_validation_artifact
            self.data_transformation_config = data_transformation_config
        except Exception as e:
            # If anything goes wrong, we use a custom error handler to tell us exactly where
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        """
        HELPING HAND: A simple tool to read a CSV file. 
        It's 'static' because it doesn't need to know anything about the class to work.
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def get_data_transformer_object(self) -> Pipeline:
        """
        THE ARCHITECT: This builds the 'instruction manual' for how to clean the data.
        It uses KNN (K-Nearest Neighbors) to fill in missing values.
        """
        logging.info("Building the KNN Imputer Pipeline...")
        try:
           # 1. Create the imputer (fills missing values by looking at similar rows)
           imputer: KNNImputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
           
           # 2. Put the imputer inside a 'Pipeline' (makes it easy to add more steps later)
           processor: Pipeline = Pipeline([("imputer", imputer)])
           
           return processor
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        """
        THE FACTORY LINE: This is the main function that executes everything.
        """
        logging.info("Starting data transformation...")
        try:
            # STEP 1: Load the files that were validated in the previous pipeline step
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            # STEP 2: Separate the 'Questions' from the 'Answers' in Training Data
            # input_feature = The data the model studies (Features)
            # target_feature = The result the model tries to guess (Label)
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            
            # Change '-1' labels to '0' so the math works better for binary classification
            target_feature_train_df = target_feature_train_df.replace(-1, 0)

            # STEP 3: Do the same separation for Testing Data
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1, 0)

            # STEP 4: Get our 'Cleaning Blueprint' (The Pipeline we made earlier)
            preprocessor = self.get_data_transformer_object()

            # STEP 5: THE CORE LOGIC
            # .fit() -> The imputer 'studies' the training data to learn the averages/patterns
            preprocessor_object = preprocessor.fit(input_feature_train_df)
            
            # .transform() -> Uses what it learned to actually fill in the missing gaps
            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df)
             
            # STEP 6: Combine Features and Target back into one single array
            # np.c_ is like 'glue' that sticks the columns together side-by-side
            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]

            # STEP 7: Save the results to your hard drive
            # We save as 'numpy' files because they are much faster for the model to read than CSVs
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)
            
            # We also save the 'preprocessor_object' (the pickle file)
            # This is crucial! You'll need this same object when you deploy your app to clean 'New' data.
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor_object)
            save_object("final_model/preprocessor.pkl", preprocessor_object)

            # STEP 8: Create the Artifact
            # This is just a message saying "Hey, I'm done! Here is where I put the files."
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
            return data_transformation_artifact
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)