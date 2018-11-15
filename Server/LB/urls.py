from django.conf.urls import url
from . import views

app_name = 'LB'

urlpatterns = [
    url(r'^project/$', views.project, name="project"),
    url(r'^instance/$', views.instance, name="instance"),
]