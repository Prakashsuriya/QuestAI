# QuestAI - Structured Questionnaire Answering Tool

An AI-powered application that automates the process of answering structured questionnaires (security reviews, vendor assessments, compliance forms) using reference documents with proper citations and confidence scoring.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📹 Demo Video

[Watch Demo Video](https://your-demo-video-link-here)

**Live Application:** [http://localhost:5000](http://localhost:5000) (Local Development)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Screenshots](#screenshots)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Industry Context](#industry-context)
- [Technical Details](#technical-details)
- [Assumptions & Trade-offs](#assumptions--trade-offs)
- [Future Improvements](#future-improvements)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## 🎯 Overview

QuestAI solves the problem of manually answering repetitive structured questionnaires (like security assessments, vendor reviews, and compliance forms) by:

1. **Uploading reference documents** that contain your company's policies and procedures
2. **Uploading questionnaires** that need to be completed
3. **Automatically generating answers** using AI with proper citations
4. **Reviewing and exporting** the completed questionnaire

### Core Workflow:
```
Reference Documents → AI Processing → Generated Answers → Review → Export
```

---

## ✨ Key Features

### ✅ Required Features (Assignment)

| Feature | Status | Description |
|---------|--------|-------------|
| User Authentication | ✅ | Secure registration/login with bcrypt hashing |
| Document Upload | ✅ | Support for PDF, DOCX, TXT, MD, XLSX, CSV formats |
| Persistent Storage | ✅ | SQLite database with SQLAlchemy ORM |
| Questionnaire Parsing | ✅ | Automatic extraction of questions from documents |
| AI Answer Generation | ✅ | RAG pipeline with semantic search |
| Citations | ✅ | Every answer includes source document references |
| Review & Edit | ✅ | Inline editing of generated answers |
| Export | ✅ | Word (.docx), Excel (.xlsx), PDF formats |

### 🌟 Nice-to-Have Features (Bonus)

| Feature | Status | Description |
|---------|--------|-------------|
| Confidence Score | ✅ | 0-100% score based on retrieval quality |
| Evidence Snippets | ✅ | Shows relevant text excerpts from sources |
| Partial Regeneration | ✅ | Regenerate answers for individual questions |
| Version History | ✅ | Automatic versioning of answer sets |
| Coverage Summary | ✅ | Dashboard showing answered/not found stats |

---

## 📸 Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)
*Main dashboard showing questionnaires and reference documents*

### Questionnaire View
![Questionnaire](docs/screenshots/questionnaire.png)
*Questionnaire with generated answers, confidence scores, and citations*

### Answer Review
![Answer Review](docs/screenshots/answer_review.png)
*Review and edit generated answers with evidence snippets*

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Browser                        │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP
┌───────────────────────▼─────────────────────────────────────┐
│                    Flask Application                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Auth       │  │  Document    │  │ Questionnaire│       │
│  │   Routes     │  │   Routes     │  │   Routes     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │    RAG       │  │   Export     │  │   Vector     │       │
│  │   Engine     │  │   Service    │  │    Store     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌─────────────┐ ┌──────────────┐
│   SQLite     │ │  ChromaDB   │ │   OpenAI     │
│  Database    │ │ Vector DB   │ │    API       │
│              │ │             │ │  (Optional)  │
└──────────────┘ └─────────────┘ └──────────────┘
```

### RAG Pipeline Flow

```
1. User uploads reference documents
   ↓
2. Documents parsed and chunked (1000 chars + 200 overlap)
   ↓
3. Chunks embedded using all-MiniLM-L6-v2 model
   ↓
4. Embeddings stored in ChromaDB with metadata
   ↓
5. User uploads questionnaire
   ↓
6. Questions extracted and stored in SQLite
   ↓
7. For each question:
   a. Semantic search retrieves top 5 relevant chunks
   b. Confidence calculated (cosine similarity + keyword matching)
   c. Answer generated using LLM or fallback extraction
   d. Citations and evidence snippets extracted
   ↓
8. Answers displayed for review with confidence scores
   ↓
9. User can edit or regenerate individual answers
   ↓
10. Export final document with preserved structure
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Git (optional)

### Run in 5 Minutes

```bash
# 1. Clone/download the project
cd questionnaire-answering-tool

# 2. Create virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install flask flask-sqlalchemy flask-login werkzeug bcrypt python-dotenv pypdf2 python-docx pandas openpyxl reportlab chromadb

# 4. Set environment
copy .env.example .env

# 5. Run the application
python run.py

# 6. Open browser
# http://localhost:5000
```

---

## 📦 Installation

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd questionnaire-answering-tool
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

Activate it:
```bash
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Note:** If you encounter issues with ChromaDB, install dependencies individually:
```bash
pip install flask flask-sqlalchemy flask-login werkzeug bcrypt python-dotenv
pip install pypdf2 python-docx pandas openpyxl reportlab
pip install chromadb
```

### Step 4: Environment Configuration
Create `.env` file:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///questionnaire_app.db
OPENAI_API_KEY=your-openai-api-key-here  # Optional but recommended
FLASK_ENV=development
```

### Step 5: Create Sample Data (Optional)
```bash
python create_sample_data.py
```

### Step 6: Run Application
```bash
python run.py
```

Access at: http://localhost:5000

---

## 📖 Usage Guide

### Getting Started

1. **Register an Account**
   - Visit `/auth/register`
   - Enter email and password (min 8 characters)

2. **Upload Reference Documents**
   - Go to Dashboard
   - Click "Upload Reference Document"
   - Select files from `sample_data/reference_docs/`:
     - `security_policy.md`
     - `infrastructure.md`
     - `compliance_certifications.md`
     - `code_of_conduct.md`
     - `privacy_policy.md`

3. **Upload Questionnaire**
   - Click "Upload Questionnaire"
   - Select a file:
     - `sample_data/questionnaire.xlsx` (original - 15 questions)
     - `sample_data/questionnaire_cybersecurity.xlsx` (12 questions)
     - `sample_data/questionnaire_vendor_risk.xlsx` (10 questions)
     - `sample_data/questionnaire_privacy.xlsx` (10 questions)

4. **Generate Answers**
   - Open the questionnaire
   - Click "Generate Answers"
   - AI analyzes documents and generates responses with citations

5. **Review and Edit**
   - Review confidence scores (0-100%)
   - View evidence snippets from source documents
   - Click "Edit Answer" to modify any response
   - Click "Regenerate" to retry a specific question

6. **Export Results**
   - Click "Export" button
   - Choose format: Word (.docx), Excel (.xlsx), or PDF
   - Download completed questionnaire with citations

---

## 🔌 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/auth/register` | User registration |
| GET/POST | `/auth/login` | User login |
| GET | `/auth/logout` | User logout |

### Document Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/documents/` | List all reference documents |
| POST | `/documents/upload` | Upload new reference document |
| GET | `/documents/<id>/view` | View document content |
| POST | `/documents/<id>/delete` | Delete document |

### Questionnaire Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/questionnaires/upload` | Upload questionnaire |
| GET | `/questionnaires/<id>` | View questionnaire with answers |
| POST | `/questionnaires/<id>/generate` | Generate all answers |
| POST | `/questionnaires/<id>/edit-answer/<qid>` | Edit specific answer |
| POST | `/questionnaires/<id>/regenerate-question/<qid>` | Regenerate specific answer |
| GET | `/questionnaires/<id>/export` | Export questionnaire |
| GET | `/questionnaires/<id>/versions` | View version history |

### Export Formats
```
GET /questionnaires/<id>/export?format=docx  # Word document
GET /questionnaires/<id>/export?format=xlsx  # Excel spreadsheet
GET /questionnaires/<id>/export?format=pdf   # PDF document
```

---

## 📁 Project Structure

```
questionnaire-answering-tool/
│
├── app/                                    # Main application
│   ├── __init__.py                         # Flask app factory
│   ├── models.py                           # Database models
│   │
│   ├── routes/                             # Blueprint routes
│   │   ├── __init__.py
│   │   ├── auth.py                         # Authentication
│   │   ├── main.py                         # Dashboard
│   │   ├── documents.py                    # Document management
│   │   └── questionnaire.py                # Questionnaire processing
│   │
│   ├── services/                           # Business logic
│   │   ├── __init__.py
│   │   ├── document_parser.py              # PDF, DOCX, XLSX parsing
│   │   ├── vector_store.py                 # ChromaDB integration
│   │   ├── rag_engine.py                   # RAG pipeline
│   │   └── export_service.py               # Export generation
│   │
│   ├── templates/                          # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── auth/
│   │   ├── documents/
│   │   └── questionnaire/
│   │
│   └── static/                             # Static assets
│       ├── css/style.css
│       └── js/main.js
│
├── documents/                              # Uploaded files storage
├── chroma_db/                              # Vector database storage
│
├── sample_data/                            # Sample documents
│   ├── company_info.md
│   ├── questionnaire.xlsx
│   ├── questionnaire_cybersecurity.xlsx
│   ├── questionnaire_vendor_risk.xlsx
│   ├── questionnaire_privacy.xlsx
│   └── reference_docs/
│       ├── security_policy.md
│       ├── infrastructure.md
│       ├── compliance_certifications.md
│       ├── code_of_conduct.md
│       └── privacy_policy.md
│
├── tests/                                  # Unit tests
│
├── .env.example                            # Environment template
├── .gitignore                              # Git ignore rules
├── create_sample_data.py                   # Sample data generator
├── requirements.txt                        # Python dependencies
├── run.py                                  # Application entry point
└── README.md                               # This file
```

---

## 🏢 Industry Context

### Fictional Company: CloudSecure Solutions

**Industry:** SaaS / Cloud Security

**Company Description:**
CloudSecure Solutions is a B2B SaaS company providing cloud infrastructure security and compliance monitoring tools for mid-market enterprises. Founded in 2020, the company helps organizations automate their security posture management across AWS, Azure, and Google Cloud Platform through their flagship product, GuardianCloud.

**Key Statistics:**
- **Founded:** 2020
- **Employees:** 150
- **Customers:** 500+
- **Annual Revenue:** $25M
- **Certifications:** SOC 2 Type II, ISO 27001, GDPR compliant
- **Deployment:** Multi-region (US, EU, APAC)

### Sample Documents

The project includes 5 comprehensive reference documents:

1. **Security Policy** (`security_policy.md`)
   - Information security management
   - Access control policies
   - Data protection procedures
   - Incident response plan
   - Business continuity

2. **Infrastructure Documentation** (`infrastructure.md`)
   - AWS architecture details
   - Security controls
   - Data management procedures
   - Third-party services

3. **Compliance Certifications** (`compliance_certifications.md`)
   - SOC 2 Type II details
   - ISO 27001:2022 certification
   - GDPR compliance
   - HIPAA and PCI DSS information
   - FedRAMP and StateRAMP status

4. **Code of Conduct** (`code_of_conduct.md`)
   - Employee ethical standards
   - Security responsibilities
   - Compliance requirements

5. **Privacy Policy** (`privacy_policy.md`)
   - Data collection practices
   - Processing and sharing policies
   - Individual rights
   - Data security measures

### Sample Questionnaires

Four different questionnaires for testing:

1. **General Security Assessment** (`questionnaire.xlsx`) - 15 questions
2. **Cybersecurity Assessment** (`questionnaire_cybersecurity.xlsx`) - 12 questions
3. **Vendor Risk Assessment** (`questionnaire_vendor_risk.xlsx`) - 10 questions
4. **Data Privacy Assessment** (`questionnaire_privacy.xlsx`) - 10 questions

---

## 🔧 Technical Details

### Technology Stack

**Backend:**
- Python 3.9+
- Flask 3.0+ (Web Framework)
- SQLAlchemy 2.0+ (ORM)
- Flask-Login (Authentication)
- SQLite (Database)

**AI/ML:**
- ChromaDB (Vector Database)
- all-MiniLM-L6-v2 (Embedding Model)
- OpenAI GPT-3.5-turbo (Optional LLM)
- LangChain (RAG Framework)

**Document Processing:**
- PyPDF2 (PDF parsing)
- python-docx (Word documents)
- pandas + openpyxl (Excel files)
- reportlab (PDF generation)

**Frontend:**
- Jinja2 Templates
- Vanilla CSS (custom design)
- Vanilla JavaScript
- Font Awesome Icons

### Confidence Scoring Algorithm

```python
Confidence Score = (Semantic_Similarity × 0.5) + (Keyword_Matching × 0.5)

Where:
- Semantic_Similarity: Cosine similarity from vector search (0-1)
- Keyword_Matching: Percentage of question keywords found in documents (0-1)
```

### Data Flow

1. **Document Upload:**
   - File saved to `documents/` folder
   - Text extracted based on file type
   - Content chunked (1000 chars + 200 overlap)
   - Chunks embedded and stored in ChromaDB

2. **Questionnaire Processing:**
   - Questions extracted from uploaded file
   - Stored in SQLite with metadata
   - Status tracked (uploaded → processing → completed)

3. **Answer Generation:**
   - Semantic search retrieves relevant chunks
   - Confidence calculated
   - Answer generated (LLM or keyword extraction)
   - Citations and evidence extracted
   - Results stored in database

---

## 🤔 Assumptions & Trade-offs

### Assumptions

1. **Document Formats:**
   - Reference documents are primarily text-based
   - Images in documents are not processed
   - Questionnaires follow standard formats

2. **Data Privacy:**
   - Single-tenant application
   - No sharing between users
   - Local file storage

3. **Usage Patterns:**
   - Small to medium questionnaires (10-100 questions)
   - Documents under 50MB each
   - Moderate concurrent users

4. **Infrastructure:**
   - SQLite sufficient for demo/small-scale
   - ChromaDB runs locally

### Trade-offs

| Decision | Pros | Cons | Rationale |
|----------|------|------|-----------|
| **ChromaDB (local)** | Easy setup, no external deps | Limited scalability | Demo/small-scale use |
| **SQLite** | Zero config, portable | Limited concurrency | Easy to upgrade via SQLAlchemy |
| **OpenAI API** | High quality answers | External dependency | Works with fallback |
| **Server-rendered templates** | Fast dev, no build step | Less interactive | Focus on backend |
| **Local file storage** | Simple, no cloud deps | No redundancy | MVP appropriate |

---

## 🚀 Future Improvements

### High Priority
- [ ] Multi-user organizations with role-based permissions
- [ ] OCR support for scanned PDFs
- [ ] Hybrid search (semantic + keyword)
- [ ] Local LLM option (Llama 3, Mistral)

### Medium Priority
- [ ] Comments and annotations on answers
- [ ] Approval workflows
- [ ] REST API for external integrations
- [ ] Slack/Teams notifications
- [ ] Two-factor authentication

### Nice-to-Have
- [ ] Mobile-responsive design improvements
- [ ] Custom export templates
- [ ] Automated compliance reporting
- [ ] White-label options

---

## 🐛 Troubleshooting

### Common Issues

**1. "ModuleNotFoundError: No module named 'flask'"**
```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Then install dependencies
pip install flask flask-sqlalchemy flask-login
```

**2. "Excel file format cannot be determined"**
- The Excel file was corrupted during creation
- Solution: Delete and recreate using `python create_sample_data.py`

**3. "Not found in references" for all answers**
- Reference documents not uploaded first
- Solution: Upload reference documents before generating answers
- Or: Re-upload documents if uploaded before the user_id fix

**4. Confidence scores are 0%**
- Fixed in latest version (cosine distance calculation)
- Solution: Pull latest code or update `rag_engine.py`

**5. ChromaDB installation fails**
```bash
# Install without ChromaDB first
pip install flask flask-sqlalchemy flask-login werkzeug bcrypt python-dotenv
pip install pypdf2 python-docx pandas openpyxl reportlab

# Then install ChromaDB separately
pip install chromadb
```

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👨‍💻 Author

**Built for:** Almabase GTM Engineering Internship Assignment

**Assignment Requirements Met:**
- ✅ User authentication with secure password hashing
- ✅ Persistent data storage (SQLite database)
- ✅ Clear user flow from upload to export
- ✅ AI doing meaningful work (RAG pipeline)
- ✅ Outputs grounded in reference data with citations
- ✅ Confidence scores and evidence snippets (nice-to-have)
- ✅ Version history (nice-to-have)
- ✅ Coverage summary (nice-to-have)
- ✅ Partial regeneration (nice-to-have)

---

## 🙏 Acknowledgments

- Flask team for the excellent web framework
- ChromaDB team for the vector database
- OpenAI for the GPT API
- Almabase for the assignment opportunity

---

**Questions or Issues?** Please open an issue in the repository or contact the maintainer.

**Happy Questionnaire Answering! 🤖✨**
