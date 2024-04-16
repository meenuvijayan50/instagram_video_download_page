from django.urls import path
from . import views




urlpatterns = [
    path('', views.enter_url, name='enter_url'),
    path('show_success_page',views.show_success_page,name='show_success_page'),
    path('download_video', views.download_video, name='download_video'),


]