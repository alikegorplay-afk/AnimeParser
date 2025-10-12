import sys
import os

# Добавляем корневую директорию и src в PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, '..'))
sys.path.insert(0, os.path.join(project_root, '../src'))