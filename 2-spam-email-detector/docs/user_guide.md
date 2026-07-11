# User Guide

## Home Page
Open the home page to access the main navigation for prediction and history.

## Predict an Email
1. Open /predict.
2. Paste an email message into the text area.
3. Click Classify.
4. The app will return a spam or ham prediction and a confidence score.

## View Prediction History
1. Open /history.
2. Review previous predictions saved in SQLite.

## Troubleshooting
- If the model is missing, run ml/train_model.py first.
- If the app cannot start, ensure dependencies are installed.
- If predictions fail, confirm the database file and model artifact exist.
