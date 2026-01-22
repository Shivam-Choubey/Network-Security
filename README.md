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
│   └── main.yml                # CI/CD workflow (GitHub Actions)
├── Network_Data/
│   └── phisingData.csv         # Raw phishing dataset
├── networksecurity/
│   ├── components/             # Core pipeline components
│   │   └── data_ingestion.py
│   ├── constant/               # Project-wide constants
│   │   └── training_pipeline/
│   ├── entity/                 # Configuration entities
│   │   └── config_entity.py
│   ├── exception/              # Custom exception handling
│   │   └── exception.py
│   ├── logging/                # Centralized logging system
│   │   └── logger.py
│   └── __init__.py
├── app.py                      # Application entry point
├── Dockerfile                  # Docker container configuration
├── push_data.py                # Script to push data into MongoDB
├── test_mongodb.py             # MongoDB connection testing
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup configuration
├── .gitignore
└── README.md
