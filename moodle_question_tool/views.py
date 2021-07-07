from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import UploadFileForm
from .file_handler import handle_uploaded_files, pdf2text

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
      pdf2text(filenames)
      # TODO: serve the converted file
      # TODO: Redirect to next page 
      return HttpResponseRedirect('/')
  else:
    form = UploadFileForm()
  return render(request, 'moodle_question_tool/convertion-pdftotext.html', {'form': form})
