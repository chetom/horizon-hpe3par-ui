
from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.admin import dashboard


class HPE3ParPanel(horizon.Panel):
    name = _("HPE3Par Storage")
    slug = "hpe3par_panel"


dashboard.Admin.register(HPE3ParPanel)
