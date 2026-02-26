import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','genai_project.settings')
django.setup()
from django.template.loader import render_to_string
print(render_to_string('dashboard.html',{'total':1,'correct':0,'accuracy':0}))
