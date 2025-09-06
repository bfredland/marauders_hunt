#!/usr/bin/python3
import sys
import os

# Add your project directory to the sys.path
path = '/home/yourusername/marauders_hunt'
if path not in sys.path:
    sys.path.insert(0, path)

os.chdir(path)

from app import app as application

if __name__ == "__main__":
    application.run()