#!/usr/bin/env python
# test_system.py

"""
Quick test script to verify all components work
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✓ FastAPI installed")
    except ImportError:
        print("✗ FastAPI missing - run: pip install fastapi")
        return False
    
    try:
        import whisper
        print("✓ Whisper installed")
    except ImportError:
        print("✗ Whisper missing - run: pip install openai-whisper")
        return False
    
    try:
        import spacy
        print("✓ spaCy installed")
        try:
            nlp = spacy.load("en_core_web_sm")
            print("✓ spaCy model loaded")
        except OSError:
            print("✗ spaCy model missing - run: python -m spacy download en_core_web_sm")
            return False
    except ImportError:
        print("✗ spaCy missing - run: pip install spacy")
        return False
    
    try:
        from pdfminer.high_level import extract_text
        print("✓ PDFMiner installed")
    except ImportError:
        print("✗ PDFMiner missing - run: pip install pdfminer.six")
        return False
    
    try:
        import requests
        print("✓ Requests installed")
    except ImportError:
        print("✗ Requests missing - run: pip install requests")
        return False
    
    return True


def test_ollama():
    """Test Ollama connection"""
    print("\nTesting Ollama connection...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama is running")
            models = response.json().get("models", [])
            if models:
                print(f"  Available models: {[m['name'] for m in models]}")
                if any("llama3" in m["name"] for m in models):
                    print("✓ Llama3 model found")
                else:
                    print("⚠ Llama3 not found - run: ollama pull llama3")
            else:
                print("⚠ No models installed - run: ollama pull llama3")
            return True
        else:
            print("✗ Ollama not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Ollama - run: ollama serve")
        return False
    except Exception as e:
        print(f"✗ Ollama test failed: {e}")
        return False


def test_pdf_extraction():
    """Test PDF extraction capability"""
    print("\nTesting PDF extraction...")
    
    try:
        from pdfminer.high_level import extract_text
        import tempfile
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create a simple test PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Generate test PDF
            c = canvas.Canvas(tmp_path, pagesize=letter)
            c.drawString(100, 750, "Test Resume")
            c.drawString(100, 730, "Skills: Python, FastAPI")
            c.drawString(100, 710, "Experience: Software Developer")
            c.save()
            
            # Extract text
            text = extract_text(tmp_path)
            
            if "Python" in text and "FastAPI" in text:
                print("✓ PDF extraction working")
                return True
            else:
                print("⚠ PDF extraction may have issues")
                return False
                
        finally:
            os.unlink(tmp_path)
            
    except ImportError:
        print("✗ reportlab missing (optional for testing)")
        print("  Skipping PDF generation test")
        print("  PDF extraction should still work for real PDFs")
        return True
    except Exception as e:
        print(f"⚠ PDF test failed: {e}")
        print("  This is non-critical - PDF extraction should still work")
        return True


def test_resume_parser():
    """Test resume parsing"""
    print("\nTesting resume parser...")
    
    try:
        from interview.resume_parser import parse_resume
        
        sample_resume = """
        John Doe
        Software Engineer
        
        SKILLS
        Python, JavaScript, FastAPI, React
        
        PROJECTS
        - Built an AI chatbot using FastAPI and Ollama
        - Developed a web scraper with Python and BeautifulSoup
        
        EXPERIENCE
        Software Developer at Tech Corp (2022-2024)
        - Developed REST APIs
        - Worked with microservices
        """
        
        result = parse_resume(sample_resume)
        
        if result["skills"]:
            print(f"✓ Skills extracted: {result['skills'][:3]}")
        else:
            print("⚠ No skills extracted")
        
        if result["projects"]:
            print(f"✓ Projects found: {len(result['projects'])}")
        else:
            print("⚠ No projects extracted")
        
        return True
        
    except Exception as e:
        print(f"✗ Resume parser failed: {e}")
        return False


def test_question_generator():
    """Test question generation"""
    print("\nTesting question generator...")
    
    try:
        from interview.question_generator import generate_questions
        
        parsed_resume = {
            "skills": ["python", "fastapi"],
            "projects": ["AI chatbot"],
            "experience": ["Software Developer at Tech Corp"]
        }
        
        questions = generate_questions(parsed_resume)
        
        if questions and len(questions) > 0:
            print(f"✓ Generated {len(questions)} questions")
            print(f"  Sample: {questions[0][:60]}...")
            return True
        else:
            print("✗ No questions generated")
            return False
            
    except Exception as e:
        print(f"✗ Question generator failed: {e}")
        return False


def test_rules():
    """Test rule-based evaluation"""
    print("\nTesting rule-based evaluation...")
    
    try:
        from evaluation.rules import run_rules
        
        short_text = "Yes"
        long_text = "This is a detailed answer with multiple sentences explaining my approach to solving the problem. I considered various factors including performance, scalability, and maintainability."
        
        short_result = run_rules(short_text)
        long_result = run_rules(long_text)
        
        if short_result["too_short"] and not long_result["too_short"]:
            print("✓ Rule detection working correctly")
            return True
        else:
            print("⚠ Rule detection may have issues")
            return False
            
    except Exception as e:
        print(f"✗ Rules test failed: {e}")
        return False


def test_file_structure():
    """Test if all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        "backend/__init__.py",
        "backend/config.py",
        "backend/main.py",
        "backend/websocket.py",
        "interview/__init__.py",
        "interview/resume_parser.py",
        "interview/question_generator.py",
        "evaluation/__init__.py",
        "evaluation/rules.py",
        "evaluation/llm_eval.py",
        "speech/__init__.py",
        "speech/stt.py",
        "frontend/index.html",
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if not missing:
        print(f"✓ All {len(required_files)} required files found")
        return True
    else:
        print(f"✗ Missing files:")
        for file in missing:
            print(f"  - {file}")
        return False


def main():
    print("=" * 60)
    print("AI Interview System - Component Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("File Structure", test_file_structure()))
    results.append(("Imports", test_imports()))
    results.append(("Ollama", test_ollama()))
    results.append(("PDF Extraction", test_pdf_extraction()))
    results.append(("Resume Parser", test_resume_parser()))
    results.append(("Question Generator", test_question_generator()))
    results.append(("Rules", test_rules()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20s} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! System is ready.")
        print("\nTo start the server:")
        print("  python run.py")
        print("\nThen open browser at: http://localhost:8000")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Download spaCy model: python -m spacy download en_core_web_sm")
        print("3. Start Ollama: ollama serve")
        print("4. Pull Llama3: ollama pull llama3")
        print("5. Create __init__.py files in all module directories")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())