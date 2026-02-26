from django.contrib import admin

from .models import Attempt, MindMap, Question, QuizSession, UserProfile


admin.site.register(UserProfile)
admin.site.register(QuizSession)
admin.site.register(Question)
admin.site.register(Attempt)
admin.site.register(MindMap)
