Act as a Senior Python Software Architect, Machine Learning Engineer, and Flask Developer.

I want to build a **Spam Email Detection System** step by step for learning purposes.

### Project Overview

Develop a web application that classifies emails as **Spam** or **Not Spam (Ham)** using Machine Learning algorithms such as:

* Naive Bayes (Primary Model)
* Logistic Regression (Optional Comparison Model)

### Technology Stack

* Language: Python 3.x
* Framework: Flask
* Database: SQLite
* ML Libraries: Scikit-learn, Pandas, NumPy
* Frontend: HTML, CSS, Bootstrap
* ORM: SQLAlchemy
* API: Use free APIs only if required (Gemini Free API preferred)

### Architecture Requirements

Use a clean and scalable architecture:

```text
2-spam-email-detector/
│
├── app.py
├── config.py
├── requirements.txt
│
├── database/
│   └── spam_detector.db
│
├── models/
│   ├── email_model.py
│   └── prediction_model.py
│
├── services/
│   ├── dataset_service.py
│   ├── training_service.py
│   └── prediction_service.py
│
├── ml/
│   ├── train_model.py
│   ├── predictor.py
│   └── saved_model.pkl
│
├── routes/
│   ├── home_routes.py
│   └── prediction_routes.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   └── history.html
│
├── static/
│   ├── css/
│   └── js/
│
└── dataset/
    └── spam.csv
```

### Features

1. Train spam detection model.
2. Classify email text as Spam or Ham.
3. Store prediction history in SQLite.
4. View prediction history.
5. Display confidence score.
6. Model accuracy report.
7. Compare Naive Bayes vs Logistic Regression.
8. Responsive UI.

### Development Rules

* Build the application step by step.
* Generate complete code for each step.
* Explain every file before creating it.
* Follow MVC pattern.
* Use SQLAlchemy ORM.
* Add proper validation and error handling.
* Use environment variables where required.
* Keep code production-ready and beginner-friendly.

### Dataset

Use a public spam email dataset (SMS Spam Collection Dataset or equivalent free dataset).

### Development Phases

#### Phase 1

* Project setup
* Folder structure
* Virtual environment
* Dependency installation

#### Phase 2

* SQLite configuration
* Database models

#### Phase 3

* Dataset loading
* Data preprocessing
* Text cleaning

#### Phase 4

* Model training
* Naive Bayes implementation
* Accuracy evaluation
* Save trained model

#### Phase 5

* Flask routes
* Prediction APIs

#### Phase 6

* Frontend UI
* Prediction form
* History page

#### Phase 7

* Testing
* Optimization
* Deployment preparation

### Output Format

For every phase provide:

1. Objective
2. Architecture explanation
3. Folder/File creation
4. Complete code
5. Commands to run
6. Expected output
7. Common errors and fixes

### Important Instructions

* Use minimum tokens while explaining.
* Focus on code and implementation.
* Do not skip any step.
* Wait for my approval before moving to the next phase.
* Start with Phase 1 only.
* User folder ai_projects_30\2-spam-email-detector as project folder
