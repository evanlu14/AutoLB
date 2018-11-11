from django.conf.urls import url
from . import views

app_name = 'LB'

urlpatterns = [
    url(r'^project/create$', views.projCreate, name="pc"),
    url(r'^project/info$', views.projInfo, name="pi"),
    url(r'^project/update$', views.projUpdate, name="pu"),
    url(r'^project/delete$', views.projDelete, name="pd"),
    url(r'^instance/create$', views.insCreate, name="ic"),
    url(r'^instance/info$', views.insInfo, name="ii"),
    url(r'^instance/update$', views.insUpdate, name="iu"),
    url(r'^instance/delete$', views.insDelete, name="id"),
]