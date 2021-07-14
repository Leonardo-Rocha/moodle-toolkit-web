from django.core.files.storage import FileSystemStorage
from django.conf import settings
import uuid
import os
from zipfile import ZipFile

from .core import moodle_question_toolkit

def handle_uploaded_files(files, convertion_type = 'pdf2text'):
  fs = FileSystemStorage()
  
  filenames = []
  base_dir = f'{convertion_type}-{uuid.uuid4()}'

  for file in files:
    filename = os.path.join(base_dir, file.name)
    filenames.append(filename)
    fs.save(filename, file)

  return filenames


def get_static_file_from_path(filepath):
  fs = FileSystemStorage()
  return fs.url(filepath.split('tmp/')[1].split('media/')[1])


def pdf2text(filenames):
  output_dir = ''
  for file in filenames:
    fullpath = os.path.join('tmp', 'media', file)
    # print(fullpath)
    output_dir = moodle_question_toolkit.pdf_to_text(fullpath)

  return output_dir


def md2tex(filenames):
  output_dir = ''
  for file in filenames:
    fullpath = os.path.join('tmp', 'media', file)
    # print(fullpath)
    output_dir = moodle_question_toolkit.MD_to_tex(fullpath)

  return output_dir


def zipfiles(directory):
  # initializing empty file paths list
  file_paths = []
  
  # crawling through directory and subdirectories
  for root, directories, files in os.walk(directory):
    for filename in files:
      # join the two strings in order to form the full filepath.
      filepath = os.path.join(root, filename)
      file_paths.append(filepath)

  # printing the list of all files to be zipped
  # print('Following files will be zipped:')
  # for file_name in file_paths:
  #   print(file_name)

  # writing files to a zipfile
  with ZipFile(f'{directory}.zip','w') as zip:
    # writing each file one by one
    for file in file_paths:
      zip.write(file)
  
