from django.core.files.storage import FileSystemStorage

def handle_uploaded_files(files):
  fs = FileSystemStorage()
  
  for file in files:
    fs.save(file.name, file)