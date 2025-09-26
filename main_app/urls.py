from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('respondents/', views.respondents_list, name='respondents'),
    path('question/<int:question_id>/vote/', views.vote, name='vote'),
    path('login/', auth_views.LoginView.as_view(template_name='main_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('questions/', views.question_list, name='question_list'),
    path('questions/create/', views.create_question, name='create_question'),
    path('questions/<int:pk>/edit/', views.edit_question, name='edit_question'),
    path('questions/<int:pk>/delete/', views.delete_question, name='delete_question'),
    path('question/<int:question_id>/add_choice/', views.add_choice, name='add_choice'),
    path('choice/<int:pk>/delete/', views.delete_choice, name='delete_choice'),
    path('account/', views.edit_account, name='account'),
    path('delete_users/', views.delete_users, name='delete_users'),

]
