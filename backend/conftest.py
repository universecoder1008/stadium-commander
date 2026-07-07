import sys
import os

# Automatically append backend folder to path during test execution
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
