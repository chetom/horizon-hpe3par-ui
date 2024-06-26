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


from django.utils.translation import gettext_lazy as _
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
