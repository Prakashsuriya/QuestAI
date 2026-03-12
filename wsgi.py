import sys
import os

# Add project directory to path
path = '/home/Prakashsuriya/QuestAI'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['SECRET_KEY'] = 'your-secret-key-here'
os.environ['DATABASE_URL'] = 'sqlite:///questionnaire_app.db'
os.environ['FLASK_ENV'] = 'production'
os.environ['PYTHONPATH'] = path

# Import the Flask app
from run import app as application
