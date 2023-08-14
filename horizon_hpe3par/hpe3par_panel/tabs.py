from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
import re

from horizon_hpe3par.api import hpe3par_flash_array
from horizon_hpe3par.hpe3par_panel import tables


class FlashArrayTab(tabs.TableTab):
    name = _("FlashArrays")
    slug = "flasharray_tab"
    table_classes = (tables.HPE3ParFlashArrayTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = False
    array_api = None

    def has_more_data(self, table):
        return self._has_more

    def get_flasharrays_data(self):
        try:
            # TODO: Add pagination
            self._has_more = False

            if not self.array_api:
                self.array_api = hpe3par_flash_array.FlashArrayAPI()

            arrays = []
            backends = self.array_api.get_array_list()
            for be in backends:
                arrays.append(self.array_api.get_array_info(be))

            return arrays

        except Exception as e:
            error_message = _('Unable to get arrays')
            exceptions.handle(self.request, error_message)
            return []


class HPE3ParPanelTabs(tabs.TabGroup):
    slug = "hpe3par_panel_tabs"
    tabs = (FlashArrayTab,)
    sticky = True
