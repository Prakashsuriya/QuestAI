import re
from typing import List, Dict, Any
import PyPDF2
from docx import Document
import pandas as pd
import openpyxl

class DocumentParser:
    """Parser for various document formats."""
    
    def parse(self, file_path: str, file_type: str) -> str:
        """Parse a document and return its text content."""
        if file_type.lower() == 'pdf':
            return self._parse_pdf(file_path)
        elif file_type.lower() in ['docx', 'doc']:
            return self._parse_docx(file_path)
        elif file_type.lower() in ['txt', 'md']:
            return self._parse_text(file_path)
        elif file_type.lower() in ['xlsx', 'xls']:
            return self._parse_excel(file_path)
        elif file_type.lower() == 'csv':
            return self._parse_csv(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _parse_pdf(self, file_path: str) -> str:
        """Parse PDF file."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _parse_docx(self, file_path: str) -> str:
        """Parse DOCX file."""
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    
    def _parse_text(self, file_path: str) -> str:
        """Parse text file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()
    
    def _parse_excel(self, file_path: str) -> str:
        """Parse Excel file and convert to text."""
        df = pd.read_excel(file_path)
        return df.to_string(index=False)
    
    def _parse_csv(self, file_path: str) -> str:
        """Parse CSV file and convert to text."""
        df = pd.read_csv(file_path)
        return df.to_string(index=False)
    
    def create_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better retrieval."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at a sentence or paragraph boundary
            if end < len(text):
                # Look for sentence ending
                for delimiter in ['.\n', '. ', '\n\n', '\n']:
                    last_delim = chunk.rfind(delimiter)
                    if last_delim > chunk_size * 0.5:  # Only break if we have substantial content
                        chunk = chunk[:last_delim + len(delimiter)]
                        end = start + len(chunk)
                        break
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def parse_questionnaire(self, file_path: str, file_type: str) -> List[Dict[str, Any]]:
        """Parse a questionnaire and extract questions."""
        if file_type.lower() in ['xlsx', 'xls']:
            return self._parse_excel_questionnaire(file_path)
        elif file_type.lower() == 'csv':
            return self._parse_csv_questionnaire(file_path)
        else:
            return self._parse_text_questionnaire(file_path)
    
    def _parse_excel_questionnaire(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse Excel questionnaire format."""
        df = pd.read_excel(file_path)
        questions = []
        
        # Expected columns: Question Number, Question, Category (optional)
        for _, row in df.iterrows():
            question_text = str(row.get('Question', row.get('Question Text', ''))).strip()
            if question_text and question_text.lower() not in ['nan', 'none', '']:
                questions.append({
                    'text': question_text,
                    'category': str(row.get('Category', 'General')).strip()
                })
        
        return questions
    
    def _parse_csv_questionnaire(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse CSV questionnaire format."""
        df = pd.read_csv(file_path)
        questions = []
        
        # Expected columns: Question Number, Question, Category (optional)
        for _, row in df.iterrows():
            question_text = str(row.get('Question', row.get('Question Text', ''))).strip()
            if question_text and question_text.lower() not in ['nan', 'none', '']:
                questions.append({
                    'text': question_text,
                    'category': str(row.get('Category', 'General')).strip()
                })
        
        return questions
    
    def _parse_text_questionnaire(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse text-based questionnaire."""
        text = self.parse(file_path, file_path.rsplit('.', 1)[1])
        questions = []
        
        # Try to identify questions by patterns
        lines = text.split('\n')
        current_category = 'General'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a category header (all caps or ends with colon)
            if line.isupper() or (line.endswith(':') and len(line) < 100):
                current_category = line.rstrip(':')
                continue
            
            # Check if it's a question (starts with number, Q, or ends with ?)
            is_question = (
                re.match(r'^\d+[.\)]\s+', line) or  # Numbered
                re.match(r'^Q\d*[.:\s]', line, re.IGNORECASE) or  # Q-based
                line.endswith('?') or  # Question mark
                re.match(r'^(what|how|when|where|why|who|is|are|does|do|can|will)', line, re.IGNORECASE)  # Question words
            )
            
            if is_question and len(line) > 10:
                questions.append({
                    'text': re.sub(r'^\d+[.\)]\s*', '', line).strip(),
                    'category': current_category
                })
        
        return questions
