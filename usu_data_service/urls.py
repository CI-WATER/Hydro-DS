from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from ciwater import settings
from usu_data_service import views
 
urlpatterns = patterns('',
  url(r'^api/dataservice/(?P<func>[A-z0-9]+)$', views.RunService.as_view()),
  url(r'^api/dataservice/showstaticdata/info', views.show_static_data_info),
  url(r'^api/dataservice/myfiles/list', views.show_my_files),
  url(r'^api/dataservice/myfiles/delete/(?P<filename>[^/]+)$', views.delete_my_file),
  url(r'^api/dataservice/myfiles/upload', views.upload_file),
  url(r'^api/dataservice/myfiles/zip', views.zip_my_files),
  url(r'^api/dataservice/hydroshare/createresource', views.create_hydroshare_resource),
)
 
urlpatterns = format_suffix_patterns(urlpatterns)
