from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Questionnaire, ReferenceDocument

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's questionnaires and documents
    questionnaires = Questionnaire.query.filter_by(user_id=current_user.id).order_by(Questionnaire.upload_date.desc()).all()
    documents = ReferenceDocument.query.filter_by(user_id=current_user.id).order_by(ReferenceDocument.upload_date.desc()).all()
    
    # Calculate statistics
    stats = {
        'total_questionnaires': len(questionnaires),
        'completed_questionnaires': len([q for q in questionnaires if q.status == 'completed']),
        'total_documents': len(documents),
        'recent_questionnaires': questionnaires[:5]
    }
    
    return render_template('dashboard.html', 
                         questionnaires=questionnaires, 
                         documents=documents,
                         stats=stats)
