#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
from rag.retriever import retrieve

tests = [
    "symptoms of dengue",
    "how to prevent type 2 diabetes",
    "what causes high blood pressure",
    "who won the cricket world cup",
    "best pizza recipe",
]
for q in tests:
    print(q, "->", round(retrieve(q, 1)[0]["distance"], 3))