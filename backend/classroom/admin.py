from django.contrib import admin
from .models import (
    Classroom, 
    ClassRoomChallenge,
    ChallengeQuestion,
    QuestionOptions,
)

admin.site.register(Classroom)
admin.site.register(ClassRoomChallenge)
admin.site.register(ChallengeQuestion)
admin.site.register(QuestionOptions)
