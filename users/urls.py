from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('<int:user_id>/', views.show_users, name='show_users')
]
