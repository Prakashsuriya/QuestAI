from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
import json
from datetime import datetime
from app import db
from app.models import (
    Questionnaire, Question, Answer, Citation, EvidenceSnippet,
    ReferenceDocument, QuestionnaireVersion
)
from app.services.document_parser import DocumentParser
from app.services.simple_rag_engine import SimpleRAGEngine
from app.services.export_service import ExportService

questionnaire_bp = Blueprint('questionnaire', __name__, url_prefix='/questionnaires')

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md', 'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@questionnaire_bp.route('/upload', methods=['POST'])
@login_required
def upload_questionnaire():
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('main.dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Allowed: PDF, DOCX, TXT, MD, XLSX, XLS', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Parse questionnaire to extract questions
        parser = DocumentParser()
        questions_data = parser.parse_questionnaire(file_path, file_ext)
        
        # Create questionnaire record
        questionnaire = Questionnaire(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_type=file_ext,
            status='uploaded',
            user_id=current_user.id
        )
        db.session.add(questionnaire)
        db.session.flush()
        
        # Create question records
        for i, q_data in enumerate(questions_data, 1):
            question = Question(
                questionnaire_id=questionnaire.id,
                question_number=i,
                question_text=q_data['text'],
                category=q_data.get('category', 'General')
            )
            db.session.add(question)
        
        db.session.commit()
        
        flash(f'Questionnaire "{original_filename}" uploaded with {len(questions_data)} questions!', 'success')
        return redirect(url_for('questionnaire.view', id=questionnaire.id))
        
    except Exception as e:
        flash(f'Error processing questionnaire: {str(e)}', 'error')
        if os.path.exists(file_path):
            os.remove(file_path)
        return redirect(url_for('main.dashboard'))

@questionnaire_bp.route('/<int:id>')
@login_required
def view(id):
    questionnaire = Questionnaire.query.get_or_404(id)
    
    # Verify ownership
    if questionnaire.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Load questions with answers
    questions = Question.query.filter_by(questionnaire_id=id).order_by(Question.question_number).all()
    
    # Calculate coverage stats
    total = len(questions)
    answered = len([q for q in questions if q.answers])
    with_citations = len([q for q in questions if q.answers and q.answers[0].citations])
    not_found = len([q for q in questions if q.answers and q.answers[0].answer_text == "Not found in references."])
    
    coverage_stats = {
        'total': total,
        'answered': answered,
        'with_citations': with_citations,
        'not_found': not_found,
        'coverage_pct': (answered / total * 100) if total > 0 else 0
    }
    
    return render_template('questionnaire/view.html', 
                         questionnaire=questionnaire, 
                         questions=questions,
                         coverage_stats=coverage_stats)

@questionnaire_bp.route('/<int:id>/generate', methods=['POST'])
@login_required
def generate_answers(id):
    questionnaire = Questionnaire.query.get_or_404(id)
    
    # Verify ownership
    if questionnaire.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Check if user has reference documents
        ref_docs = ReferenceDocument.query.filter_by(user_id=current_user.id).all()
        if not ref_docs:
            flash('Please upload reference documents first.', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Update status
        questionnaire.status = 'processing'
        db.session.commit()
        
        # Generate answers using RAG (lightweight version for Render)
        rag_engine = SimpleRAGEngine()
        
        questions = Question.query.filter_by(questionnaire_id=id).order_by(Question.question_number).all()
        
        for question in questions:
            # Delete existing answers
            Answer.query.filter_by(question_id=question.id).delete()
            
            # Generate new answer
            result = rag_engine.answer_question(question.question_text, current_user.id)
            
            # Create answer record
            answer = Answer(
                question_id=question.id,
                answer_text=result['answer'],
                confidence_score=result.get('confidence', 0.0)
            )
            db.session.add(answer)
            db.session.flush()
            
            # Add citations
            for citation_data in result.get('citations', []):
                doc = ReferenceDocument.query.filter_by(
                    user_id=current_user.id,
                    original_filename=citation_data['document_name']
                ).first()
                
                if doc:
                    citation = Citation(
                        answer_id=answer.id,
                        document_id=doc.id,
                        page_number=citation_data.get('page'),
                        section=citation_data.get('section')
                    )
                    db.session.add(citation)
            
            # Add evidence snippets
            for snippet_data in result.get('evidence_snippets', []):
                doc = ReferenceDocument.query.filter_by(
                    user_id=current_user.id,
                    original_filename=snippet_data['document_name']
                ).first()
                
                if doc:
                    snippet = EvidenceSnippet(
                        answer_id=answer.id,
                        document_id=doc.id,
                        snippet_text=snippet_data['text'],
                        relevance_score=snippet_data.get('relevance', 0.0)
                    )
                    db.session.add(snippet)
        
        # Update status
        questionnaire.status = 'completed'
        questionnaire.completed_date = datetime.utcnow()
        db.session.commit()
        
        # Save version
        save_version(questionnaire)
        
        flash('Answers generated successfully!', 'success')
        
    except Exception as e:
        questionnaire.status = 'uploaded'
        db.session.commit()
        flash(f'Error generating answers: {str(e)}', 'error')
    
    return redirect(url_for('questionnaire.view', id=id))

@questionnaire_bp.route('/<int:id>/edit-answer/<int:question_id>', methods=['POST'])
@login_required
def edit_answer(id, question_id):
    questionnaire = Questionnaire.query.get_or_404(id)
    
    if questionnaire.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    new_answer = request.form.get('answer', '').strip()
    
    if not new_answer:
        return jsonify({'error': 'Answer cannot be empty'}), 400
    
    try:
        question = Question.query.get_or_404(question_id)
        
        # Get or create answer
        if question.answers:
            answer = question.answers[0]
            answer.answer_text = new_answer
            answer.edited_at = datetime.utcnow()
            answer.is_edited = True
        else:
            answer = Answer(
                question_id=question_id,
                answer_text=new_answer,
                is_edited=True,
                edited_at=datetime.utcnow()
            )
            db.session.add(answer)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'answer': new_answer,
            'is_edited': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@questionnaire_bp.route('/<int:id>/regenerate-question/<int:question_id>', methods=['POST'])
@login_required
def regenerate_question(id, question_id):
    questionnaire = Questionnaire.query.get_or_404(id)
    
    if questionnaire.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        question = Question.query.get_or_404(question_id)
        
        # Delete existing answer
        Answer.query.filter_by(question_id=question_id).delete()
        db.session.commit()
        
        # Generate new answer
        rag_engine = RAGEngine()
        result = rag_engine.answer_question(question.question_text, current_user.id)
        
        # Create new answer
        answer = Answer(
            question_id=question_id,
            answer_text=result['answer'],
            confidence_score=result.get('confidence', 0.0)
        )
        db.session.add(answer)
        db.session.flush()
        
        # Add citations and snippets
        for citation_data in result.get('citations', []):
            doc = ReferenceDocument.query.filter_by(
                user_id=current_user.id,
                original_filename=citation_data['document_name']
            ).first()
            
            if doc:
                citation = Citation(
                    answer_id=answer.id,
                    document_id=doc.id,
                    page_number=citation_data.get('page'),
                    section=citation_data.get('section')
                )
                db.session.add(citation)
        
        for snippet_data in result.get('evidence_snippets', []):
            doc = ReferenceDocument.query.filter_by(
                user_id=current_user.id,
                original_filename=snippet_data['document_name']
            ).first()
            
            if doc:
                snippet = EvidenceSnippet(
                    answer_id=answer.id,
                    document_id=doc.id,
                    snippet_text=snippet_data['text'],
                    relevance_score=snippet_data.get('relevance', 0.0)
                )
                db.session.add(snippet)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'confidence': result.get('confidence', 0.0),
            'citations': result.get('citations', []),
            'evidence_snippets': result.get('evidence_snippets', [])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@questionnaire_bp.route('/<int:id>/export', methods=['GET'])
@login_required
def export_questionnaire(id):
    questionnaire = Questionnaire.query.get_or_404(id)
    
    if questionnaire.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    export_format = request.args.get('format', 'docx')
    
    try:
        export_service = ExportService()
        
        if export_format == 'docx':
            output_path = export_service.export_to_docx(questionnaire)
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            extension = 'docx'
        elif export_format == 'xlsx':
            output_path = export_service.export_to_excel(questionnaire)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            extension = 'xlsx'
        elif export_format == 'pdf':
            output_path = export_service.export_to_pdf(questionnaire)
            mimetype = 'application/pdf'
            extension = 'pdf'
        else:
            flash('Invalid export format.', 'error')
            return redirect(url_for('questionnaire.view', id=id))
        
        return send_file(
            output_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=f"{questionnaire.original_filename.rsplit('.', 1)[0]}_completed.{extension}"
        )
        
    except Exception as e:
        flash(f'Error exporting questionnaire: {str(e)}', 'error')
        return redirect(url_for('questionnaire.view', id=id))

@questionnaire_bp.route('/<int:id>/versions')
@login_required
def view_versions(id):
    questionnaire = Questionnaire.query.get_or_404(id)
    
    if questionnaire.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    versions = QuestionnaireVersion.query.filter_by(questionnaire_id=id).order_by(QuestionnaireVersion.version_number.desc()).all()
    
    return render_template('questionnaire/versions.html', questionnaire=questionnaire, versions=versions)

def save_version(questionnaire):
    """Save a snapshot of current answers as a version."""
    questions = Question.query.filter_by(questionnaire_id=questionnaire.id).all()
    
    answers_snapshot = {}
    for q in questions:
        if q.answers:
            answer = q.answers[0]
            answers_snapshot[q.question_number] = {
                'question': q.question_text,
                'answer': answer.answer_text,
                'confidence': answer.confidence_score,
                'edited': answer.is_edited
            }
    
    # Get next version number
    last_version = QuestionnaireVersion.query.filter_by(questionnaire_id=questionnaire.id).order_by(QuestionnaireVersion.version_number.desc()).first()
    version_number = (last_version.version_number + 1) if last_version else 1
    
    version = QuestionnaireVersion(
        questionnaire_id=questionnaire.id,
        version_number=version_number,
        answers_snapshot=json.dumps(answers_snapshot)
    )
    db.session.add(version)
    db.session.commit()
