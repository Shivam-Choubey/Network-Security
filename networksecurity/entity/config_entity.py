from datetime import datetime  
import os                       # Used to join folder names into a path (e.g., folder/subfolder/file)

# We are importing the constants you just wrote in the previous file
from networksecurity.constant import training_pipeline 

# These print statements help you check if the constants are loading correctly when you run the code
print(training_pipeline.PIPELINE_NAME)
print(training_pipeline.ARTIFACT_DIR)

# =============================================================================
# CLASS: TrainingPipelineConfig
# =============================================================================
# This class sets up the main folder structure for the entire run.
class TrainigPipelineConfig:
    def __init__(self, timestamp = datetime.now()):
        # 1. Create a unique timestamp (e.g., 10_25_2024_14_30_05)
        # This ensures every time you run the code, it creates a NEW folder so you don't overwrite old results.
        timestamp = timestamp.strftime("%m_%d_%Y_%H_%M_%S") # Month_Day_Year_Hour_Min_Sec
        
        self.pipeline_name = training_pipeline.PIPELINE_NAME
        self.artifact_name = training_pipeline.ARTIFACT_DIR
        
        # 2. Path: Artifacts/10_25_2024_14_30_05
        # os.path.join makes sure the path works on Windows, Mac, or Linux automatically.
        self.artifact_dir = os.path.join(self.artifact_name, timestamp)
        self.timestamp: str = timestamp

# =============================================================================
# CLASS: DataIngestionConfig
# =============================================================================
# This class sets up the specific "mailing addresses" for data files.
class DataIngestionConfig:
    def __init__(self, training_pipeline_config: TrainigPipelineConfig):
        
        # 1. Main folder for ingestion: Artifacts/TIMESTAMP/data_ingestion
        self.data_ingestion_dir: str = os.path.join(
            training_pipeline_config.artifact_dir, 
            training_pipeline.DATA_INGESTION_DIR_NAME
        )
        
        # 2. Path to the raw feature store: Artifacts/TIMESTAMP/data_ingestion/feature_store/phisingData.csv
        self.feature_store_file_path: str = os.path.join(
            self.data_ingestion_dir, 
            training_pipeline.DATA_INGESTION_FEATURE_STORE_DIR, 
            training_pipeline.FILE_NAME
        )
        
        # 3. Path where the TRAIN file will go: Artifacts/TIMESTAMP/data_ingestion/ingested/train.csv
        self.training_file_path: str = os.path.join(
            self.data_ingestion_dir, 
            training_pipeline.DATA_INGESTION_INGESTION_DIR, 
            training_pipeline.TRAIN_FILE_NAME
        )
        
        # 4. Path where the TEST file will go: Artifacts/TIMESTAMP/data_ingestion/ingested/test.csv
        self.testing_file_path: str = os.path.join(
            self.data_ingestion_dir, 
            training_pipeline.DATA_INGESTION_INGESTION_DIR, # Note: corrected logic here to use ingestion dir
            training_pipeline.TEST_FILE_NAME
        )
        
        # 5. Bringing in database details from our constants
        self.train_test_split_ration: float = training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO
        self.collection_name: str = training_pipeline.DATA_INGESTION_COLLECTION_NAME
        self.databae_name: str = training_pipeline.DATA_INGESTION_DATABASE_NAME