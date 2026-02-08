"""
Setup script to help initialize the project.
This script checks prerequisites and guides through setup.
"""
import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_postgresql():
    """Check if PostgreSQL is available"""
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ PostgreSQL found: {result.stdout.strip()}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    print("⚠️  PostgreSQL not found in PATH (you may need to install it)")
    return False

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ Tesseract OCR found: {version_line}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    print("⚠️  Tesseract OCR not found (required for PDF OCR functionality)")
    print("   Install: https://github.com/tesseract-ocr/tesseract")
    return False

def check_env_file():
    """Check if .env file exists"""
    if os.path.exists('.env'):
        print("✅ .env file exists")
        return True
    else:
        print("⚠️  .env file not found")
        print("   Create .env file from .env.example and fill in your values")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def main():
    print("🚀 HR Automation Pipeline - Setup Check\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("PostgreSQL", check_postgresql),
        ("Tesseract OCR", check_tesseract),
        ("Environment File", check_env_file),
    ]
    
    results = []
    for name, check_func in checks:
        results.append(check_func())
    
    print("\n" + "="*50)
    
    if all(results):
        print("✅ All checks passed!")
    else:
        print("⚠️  Some checks failed. Please address the issues above.")
    
    print("\nNext steps:")
    print("1. Create .env file from .env.example")
    print("2. Run: python init_db.py (to initialize database)")
    print("3. Run: uvicorn app.main:app --reload (to start server)")

if __name__ == "__main__":
    main()
