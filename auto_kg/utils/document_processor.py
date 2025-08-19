"""
Document processing utilities for handling uploaded files.
"""

import os
import tempfile
from typing import Dict, Optional
import mimetypes


class DocumentProcessor:
    """Process uploaded documents and extract text content."""
    
    def __init__(self):
        """Initialize the document processor."""
        self.supported_types = {
            'text/plain': self._process_txt,
            'application/pdf': self._process_pdf,
            'application/msword': self._process_doc,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': self._process_docx
        }
    
    def is_supported(self, filename: str) -> bool:
        """Check if the file type is supported."""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type in self.supported_types
    
    def process_file(self, file_path: str, filename: str) -> Dict[str, str]:
        """
        Process a file and extract its text content.
        
        Args:
            file_path: Path to the uploaded file
            filename: Original filename
            
        Returns:
            Dictionary with extracted text and metadata
        """
        mime_type, _ = mimetypes.guess_type(filename)
        
        if mime_type not in self.supported_types:
            raise ValueError(f"Unsupported file type: {mime_type}")
        
        processor = self.supported_types[mime_type]
        text_content = processor(file_path)
        
        return {
            'title': os.path.splitext(filename)[0],
            'content': text_content,
            'filename': filename,
            'mime_type': mime_type
        }
    
    def _process_txt(self, file_path: str) -> str:
        """Process a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _process_pdf(self, file_path: str) -> str:
        """Process a PDF file."""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            return "PDF processing requires PyPDF2. Please install it with: pip install PyPDF2"
        except Exception as e:
            return f"Error processing PDF: {str(e)}"
    
    def _process_doc(self, file_path: str) -> str:
        """Process a DOC file."""
        try:
            import python_docx2txt
            return python_docx2txt.process(file_path)
        except ImportError:
            return "DOC processing requires python-docx2txt. Please install it with: pip install python-docx2txt"
        except Exception as e:
            return f"Error processing DOC: {str(e)}"
    
    def _process_docx(self, file_path: str) -> str:
        """Process a DOCX file."""
        try:
            from docx import Document
            doc = Document(file_path)
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            return '\n'.join(text)
        except ImportError:
            return "DOCX processing requires python-docx. Please install it with: pip install python-docx"
        except Exception as e:
            return f"Error processing DOCX: {str(e)}"


def create_knowledge_graph_from_document(document_data: Dict[str, str]) -> Dict:
    """
    Create a knowledge graph from processed document data.
    
    Args:
        document_data: Processed document with text content
        
    Returns:
        Dictionary with nodes and edges for the knowledge graph
    """
    from auto_kg.llm.concept_extractor import ConceptExtractor
    
    # Initialize concept extractor
    extractor = ConceptExtractor(model_type='rule_based')
    
    # Create a fake Wikipedia page format for the processor
    page_data = {
        'title': document_data['title'],
        'summary': document_data['content'][:500] + "..." if len(document_data['content']) > 500 else document_data['content'],
        'content': document_data['content'],
        'url': f"uploaded://{document_data['filename']}",
        'categories': ['User Upload'],
        'links': []
    }
    
    # Process the document
    result = extractor.process_wikipedia_page(page_data)
    
    # Convert to graph format
    nodes = []
    edges = []
    
    # Create main document node
    main_node = {
        'id': document_data['title'],
        'label': document_data['title'],
        'summary': page_data['summary'],
        'url': page_data['url'],
        'categories': ['Document', 'User Upload']
    }
    nodes.append(main_node)
    
    # Create concept nodes
    for concept in result.get('concepts', []):
        if concept.lower() != document_data['title'].lower():
            concept_node = {
                'id': concept,
                'label': concept,
                'summary': f"Concept from {document_data['filename']}",
                'url': page_data['url'],
                'categories': ['Concept', 'User Upload']
            }
            nodes.append(concept_node)
            
            # Create edge from document to concept
            edges.append({
                'source': document_data['title'],
                'target': concept,
                'relationship_type': 'CONTAINS_CONCEPT',
                'properties': {}
            })
    
    # Create relationship edges
    for rel in result.get('relationships', []):
        try:
            source, target, rel_type = rel
            if source != target:  # Avoid self-loops
                edges.append({
                    'source': str(source),
                    'target': str(target),
                    'relationship_type': str(rel_type).upper(),
                    'properties': {}
                })
        except ValueError:
            continue
    
    return {
        'nodes': nodes,
        'edges': edges,
        'metadata': {
            'document_title': document_data['title'],
            'filename': document_data['filename'],
            'concept_count': len(nodes),
            'relationship_count': len(edges)
        }
    }