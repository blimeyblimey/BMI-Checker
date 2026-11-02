import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "prod-health-checker-secure-secret-key")
    DEBUG = False
    TESTING = False