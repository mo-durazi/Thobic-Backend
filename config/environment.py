import os
from pathlib import Path
from dotenv import load_dotenv

# Find the root directory and point directly to the .env file
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv('DATABASE_URL')
JWT_SECRET = os.getenv('JWT_SECRET')