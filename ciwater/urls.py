from django.conf.urls import include, url
from django.conf.urls.static import static

from django.contrib import admin
from ciwater import settings

admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'ciwater.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^', include('usu_data_service.urls'))
]
