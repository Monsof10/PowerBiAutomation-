"""
Setup Verification - Test configuration and dependencies
"""
import sys


def test_imports():
    """Test that required packages are installed"""
    packages = ['streamlit', 'msal', 'requests', 'pypdf', 'yagmail', 'dotenv']
    missing = []
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    return len(missing) == 0


def test_config():
    """Test configuration"""
    import config
    
    required = {
        'POWERBI_EMAIL': config.POWERBI_EMAIL,
        'POWERBI_PASSWORD': config.POWERBI_PASSWORD,
        'POWERBI_REPORT_URL': config.POWERBI_REPORT_URL,
        'EMAIL_ADDRESS': config.EMAIL_ADDRESS,
        'EMAIL_PASSWORD': config.EMAIL_PASSWORD
    }
    
    missing = [k for k, v in required.items() if not v]
    
    for key in required:
        status = "✅" if key not in missing else "❌"
        print(f"{status} {key}")
    
    return len(missing) == 0


def main():
    """Run all tests"""
    print("="*60)
    print("SETUP VERIFICATION")
    print("="*60)
    
    print("\n1. Testing Imports:")
    imports_ok = test_imports()
    
    print("\n2. Testing Configuration:")
    config_ok = test_config()
    
    print("\n" + "="*60)
    
    if imports_ok and config_ok:
        print("✅ All checks passed!")
        return 0
    else:
        print("❌ Some checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

