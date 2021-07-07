from django.core.files.storage import FileSystemStorage
from django.conf import settings
import uuid
import os

import sys, os.path as path
from inspect import getsourcefile

# parent_dir = path.dirname(path.dirname(path.dirname(path.abspath(getsourcefile(lambda: 0)))))
# print(path.join(settings.BASE_DIR, 'moodle-question-toolkit'))
# sys.path.append(path.join(settings.BASE_DIR, 'moodle-question-toolkit'))

# # make sure to hack the sys.path
# # before importing your own modules

# from . import src
# from .core import moodle_question_toolkit

def handle_uploaded_files(files):
  fs = FileSystemStorage()
  
  filenames = []

  for file in files:
    filename = os.path.join(f'pdf2text-{uuid.uuid4()}', file.name)
    filenames.append(filename)
    fs.save(filename, file)

  return filenames


def pdf2text(filenames):
  # for file in filenames:
  #   moodle_question_toolkit.pdf_to_text(file)
