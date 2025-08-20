#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Encoding test scripti - Unicode sorunlarını tespit etmek için
"""

import sys
import locale
import os

def test_encoding():
    print("=== ENCODING TEST ===")
    
    # Sistem bilgileri
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"File system encoding: {sys.getfilesystemencoding()}")
    print(f"Default encoding: {sys.getdefaultencoding()}")
    
    # Locale bilgileri
    try:
        print(f"Preferred encoding: {locale.getpreferredencoding()}")
        print(f"Locale: {locale.getlocale()}")
    except Exception as e:
        print(f"Locale error: {e}")
    
    # Environment variables
    print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'Not set')}")
    print(f"LANG: {os.environ.get('LANG', 'Not set')}")
    print(f"LC_ALL: {os.environ.get('LC_ALL', 'Not set')}")
    
    # Türkçe karakterler testi
    turkish_text = "Türkçe karakterler: çğıöşü ÇĞIÖŞÜ"
    print(f"\nTürkçe test: {turkish_text}")
    
    try:
        # ASCII encoding testi
        turkish_text.encode('ascii')
        print("ASCII encoding: OK")
    except UnicodeEncodeError as e:
        print(f"ASCII encoding error: {e}")
    
    try:
        # UTF-8 encoding testi
        utf8_encoded = turkish_text.encode('utf-8')
        utf8_decoded = utf8_encoded.decode('utf-8')
        print(f"UTF-8 encoding/decoding: OK - {utf8_decoded}")
    except Exception as e:
        print(f"UTF-8 error: {e}")
    
    # Streamlit import testi
    try:
        import streamlit as st
        print("Streamlit import: OK")
    except Exception as e:
        print(f"Streamlit import error: {e}")
    
    # OpenAI import testi
    try:
        from openai import OpenAI
        print("OpenAI import: OK")
    except Exception as e:
        print(f"OpenAI import error: {e}")
    
    print("=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_encoding()
