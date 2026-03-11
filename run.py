"""
QuestAI - Structured Questionnaire Answering Tool
Main entry point for the Flask application.
"""

from app import create_app, db
from app.models import User
import os

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User
    }

if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=True
    )
