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


import horizon
from django.utils.translation import gettext_lazy as _
from openstack_dashboard.dashboards.admin import dashboard


class HPE3ParPanel(horizon.Panel):
    name = _("HPE 3Par Storage")
    slug = "hpe3par_panel"


dashboard.Admin.register(HPE3ParPanel)
