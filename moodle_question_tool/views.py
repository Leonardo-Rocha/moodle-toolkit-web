from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import UploadFileForm
from .file_handler import handle_uploaded_files, pdf2text, zipfiles, get_static_file_from_path, md2tex

def home(request):
  return render(request, 'moodle_question_tool/home.html')


def examples(request):
  return render(request, 'moodle_question_tool/examples.html')


def convertion(request):
  return render(request, 'moodle_question_tool/convertion.html')


def convertion_pdf_to_text(request):
  if request.method == 'POST':
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
      filenames = handle_uploaded_files(request.FILES.getlist('files'))
      output_dir = pdf2text(filenames)
      zipfiles(output_dir)
      url = get_static_file_from_path(f'{output_dir}.zip')
  else:
    form = UploadFileForm()
    url = None
  return render(request, 'moodle_question_tool/convertion-pdftotext.html', {'form': form, 'url': url})


def convertion_md_to_tex(request):
  if request.method == 'POST':
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
      filenames = handle_uploaded_files(request.FILES.getlist('files'), 'md2tex')
      output_dir = md2tex(filenames)
      zipfiles(output_dir)
      url = get_static_file_from_path(f'{output_dir}.zip')
  else:
    form = UploadFileForm()
    url = None
  return render(request, 'moodle_question_tool/convertion-mdtotex.html', {'form': form, 'url': url})
