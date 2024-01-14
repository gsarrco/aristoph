from django.urls import path

from . import views

app_name = 'stats'

urlpatterns = [
    path('presences_by_meeting_and_user/<int:activity_id>/<int:subject_id>/<int:group_id>',
         views.presences_by_meeting_and_user, name='presences_by_meeting_and_user'),
    path('student_registry/<int:activity_id>', views.student_registry, name='student_registry'),
]
