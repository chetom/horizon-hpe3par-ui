from django.conf import settings
import logging
from hp3parclient import client, exceptions
import re

from openstack_dashboard.api import base

from horizon_hpe3par.api import cinder as hpe3par_cinder_api


LOG = logging.getLogger(__name__)

SIZE_KEYS = [
    'capacity',
    'snapshots',
    'volumes',
    'total',
    'shared_space',
    'input_per_sec',
    'output_per_sec',
]
RATIO_KEYS = [
    'data_reduction',
    'thin_provisioning',
    'total_reduction'
]

class ErrorStateArray(client.HP3ParClient):
    def __init__(self, target, e):
        self._target = target
        self.error = e


class FlashArrayAPI(object):
    def __init__(self):
        self._arrays = {}
        self._array_config = getattr(settings, 'HPE3PAR_FLASH_ARRAYS')
        self._array_id_list = []
        self._init_all_arrays()

    def _init_all_arrays(self):
        for array_conf in self._array_config:
            array_id = array_conf['backend_name']
            array = self._get_array_from_conf(array_conf)
            self._arrays[array_id] = array
            self._array_id_list.append(array_id)

    def _get_array_from_conf(self, conf):
        try:
            array = client.HP3ParClient(conf['wsapi_url'])
            array.login(conf['wsapi_user'], conf['wsapi_password'])
            array.error = None
            return array
        except exceptions.ClientException as e:
            LOG.warning('Unable to create HPE 3Par FlashArray client: %s'
                        % str(e))
            return ErrorStateArray(conf['wsapi_url'], 'Failed to connect')

    def _get_array(self, array_id):
        array = self._arrays.get(array_id)
        if array and array.error:
            LOG.debug('Removing FlashArray client for %s that was in error '
                      'state.' % array_id)
            array = None
            self._arrays[array_id] = None
        if not array:
            LOG.debug('Initializing FlashArray client for ' + array_id)
            if self._array_config:
                for array_conf in self._array_config:
                    be_name = array_conf.get('backend_name')
                    if be_name == array_id:
                        array = self._get_array_from_conf(array_conf)
                        self._arrays[array_id] = array
                        break
                if not array:
                    LOG.error('Failed to find array in conf for %s' % array_id)
                    array = ErrorStateArray('array_id', 'Not in config')
        else:
            LOG.debug('Using existing FlashArray client for ' + array_id)
        return array

    def get_volumes_data(self, volumes):
        data = []
        for vol in volumes:
            data.append(self.get_volume_info(vol))
        return data

    def _get_volume_stats(self, array, vol_id):
        stats = {}
        hpe3par_vol_name = 'osv-%s' % hpe3par_cinder_api.HPE3ParVolume.find_name(vol_id)
        LOG.debug('Getting volume stats for %s from %s' % (vol_id, array))
        stats.update({
            'vv_name': hpe3par_vol_name,
                    })
        LOG.debug('stats = %s' % stats)
        return stats

    def get_volume_info(self, volume):
        stats = {}
        try:
            backend = getattr(volume, 'os-vol-host-attr:host')
            backend = re.split('@', backend)[1]
            backend = re.split('#', backend)[0]
            LOG.debug('Found backend %s' % backend)
        except Exception:
            backend = ''
            LOG.debug('Backend not found. Looping...')
        if backend:
            # Fast path, we are an admin and know what array it belongs to
            array = self._get_array(backend)
            LOG.debug('Got array %s' % array)
            if array and not array.error:
                try:
                    stats = self._get_volume_stats(array, volume.id)
                except Exception as e:
                    LOG.exception(e)
                    LOG.warning('Failed to get HPE 3Par volume info: %s' % e)
        else:
            for array_id in self._array_id_list:
                array = self._get_array(array_id)
                LOG.debug('Trying array %s' % array)
                try:
                    stats = self._get_volume_stats(array, volume.id)
                    break
                except Exception as e:
                    LOG.debug('Unable to get volume stats from %s for vol %s:'
                              ' %s' % (array_id, volume.id, e))
            if not stats:
                LOG.debug('Failed to find volume %s on any configured arrays!'
                          % volume.id)

        stats.update(volume.to_dict())
        return hpe3par_cinder_api.HPE3ParVolume(base.APIDictWrapper(stats))

    # def get_host_stats(self, host):
    #     # TODO: Lookup the purity host and return perf info and connected volumes
    #     return {}

    # def get_total_stats(self):
    #     stats = {}
    #     arrays = self._array_id_list

    #     for array_id in arrays:
    #         array_stats = self.get_array_stats(array_id)
    #         for key in array_stats:
    #             if key in stats:
    #                 stats[key] += array_stats[key]
    #             else:
    #                 stats[key] = array_stats[key]

    #     LOG.debug('Found total stats for flash arrays: %s' % stats)
    #     return stats

    # def get_array_stats(self, array_id):
    #     array = self._get_array(array_id)

    #     total_used = 0
    #     total_available = 0
    #     total_volume_count = 0
    #     total_snapshot_count = 0
    #     total_host_count = 0
    #     total_pgroup_count = 0
    #     available_volume_count = 0
    #     available_snapshot_count = 0
    #     available_host_count = 0
    #     available_pgroup_count = 0

    #     if not array.error:
    #         info = array.get()
    #         array_volume_cap = 500
    #         array_snapshot_cap = 5000
    #         array_host_cap = 50
    #         array_pgroup_cap = 50
    #         version = info['version'].split('.')
    #         if ((int(version[0]) == 4 and int(version[1]) >= 8) or
    #                 (int(version[0]) > 4)):
    #             array_volume_cap = 5000
    #             array_snapshot_cap = 50000
    #             array_pgroup_cap = 250
    #             array_host_cap = 500
    #         if ((int(version[0]) == 5 and int(version[1]) >= 3)):
    #             array_volume_cap = 10000
    #         if (int(version[0]) > 5):
    #             array_volume_cap = 20000
    #             array_snapshot_cap = 100000
    #             array_host_cap = 1000

    #         available_volume_count += array_volume_cap
    #         available_snapshot_count += array_snapshot_cap
    #         available_host_count += array_host_cap
    #         available_pgroup_count += array_pgroup_cap

    #         total_volume_count += len(array.list_volumes(pending=True))
    #         total_snapshot_count += len(array.list_volumes(snap=True,
    #                                                        pending=True))
    #         total_host_count += len(array.list_hosts())

    #         total_pgroup_count += len(array.list_pgroups(snap=False,
    #                                                      pending=True))
    #         space_info = array.get(space=True)
    #         if isinstance(space_info, list):
    #             space_info = space_info[0]
    #         total_used = total_used + space_info['total']
    #         total_available = total_available + space_info['capacity']

    #     total_used = adjust_purity_size(total_used)
    #     total_available = adjust_purity_size(total_available)

    #     stats = {
    #         'total_used': total_used,
    #         'total_available': total_available,
    #         'total_volume_count': total_volume_count,
    #         'available_volume_count': available_volume_count,
    #         'total_snapshot_count': total_snapshot_count,
    #         'available_snapshot_count': available_snapshot_count,
    #         'total_host_count': total_host_count,
    #         'available_host_count': available_host_count,
    #         'total_pgroup_count': total_pgroup_count,
    #         'available_pgroup_count': available_pgroup_count,
    #     }
    #     return stats

    def get_array_list(self):
        return self._array_id_list

    def get_array_info(self, array_id, detailed=False):
        array = self._get_array(array_id)
        if array.error:
            info = {
                'id': '1',
                'status': 'Error: ' + array.error,
            }
        else:
            info['status'] = 'Connected'
            if detailed:
                pass    
        info['cinder_name'] = array_id
        info['cinder_id'] = array_id
        info['target'] = array._target
        LOG.debug('Found flash array info for %s: %s' % (array_id, str(info)))
        return base.APIDictWrapper(info)
