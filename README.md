# Network Security – Phishing Detection System 🔐

This project is an **end-to-end Network Security application** focused on detecting **phishing attacks** using structured data.  
It follows **industry-level project architecture**, modular coding practices, logging, exception handling, CI/CD support, and deployment readiness using Docker.

---

## 📌 Project Overview

Phishing attacks are one of the most common cybersecurity threats.  
This project aims to build a **robust data pipeline** for phishing detection by:

- Ingesting network security data
- Validating and processing data
- Preparing the system for ML model training and deployment
- Supporting scalable and maintainable development

---

## 🗂️ Project Structure

```text
├── .github/
│   └── main.yml
├── data_schema/
│   └── schema.yaml
├── final_model/
│   ├── model.pkl
│   └── preprocessor.pkl
├── Network_Data/
│   └── phisingData.csv
├── networksecurity/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── data_ingestion.py
│   │   ├── data_transformation.py
│   │   ├── data_validation.py
│   │   └── model_trainer.py
│   ├── constant/
│   │   ├── training_pipeline/
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── entity/
│   │   ├── __inti__.py
│   │   ├── artifact_entity.py
│   │   └── config_entity.py
│   ├── exception/
│   │   ├── __init__.py
│   │   └── exception.py
│   ├── logging/
│   │   ├── __init__.py
│   │   └── logger.py
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── batch_prediction.py
│   │   └── training_pipeline.py
│   ├── utils/
│   │   ├── main_utils/
│   │   │   └── utils.py
│   │   ├── ml_utils/
│   │   │   ├── metric/
│   │   │   │   ├── __init__.py
│   │   │   │   └── classification_metric.py
│   │   │   └── model/
│   │   │       ├── __init__.py
│   │   │       └── estimator.py
│   │   └── __init__.py
│   └── __init_.py
├── prediction_output/
│   └── output.csv
├── templates/
│   ├── index.html
│   └── table.html
├── valid_data/
│   └── test.csv
├── .gitignore
├── app.py
├── Dockerfile
├── main.py
├── push_data.py
├── README.md
├── requirements.txt
├── setup.py
└── test_mongodb.py
