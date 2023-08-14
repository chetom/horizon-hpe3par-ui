from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from horizon_hpe3par.api import hpe3par_flash_array


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("hpe3par_panel/flasharrays/detail_view.html")

    def get_context_data(self, request):
        context = super(OverviewTab, self).get_context_data(request)
        context['backend_id'] = self.tab_group.kwargs['backend_id']
        try:
            array_api = hpe3par_flash_array.FlashArrayAPI()
            context['array'] = array_api.get_array_info(context['backend_id'],
                                                        detailed=True)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve FlashArray details.'))

        return context


class FlashArrayDetailTabs(tabs.TabGroup):
    slug = "flasharray_details"
    tabs = (OverviewTab,)