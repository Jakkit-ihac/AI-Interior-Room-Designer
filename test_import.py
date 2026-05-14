#!/usr/bin/env python
"""Test script to debug app.py startup issues"""

import sys
import traceback

print("=" * 60)
print("Testing imports...")
print("=" * 60)

try:
    print("✓ Loading Streamlit...")
    import streamlit as st
    print(f"  Streamlit version: {st.__version__}")
except Exception as e:
    print(f"✗ Streamlit failed: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("✓ Loading PIL...")
    from PIL import Image
except Exception as e:
    print(f"✗ PIL failed: {e}")
    traceback.print_exc()

try:
    print("✓ Loading other libraries...")
    import os, base64, io, requests
    import urllib.parse
    import time
except Exception as e:
    print(f"✗ Standard libs failed: {e}")
    traceback.print_exc()

try:
    print("✓ Loading python-dotenv...")
    from dotenv import load_dotenv
    load_dotenv()
    print("  ENV loaded")
except Exception as e:
    print(f"✗ dotenv failed: {e}")
    traceback.print_exc()

try:
    print("✓ Loading google.generativeai...")
    import google.generativeai as genai
    print("  Genai OK")
except Exception as e:
    print(f"⚠ google.generativeai failed: {e}")
    print("  (This is OK - using fallback)")

try:
    print("✓ Loading Replicate...")
    import replicate
    print("  Replicate OK")
except Exception as e:
    print(f"✗ Replicate failed: {e}")

try:
    print("✓ Loading rembg...")
    from rembg import remove
    print("  Rembg OK")
except Exception as e:
    print(f"✗ Rembg failed: {e}")
    print("  (This is optional)")

try:
    print("✓ Loading product_shopping_utils...")
    from product_shopping_utils import detect_products_in_room, get_product_suggestions, calculate_total_budget, get_product_by_id
    print("  Utils loaded OK")
except Exception as e:
    print(f"✗ Utils failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL IMPORTS SUCCESSFUL!")
print("=" * 60)
print("\nApp should work. Run:")
print("  python -m streamlit run app.py")
