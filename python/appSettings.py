""" Populate ENV variables from .env file """
import os
from dotenv import load_dotenv

load_dotenv()

# get the cuurent directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# get the API key from the .env file
apiKey = os.getenv("ARCAPI")
