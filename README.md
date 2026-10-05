# Machine Risk App

A local web app for configuring machine fields, managing machine records, and predicting machine risk. It returns Low, Medium, or High using a Python machine learning model. The project is built for the technical assessment and does not use cloud AI services.

GitHub repository: https://github.com/nandh1n1reddy/Machine_Risk_App

## Technologies

- Python 3.10 or later
- Streamlit for the web UI
- FastAPI and Uvicorn for the local backend API
- SQLite and SQLAlchemy for database storage
- scikit-learn, pandas, NumPy, and joblib for model training and prediction
- requests for calls from the Streamlit UI to the backend

All components run locally. The prediction model is loaded by the backend; it does not run as a separate web service.

## Features

- Configure text, number, and dropdown machine fields, including required status and dropdown options.
- Create, view, edit, and delete machine records through dynamically generated forms.
- Store machine-specific values as JSON so adding fields does not require a database schema change.
- Predict Low, Medium, or High risk for a selected machine.
- Report which machine fields the current model uses and which it ignores.

## Setup

From the project root in PowerShell, create a virtual environment, install dependencies, create the local SQLite database, and train the model:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m backend.setup_db
.\.venv\Scripts\python.exe -m ml.train_model
```

The database setup creates the `field_definitions` and `machines` tables and seeds Machine Name, Temperature, Pressure, and Vibration. The training command generates synthetic examples, trains the local classifier, and saves `ml/risk_model.joblib`. Run it before starting the backend if the model file is missing.

## Run the application

Start the backend in one PowerShell terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

Start the Streamlit UI in a second terminal, also from the project root:

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend/app.py
```

Open the app at `http://localhost:8501`. The API documentation is at `http://127.0.0.1:8000/docs`.

## Python machine learning component

Train or regenerate the local model from the project root with:

```powershell
.\.venv\Scripts\python.exe -m ml.train_model
```

This command creates synthetic training data in memory, trains a scikit-learn classifier, and saves `ml/risk_model.joblib`. The FastAPI backend uses `ml/predictor.py` to load that model for prediction. Start the backend using the command in Run the application; the model runs locally inside that backend process, so there is no separate ML server to start.

## Architecture

```text
Browser
  -> Streamlit UI (port 8501)
  -> FastAPI backend (port 8000)
       -> SQLite database (field definitions and machine records)
       -> Local Python/scikit-learn model (in-process prediction)
  <- Risk result displayed in Streamlit
```

The Streamlit UI sends HTTP requests to FastAPI. The backend reads and writes the database and calls the local Python model for predictions. No third ML service or external AI API is required.

## Dynamic fields and Humidity

Field definitions are stored in `field_definitions`. Machine values are stored in the JSON `machines.data` column using each field's key. The Fields page creates or updates field definitions; the Machines page builds its inputs and columns from those definitions. Adding an optional field such as Humidity therefore does not require a database schema change. Existing machine records can still be opened; the new optional field is blank until a value is entered.

The current model expects Temperature, Pressure, and Vibration. It does not use Humidity: the backend passes only the model's expected inputs and reports additional populated fields as ignored. To use Humidity in a future model, collect labeled examples that include Humidity and retrain the classifier. Automatic retraining is not part of this assessment.

## Submission and sensitive information

Push the complete source code, database setup script, model-training code, and this README to the GitHub repository above. Share the repository link with the assessment team and make sure they have access. Do not commit passwords, API keys, access tokens, `.env` files, or the local SQLite database. The generated model can be reproduced with `python -m ml.train_model`.


