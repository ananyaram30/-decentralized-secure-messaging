import os
from datetime import timedelta

class Config:
    # Secret key for session management
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {'sslmode': 'require'},
    }
    
    # JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt_secret_key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # IPFS configuration
    IPFS_API_URL = os.getenv('IPFS_API_URL', 'https://ipfs.infura.io:5001/api/v0')
    IPFS_PROJECT_ID = os.getenv('IPFS_PROJECT_ID', '')
    IPFS_PROJECT_SECRET = os.getenv('IPFS_PROJECT_SECRET', '')
    
    # Web3 configuration
    WEB3_PROVIDER_URI = os.getenv('WEB3_PROVIDER_URI', 'https://mainnet.infura.io/v3/your-infura-project-id')
    
    # PostgreSQL configuration
    POSTGRES_USER = os.getenv('PGUSER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('PGPASSWORD', 'postgres')
    POSTGRES_HOST = os.getenv('PGHOST', 'localhost')
    POSTGRES_PORT = os.getenv('PGPORT', '5432')
    POSTGRES_DB = os.getenv('PGDATABASE', 'decsecmsg')
