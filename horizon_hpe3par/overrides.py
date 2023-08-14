import logging

from django.utils.translation import ugettext_lazy as _
from horizon import tables
from openstack_dashboard.dashboards.project.volumes import tables \
    as volumes_tables
from openstack_dashboard.dashboards.project.volumes import tabs


from horizon_hpe3par.api import hpe3par_flash_array


LOG = logging.getLogger(__name__)


array_api = hpe3par_flash_array.FlashArrayAPI()


class HPE3ParVolumeTable(volumes_tables.VolumesTable):
    used_space = tables.Column('used_space', verbose_name=_("Used"))

    class Meta(volumes_tables.VolumesTable.Meta):
        pass


class HPE3ParVolumeTab(tabs.VolumeDetailTabs):
    table_classes = (HPE3ParVolumeTable,)

    def get_volumes_data(self):
        volumes = super(HPE3ParVolumeTab, self).get_volumes_data()

        hpe3par_volumes = array_api.get_volumes_data(volumes)
        return hpe3par_volumes


def get_hpe3par_volume_context_data(self, request):
    vol = self.tab_group.kwargs['volume']
    hpe3par_vol = array_api.get_volume_info(vol)
    LOG.debug("Patched volume: " + str(hpe3par_vol.to_dict()))
    return {"volume": hpe3par_vol}


LOG.debug("Setting overrides for Project VolumeAndSnapshotTabs.")
# Patch our updated versions of the volume tab into the TabGroup
#vol_tabs = tabs.VolumeAndSnapshotTabs.tabs
#purified_tabs = [PureVolumeTab]
# for tab in vol_tabs:
#     if tab != tabs.VolumeTab:
#         purified_tabs.append(tab)

#tabs.VolumeAndSnapshotTabs.tabs = tuple(vol_tabs)

tabs.OverviewTab.template_name = "project/volumes/hpe3par_detail_view.html"

# TODO: Maybe hook in at the tab group step and see if we can avoid requerying
# so much from the array.
tabs.OverviewTab.get_context_data = get_hpe3par_volume_context_data

LOG.debug("Completed overrides for Project VolumeAndSnapshotTabs.")
