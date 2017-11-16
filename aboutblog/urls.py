from django.conf.urls import url
from . import views

app_name = 'aboutblog'
urlpatterns = [
    url(r'^about/$', views.about_page, name='about'),
]
