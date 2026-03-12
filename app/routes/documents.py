from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
from app import db
from app.models import ReferenceDocument, DocumentChunk
from app.services.document_parser import DocumentParser

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@documents_bp.route('/')
@login_required
def list_documents():
    documents = ReferenceDocument.query.filter_by(user_id=current_user.id).order_by(ReferenceDocument.upload_date.desc()).all()
    return render_template('documents/list.html', documents=documents)

@documents_bp.route('/upload', methods=['POST'])
@login_required
def upload_document():
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('main.dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Allowed: PDF, DOCX, TXT, MD', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Parse document content
        parser = DocumentParser()
        content = parser.parse(file_path, file_ext)
        
        # Create database record
        doc = ReferenceDocument(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_type=file_ext,
            content=content,
            user_id=current_user.id
        )
        db.session.add(doc)
        db.session.commit()
        
        # Create chunks for reference (no vector store on Render free tier)
        chunks = parser.create_chunks(content)
        
        for i, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=doc.id,
                chunk_text=chunk_text,
                chunk_index=i
            )
            db.session.add(chunk)
        
        db.session.commit()
        
        flash(f'Document "{original_filename}" uploaded and processed successfully!', 'success')
        
    except Exception as e:
        flash(f'Error processing document: {str(e)}', 'error')
        # Clean up file if it was saved
        if os.path.exists(file_path):
            os.remove(file_path)
    
    return redirect(url_for('main.dashboard'))

@documents_bp.route('/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_document(doc_id):
    doc = ReferenceDocument.query.get_or_404(doc_id)
    
    # Verify ownership
    if doc.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('documents.list_documents'))
    
    try:
        # Remove file
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
        
        # Remove from database (chunks cascade delete)
        db.session.delete(doc)
        db.session.commit()
        
        flash(f'Document "{doc.original_filename}" deleted.', 'success')
        
    except Exception as e:
        flash(f'Error deleting document: {str(e)}', 'error')
    
    return redirect(url_for('main.dashboard'))

@documents_bp.route('/<int:doc_id>/view')
@login_required
def view_document(doc_id):
    doc = ReferenceDocument.query.get_or_404(doc_id)
    
    # Verify ownership
    if doc.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('documents.list_documents'))
    
    return render_template('documents/view.html', document=doc)
