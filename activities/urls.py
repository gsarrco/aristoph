from django.urls import path

from . import views

app_name = 'activities'

urlpatterns = [
    path('', views.list_activities, name='list_activities'),
    path('participations/edit', views.edit_participations, name='edit_participations'),
    path('create', views.create_activities, name='create_activities'),
    path('<int:activity_id>/add_users_to_meetings/<str:meetings>', views.add_users_to_meetings,
         name='add_users_to_meetings'),
    path('<int:activity_id>/', views.show_activity, name='show_activity'),
    path('<int:activity_id>/registrations/create', views.create_registrations, name='create_registrations'),
    path('<int:activity_id>/meetings/stats', views.list_meetings_stats, name='list_meetings_stats'),
    path('<int:activity_id>/subjects/create', views.create_subjects, name='create_subjects'),
    path('<int:activity_id>/subjects/<int:subject_id>/applications/create', views.create_applications,
         name='create_applications'),
    path('<int:activity_id>/subjects/<int:subject_id>/users', views.show_activity_users,
         name='show_activity_users'),
    path('<int:activity_id>/subjects/<int:subject_id>/add_users_by_classe', views.add_users_by_classe,
         name='add_users_by_classe'),

    path('<int:activity_id>/subjects/<int:subject_id>/users', views.show_activity_users,
         name='show_activity_users'),
    path('<int:activity_id>/participations/stats', views.list_participations_stats, name='list_participations_stats'),

    path('<int:activity_id>/participations', views.list_participations, name='list_participations'),
    path('<int:activity_id>/participations/xlsx', views.list_participations_xlsx, name='list_participations_xlsx'),
    path('<int:activity_id>/participations/user/<int:user_id>', views.list_participations_by_user,
         name='list_participations_by_user'),
    path('<int:activity_id>/subjects/<int:subject_id>/', views.show_subject, name='show_subject'),
    path('<int:activity_id>/subjects/<int:subject_id>/meetings/create', views.create_meetings, name='create_meetings'),
    path('<int:activity_id>/subjects/<int:subject_id>/meetings/<int:meeting_id>/delete', views.delete_meeting,
         name='delete_meeting'),
    path('<int:activity_id>/subjects/<int:subject_id>/meetings/<int:meeting_id>', views.show_meeting,
         name='show_meeting'),
    path('<int:activity_id>/subjects/<int:subject_id>/meetings/<int:meeting_id>/reserve', views.reserve_meeting,
         name='reserve_meeting'),
    path('<int:activity_id>/subjects/<int:subject_id>/meetings/<int:meeting_id>/edit_topic', views.edit_topic,
         name='edit_topic'),
    path('<int:activity_id>/participations/<int:participation_id>', views.show_participation,
         name='show_participation'),
    path('<int:activity_id>/participations/<int:participation_id>/delete', views.delete_participation,
         name='delete_participation'),
    path('<int:activity_id>/dates/<int:year>/<int:month>/<int:day>/', views.show_date, name='show_date'),
    path('<int:activity_id>/stats/subjects', views.subject_stats, name='subject_stats'),
    path('<int:activity_id>/stats/classi/<int:participation_group_id>', views.classe_stats, name='classe_stats'),
    path('<int:activity_id>/stats/users/<int:participation_group_id>', views.user_stats, name='user_stats'),
    path('<int:activity_id>/stats/users/<int:participation_group_id>/xlsx', views.user_stats_xlsx,
         name='user_stats_xlsx'),
    path('clean_up_presences', views.clean_up_presences, name='clean_up_presences'),
]
