from django.urls import reverse

from horizon import tabs

from horizon_hpe3par.hpe3par_panel.flasharrays import tabs as flasharray_tabs


class DetailView(tabs.TabView):
    tab_group_class = flasharray_tabs.FlashArrayDetailTabs
    template_name = 'horizon/common/_detail.html'
    page_title = "{{ backend.name }}"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['backend_id'] = self.get_data()
        return context

    def get_redirect_url(self):
        return reverse('horizon:admin:hpe3par_panel:index')

    def get_data(self):
        return self.kwargs['backend_id']
