import os
import sys
from pathlib import Path

# Get the absolute path of the project root
BASE_DIR = Path(__file__).resolve().parent

# Add the project root to Python path
sys.path.append(str(BASE_DIR))

os.environ["DJANGO_SETTINGS_MODULE"] = "agoa.settings"

import django
django.setup() 