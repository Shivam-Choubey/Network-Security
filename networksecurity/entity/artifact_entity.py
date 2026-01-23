from dataclasses import dataclass # A helper that creates classes used specifically for storing data

# =============================================================================
# 1. DATA INGESTION ARTIFACT
# =============================================================================
@dataclass
class DataIngestionArtifact:
    """
    The 'Receipt' from the Ingestion worker.
    It simply stores the paths to the raw CSV files we just downloaded and split.
    """
    trained_file_path: str  # Where the 80% training data is stored
    test_file_path: str     # Where the 20% testing data is stored

# =============================================================================
# 2. DATA VALIDATION ARTIFACT
# =============================================================================
@dataclass
class DataValidationArtifact:
    """
    The 'Quality Report' from the Validation worker.
    Before training, we check if the data is broken, missing, or 'drifting'.
    """
    validation_status: bool        # True = Data is good to go! False = Stop, something is wrong.
    valid_train_file_path: str     # Path to data that passed the quality check
    valid_test_file_path: str      # Path to data that passed the quality check
    invalid_train_file_path: str   # Path to 'bad' data (e.g., missing columns)
    invalid_test_file_path: str    # Path to 'bad' data (e.g., missing columns)
    drift_report_file_path: str    # Path to a report (YAML/JSON) showing if data changed over time
    
# =============================================================================
# 3. DATA TRANSFORMATION ARTIFACT
# =============================================================================
@dataclass
class DataTransformationArtifact:
    """
    The 'Processed Materials' receipt.
    The AI cannot read raw text; it needs numbers. This stage stores 
    the final transformed numbers and the 'tool' (object) used to convert them.
    """
    transformed_object_file_path: str # Path to the saved 'Scaler' or 'Encoder' (the math tool)
    transformed_train_file_path: str  # Path to the final numbers (usually .npy or .pkl)
    transformed_test_file_path: str   # Path to the final numbers (usually .npy or .pkl)

# =============================================================================
# 4. CLASSIFICATION METRIC ARTIFACT
# =============================================================================
@dataclass
class ClassificationMetricArtifact:
    """
    The 'Scorecard'.
    This stores the mathematical scores that tell us how smart the AI is.
    """
    f1_score: float        # The overall balance between accuracy and detection
    precision_score: float # How many 'Network Threats' it correctly identified
    recall_score: float    # How many total threats it managed to catch

# =============================================================================
# 5. MODEL TRAINER ARTIFACT
# =============================================================================
@dataclass
class ModelTrainerArtifact:
    """
    The 'Final Product' receipt.
    This is the most important artifact because it holds the actual trained AI Model.
    """
    trained_model_file_path: str # The physical location of the trained brain (.pkl file)
    
    # We store two scorecards: one for data it saw, and one for data it never saw.
    train_metric_artifact: ClassificationMetricArtifact
    test_metric_artifact: ClassificationMetricArtifact