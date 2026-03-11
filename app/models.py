from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    questionnaires = db.relationship('Questionnaire', backref='user', lazy=True)
    reference_documents = db.relationship('ReferenceDocument', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'

class ReferenceDocument(db.Model):
    __tablename__ = 'reference_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    chunks = db.relationship('DocumentChunk', backref='document', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ReferenceDocument {self.original_filename}>'

class DocumentChunk(db.Model):
    __tablename__ = 'document_chunks'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('reference_documents.id'), nullable=False)
    chunk_text = db.Column(db.Text, nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False)
    embedding_id = db.Column(db.String(100))  # Reference to vector DB
    
    def __repr__(self):
        return f'<DocumentChunk {self.id} from doc {self.document_id}>'

class Questionnaire(db.Model):
    __tablename__ = 'questionnaires'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='uploaded')  # uploaded, processing, completed
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    questions = db.relationship('Question', backref='questionnaire', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Questionnaire {self.original_filename}>'
    
    @property
    def total_questions(self):
        return len(self.questions)
    
    @property
    def answered_questions(self):
        return len([q for q in self.questions if q.answers])
    
    @property
    def not_found_count(self):
        return len([q for q in self.questions if q.answers and q.answers[0].answer_text == "Not found in references."])

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaires.id'), nullable=False)
    question_number = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))  # e.g., "Security", "Compliance", "Technical"
    
    # Relationships
    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Question {self.question_number}: {self.question_text[:50]}...>'

class Answer(db.Model):
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    confidence_score = db.Column(db.Float)  # 0.0 to 1.0
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime)
    is_edited = db.Column(db.Boolean, default=False)
    
    # Relationships
    citations = db.relationship('Citation', backref='answer', lazy=True, cascade='all, delete-orphan')
    evidence_snippets = db.relationship('EvidenceSnippet', backref='answer', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Answer for Question {self.question_id}>'

class Citation(db.Model):
    __tablename__ = 'citations'
    
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('reference_documents.id'), nullable=False)
    document = db.relationship('ReferenceDocument')
    page_number = db.Column(db.Integer)
    section = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Citation from {self.document.original_filename}>'

class EvidenceSnippet(db.Model):
    __tablename__ = 'evidence_snippets'
    
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('reference_documents.id'), nullable=False)
    document = db.relationship('ReferenceDocument')
    snippet_text = db.Column(db.Text, nullable=False)
    relevance_score = db.Column(db.Float)
    
    def __repr__(self):
        return f'<EvidenceSnippet from {self.document.original_filename}>'

class QuestionnaireVersion(db.Model):
    __tablename__ = 'questionnaire_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    questionnaire_id = db.Column(db.Integer, db.ForeignKey('questionnaires.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    answers_snapshot = db.Column(db.Text)  # JSON string of all answers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    questionnaire = db.relationship('Questionnaire', backref='versions')
    
    def __repr__(self):
        return f'<Version {self.version_number} of Questionnaire {self.questionnaire_id}>'
    
    def get_answers(self):
        return json.loads(self.answers_snapshot) if self.answers_snapshot else {}
