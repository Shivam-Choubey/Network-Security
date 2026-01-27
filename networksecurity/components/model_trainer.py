import os
import sys

# Standard error handling and logging
from networksecurity.exception.exception import NetworkSecurityException 
from networksecurity.logging.logger import logging

# Importing 'Artifacts' (inputs from transformation) and 'Configs' (output settings)
from networksecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig

# Specialized tools for saving/loading and measuring model performance
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object, load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data, evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

# THE CANDIDATES: Different Machine Learning Algorithms
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig,
                 data_transformation_artifact: DataTransformationArtifact):
        """
        CONSTRUCTOR: Links the configuration (where to save model) 
        and the transformation artifact (where the clean data is).
        """
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def train_model(self, X_train, y_train, x_test, y_test):
        """
        THE TOURNAMENT: This method trains multiple models and picks the winner.
        """
        try:
            # STEP 1: Define a dictionary of models to try
            models = {
                "Random Forest": RandomForestClassifier(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier(),
            }

            # STEP 2: Hyperparameter Tuning
            # These are 'knobs' we turn to find the best settings for each model.
            params = {
                "Decision Tree": {
                    'criterion': ['gini', 'entropy', 'log_loss'],
                },
                "Random Forest": {
                    'n_estimators': [8, 16, 32, 128, 256]
                },
                "Gradient Boosting": {
                    'learning_rate': [.1, .01, .05, .001],
                    'subsample': [0.6, 0.7, 0.75, 0.85, 0.9],
                    'n_estimators': [8, 16, 32, 64, 128, 256]
                },
                "Logistic Regression": {}, # Basic settings
                "AdaBoost": {
                    'learning_rate': [.1, .01, .001],
                    'n_estimators': [8, 16, 32, 64, 128, 256]
                }
            }

            # STEP 3: Evaluation
            # evaluate_models is a custom function that trains every model in the list
            # and returns a report card with their scores.
            model_report: dict = evaluate_models(
                X_train=X_train, y_train=y_train, X_test=x_test, y_test=y_test,
                models=models, param=params
            )

            # STEP 4: Selecting the Winner
            # Find the highest score in the report card
            best_model_score = max(model_report.values())
            
            # Find the name of the model that achieved that high score
            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            best_model = models[best_model_name]

            # STEP 5: Scoring the Best Model
            # Calculate metrics like Precision, Recall, and F1-Score for the winner
            y_train_pred = best_model.predict(X_train)
            classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)

            y_test_pred = best_model.predict(x_test)
            classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)

            # STEP 6: Packaging for Production
            # We load the 'preprocessor' (imputer) we saved earlier
            preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)

            # We combine the PREPROCESSOR + BEST MODEL into one single object (NetworkModel)
            # This way, when you deploy, you only need one file to handle both cleaning and predicting.
            Network_Model = NetworkModel(preprocessor=preprocessor, model=best_model)

            # Save the final model object
            save_object(self.model_trainer_config.trained_model_file_path, obj=Network_Model)
            save_object("final_model/model.pkl", best_model) # Save a copy for easy access

            # STEP 7: Create the Artifact
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                train_metric_artifact=classification_train_metric,
                test_metric_artifact=classification_test_metric
            )
            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        """
        THE PREPARER: This prepares the data for the 'train_model' tournament.
        """
        try:
            # 1. Locate the transformed numpy arrays (from the previous pipeline stage)
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            # 2. Load the data back into memory
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            # 3. Slice the arrays: All columns except last = X (Features), Last column = y (Target)
            # train_arr[:, :-1] means 'take all rows and all columns except the very last one'
            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )

            # 4. Trigger the actual training process
            return self.train_model(x_train, y_train, x_test, y_test)

        except Exception as e:
            raise NetworkSecurityException(e, sys)