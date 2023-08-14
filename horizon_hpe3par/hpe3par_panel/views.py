from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from horizon_hpe3par.api import hpe3par_flash_array
from horizon_hpe3par.hpe3par_panel import tabs as hpe3par_tabs


class IndexView(tabs.TabbedTableView):
    template_name = 'hpe3par_panel/index.html'
    tab_group_class = hpe3par_tabs.HPE3ParPanelTabs
    page_title = "HPE 3Par Storage"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        try:
            array_api = hpe3par_flash_array.FlashArrayAPI()
            context["stats"] = array_api.get_total_stats()
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve Flash Array statistics.'))
        return context
