from django.conf.urls import include
from django.conf.urls import url

from horizon_hpe3par.hpe3par_panel import views
from horizon_hpe3par.hpe3par_panel.flasharrays import urls as array_urls


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'', include((
        array_urls,
        'flasharrays'))),
]

