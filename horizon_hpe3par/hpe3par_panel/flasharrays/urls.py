from django.conf.urls import url

from horizon_hpe3par.hpe3par_panel.flasharrays import views


urlpatterns = [
    url(r'^(?P<backend_id>[^/]+)/$',
        views.DetailView.as_view(),
        name='detail'),
]
