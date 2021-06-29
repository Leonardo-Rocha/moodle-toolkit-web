from django.shortcuts import render

def home(request):
  return render(request, 'moodle_question_tool/home.html')


def examples(request):
  return render(request, 'moodle_question_tool/examples.html')
