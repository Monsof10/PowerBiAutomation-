"""
Setup Verification Script
Tests that all components are properly configured
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all required packages are installed"""
    print("Testing package imports...")
    packages = {
        'streamlit': 'streamlit',
        'playwright': 'playwright',
        'pypdf': 'pypdf',
        'yagmail': 'yagmail',
        'dotenv': 'python-dotenv',
        'pdf2image': 'pdf2image',
        'PIL': 'Pillow',
        'pandas': 'pandas'
    }
    
    missing = []
    for package, pip_name in packages.items():
        try:
            __import__(package)
            print(f"  ✅ {pip_name}")
        except ImportError:
            print(f"  ❌ {pip_name} (missing)")
            missing.append(pip_name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    print("✅ All packages installed\n")
    return True


def test_playwright():
    """Test Playwright installation"""
    print("Testing Playwright browser...")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        print("  ✅ Playwright chromium browser installed\n")
        return True
    except Exception as e:
        print(f"  ❌ Playwright browser not installed: {e}")
        print("Install with: playwright install chromium\n")
        return False


def test_config():
    """Test configuration file"""
    print("Testing configuration...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("  ❌ .env file not found")
        print("  Create it from env.example: cp env.example .env\n")
        return False
    
    print("  ✅ .env file exists")
    
    try:
        import config
        
        checks = {
            'Power BI Email': config.POWERBI_EMAIL,
            'Power BI Password': config.POWERBI_PASSWORD,
            'Report URL': config.POWERBI_REPORT_URL,
            'Email Address': config.EMAIL_ADDRESS,
            'Email Password': config.EMAIL_PASSWORD
        }
        
        missing = []
        for key, value in checks.items():
            if value and value != f"your_{key.lower().replace(' ', '_')}_here" and not value.startswith('your'):
                print(f"  ✅ {key} configured")
            else:
                print(f"  ⚠️  {key} not configured")
                missing.append(key)
        
        if missing:
            print(f"\n⚠️  Configure these in .env file: {', '.join(missing)}\n")
            return False
        
        print("✅ All configuration values set\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Error loading config: {e}\n")
        return False


def test_folders():
    """Test that necessary folders exist"""
    print("Testing folder structure...")
    
    folders = ['downloads', 'output', 'logs']
    for folder in folders:
        folder_path = Path(folder)
        if folder_path.exists():
            print(f"  ✅ {folder}/ folder exists")
        else:
            print(f"  ⚠️  {folder}/ folder missing (will be created automatically)")
    
    print()
    return True


def test_poppler():
    """Test Poppler installation (for PDF thumbnails)"""
    print("Testing Poppler (for PDF thumbnails)...")
    try:
        from pdf2image import convert_from_path
        # This will fail gracefully if poppler is not installed
        print("  ✅ pdf2image installed")
        print("  ℹ️  Poppler test requires a PDF file (will be tested during actual run)\n")
        return True
    except Exception as e:
        print(f"  ⚠️  pdf2image issue: {e}")
        print("  Install Poppler:")
        print("    - Linux: sudo apt-get install poppler-utils")
        print("    - Mac: brew install poppler")
        print("    - Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases\n")
        return True  # Not critical


def main():
    """Run all tests"""
    print("=" * 60)
    print("Power BI Automation - Setup Verification")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Packages", test_imports()))
    results.append(("Playwright", test_playwright()))
    results.append(("Configuration", test_config()))
    results.append(("Folders", test_folders()))
    results.append(("Poppler", test_poppler()))
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    
    all_passed = all(result[1] for result in results[:3])  # First 3 are critical
    
    if all_passed:
        print("🎉 Setup verification complete!")
        print("You're ready to run: streamlit run main.py")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("See README.md for detailed setup instructions.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

