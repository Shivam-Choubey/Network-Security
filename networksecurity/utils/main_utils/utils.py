import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import os, sys
import numpy as np
import pickle # Used to save complex Python objects (like models) to your hard drive

from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV # The tool for 'Hyperparameter Tuning'

# ==========================================
# SECTION 1: YAML FILE HELPERS
# YAML files are used for configuration (like settings)
# ==========================================

def read_yaml_file(file_path: str) -> dict:
    """Reads a .yaml file and converts it into a Python Dictionary."""
    try:
        with open(file_path, "rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    """Writes data into a .yaml file. Good for saving settings/reports."""
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            yaml.dump(content, file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)

# ==========================================
# SECTION 2: NUMPY DATA HELPERS
# We save processed data as .npy files because they are fast and small.
# ==========================================
    
def save_numpy_array_data(file_path: str, array: np.array):
    """Saves a numerical array to the specified path."""
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True) # Create the folder if it doesn't exist
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def load_numpy_array_data(file_path: str) -> np.array:
    """Reads a .npy file back into a Python array."""
    try:
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

# ==========================================
# SECTION 3: OBJECT HELPERS (Pickling)
# Pickling is like 'freezing' a Python object so you can 'thaw' it later.
# ==========================================
    
def save_object(file_path: str, obj: object) -> None:
    """Saves a Python object (like a trained model or imputer) as a .pkl file."""
    try:
        logging.info("Entered the save_object method")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj) # 'dump' means save
        logging.info("Exited the save_object method")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_object(file_path: str) -> object:
    """Loads a .pkl file back into Python as a usable object."""
    try:
        if not os.path.exists(file_path):
            raise Exception(f"The file: {file_path} does not exist")
        with open(file_path, "rb") as file_obj:
            return pickle.load(file_obj) # 'load' means bring back to life
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

# ==========================================
# SECTION 4: THE MODEL EVALUATOR (The Brain)
# This is the most complex part of the utils file.
# ==========================================

def evaluate_models(X_train, y_train, X_test, y_test, models, param):
    """
    This function takes a list of models and a list of parameters, 
    tries every combination, and returns a report of how they performed.
    """
    try:
        report = {}

        # Loop through every model in our dictionary (e.g., Random Forest, Decision Tree)
        for i in range(len(list(models))):
            model = list(models.values())[i]
            para = param[list(models.keys())[i]] # Get the 'knobs' (params) for this specific model

            # --- GRID SEARCH ---
            # GridSearchCV acts like a scientist. It tries every setting you gave it
            # and uses 'Cross-Validation' (cv=3) to make sure the results are consistent.
            gs = GridSearchCV(model, para, cv=3)
            gs.fit(X_train, y_train)

            # --- RE-TRAINING ---
            # Now we take the 'Best Settings' found by the scientist (gs.best_params_)
            # and train the model one last time with those perfect settings.
            model.set_params(**gs.best_params_)
            model.fit(X_train, y_train)

            # --- SCORING ---
            # We ask the model to predict the training and testing data
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            # Calculate the R2 Score (Accuracy score for regression/classification)
            # Higher is better (1.0 is a perfect score)
            test_model_score = r2_score(y_test, y_test_pred)

            # Save the score in our report dictionary
            report[list(models.keys())[i]] = test_model_score

        return report # Returns something like {'RandomForest': 0.95, 'DecisionTree': 0.82}

    except Exception as e:
        raise NetworkSecurityException(e, sys)