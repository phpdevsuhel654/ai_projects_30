class Config:
    SECRET_KEY = "dev-secret-key"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///database/spam_detector.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
