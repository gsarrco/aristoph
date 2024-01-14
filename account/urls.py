from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    path('register', views.register, name='register'),
    path('settings', views.settings, name='settings'),
    path('change_password', views.change_password, name='change_password'),
    path('update_user', views.update_user, name='update_user'),
    path('import_users', views.import_users, name='import_users'),
    path('set_parent', views.set_parent, name='set_parent'),
    path('<int:user_id>/update_notes', views.update_notes, name='update_notes')
]