from django.urls import path
from django.conf.urls import url
from .import views
app_name='apis'
urlpatterns = 	[
					url(r'^students/$', views.StudentsApi.as_view(), name='api-students'),
				]