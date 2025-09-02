#!/usr/bin/env python3
"""
Test script to verify that all required modules can be imported correctly.
Run this after installing dependencies to ensure everything is working.
"""

import sys
import os

def test_imports():
    """Test importing all required modules."""
    print("🧪 Testing module imports...")
    print("=" * 40)
    
    # Test core Python modules
    print("📦 Testing core Python modules...")
    try:
        import ast
        print("  ✅ ast (built-in)")
    except ImportError as e:
        print(f"  ❌ ast: {e}")
    
    try:
        import json
        print("  ✅ json (built-in)")
    except ImportError as e:
        print(f"  ❌ json: {e}")
    
    try:
        import time
        print("  ✅ time (built-in)")
    except ImportError as e:
        print(f"  ❌ time: {e}")
    
    # Test third-party packages
    print("\n📦 Testing third-party packages...")
    
    try:
        import requests
        print(f"  ✅ requests {requests.__version__}")
    except ImportError as e:
        print(f"  ❌ requests: {e}")
    
    try:
        import pandas
        print(f"  ✅ pandas {pandas.__version__}")
    except ImportError as e:
        print(f"  ❌ pandas: {e}")
    
    try:
        import numpy
        print(f"  ✅ numpy {numpy.__version__}")
    except ImportError as e:
        print(f"  ❌ numpy: {e}")
    
    try:
        import dotenv
        print(f"  ✅ python-dotenv")
    except ImportError as e:
        print(f"  ❌ python-dotenv: {e}")
    
    # Test our custom modules
    print("\n🔧 Testing custom modules...")
    
    try:
        from config.settings import get_config
        print("  ✅ config.settings")
    except ImportError as e:
        print(f"  ❌ config.settings: {e}")
    
    try:
        from agents.base_agent import BaseAgent
        print("  ✅ agents.base_agent")
    except ImportError as e:
        print(f"  ❌ agents.base_agent: {e}")
    
    try:
        from agents.memory import Memory
        print("  ✅ agents.memory")
    except ImportError as e:
        print(f"  ❌ agents.memory: {e}")
    
    try:
        from agents.planner import Planner
        print("  ✅ agents.planner")
    except ImportError as e:
        print(f"  ❌ agents.planner: {e}")
    
    try:
        from tools.code_tools import analyze_code
        print("  ✅ tools.code_tools")
    except ImportError as e:
        print(f"  ❌ tools.code_tools: {e}")
    
    try:
        from tools.data_tools import query_data
        print("  ✅ tools.data_tools")
    except ImportError as e:
        print(f"  ❌ tools.data_tools: {e}")
    
    try:
        from tools.search_tools import search_knowledge
        print("  ✅ tools.search_tools")
    except ImportError as e:
        print(f"  ❌ tools.search_tools: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 Import testing completed!")

def test_basic_functionality():
    """Test basic functionality of key components."""
    print("\n🧪 Testing basic functionality...")
    print("=" * 40)
    
    try:
        from config.settings import get_config
        config = get_config()
        print(f"✅ Configuration loaded: {len(config)} settings")
        print(f"  - Ollama URL: {config.get('ollama_base_url', 'N/A')}")
        print(f"  - Default Model: {config.get('default_model', 'N/A')}")
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
    
    try:
        from agents.memory import Memory
        memory = Memory()
        stats = memory.get_stats()
        print(f"✅ Memory system initialized: {stats['total_items']} items")
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
    
    try:
        from agents.planner import Planner
        planner = Planner()
        print(f"✅ Planner system initialized")
    except Exception as e:
        print(f"❌ Planner test failed: {e}")
    
    try:
        from tools.code_tools import analyze_code
        sample_code = "def hello(): print('Hello, World!')"
        result = analyze_code(sample_code, "python")
        if "error" not in result:
            print(f"✅ Code analysis tool working: {result.get('metrics', {}).get('functions', 0)} functions found")
        else:
            print(f"❌ Code analysis failed: {result['error']}")
    except Exception as e:
        print(f"❌ Code tools test failed: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 Functionality testing completed!")

def main():
    """Main test function."""
    print("🧠 AI Agent Project - Installation Test")
    print("=" * 50)
    print()
    
    # Test imports
    test_imports()
    
    # Test basic functionality
    test_basic_functionality()
    
    print("\n🎉 All tests completed!")
    print("\n💡 If you see any ❌ errors above, please:")
    print("  1. Check that all dependencies are installed")
    print("  2. Ensure you're in the correct directory")
    print("  3. Try running: pip install -r requirements.txt")
    print("\n🚀 If all tests pass, you're ready to run the examples!")

if __name__ == "__main__":
    main()
