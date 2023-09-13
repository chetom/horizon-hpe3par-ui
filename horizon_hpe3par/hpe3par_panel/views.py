# Copyright (c) 2016 Pure Storage, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# Modifications copyright (C) 2023 chetom


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
