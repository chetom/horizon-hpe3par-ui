from django.conf import settings
import logging
from hpe3parclient import client, exceptions
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
    'bandwidth',
]
RATIO_KEYS = [
    'data_reduction',
    'thin_provisioning',
    'total_reduction'
]


def adjust_size(mib):
    return mib / (1024 ** 2)

class ErrorStateArray(client.HPE3ParClient):
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
            array = client.HPE3ParClient(conf['wsapi_url'])
            array.setSSHOptions(ip=conf['ssh_ip'], login=conf['ssh_user'], password=conf['ssh_password'])
            array.login(conf['wsapi_user'], conf['wsapi_password'])
            array.error = None
            return array
        except Exception as e:
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

    def get_total_stats(self):
        stats = {}
        arrays = self._array_id_list

        for array_id in arrays:
            array_stats = self.get_array_stats(array_id)
            for key in array_stats:
                if key in stats:
                    stats[key] += array_stats[key]
                else:
                    stats[key] = array_stats[key]

        LOG.debug('Found total stats for flash arrays: %s' % stats)
        return stats

    def get_array_stats(self, array_id):
        array = self._get_array(array_id)

        total_used = 0
        total_available = 0
        total_volume_count = 0
        total_vluns_count = 0
        available_volume_count = 0
        available_vluns_count = 0

        if not array.error:
            info = {}
            array_volume_cap = 16384
            array_vluns_cap = 131072
            
            available_volume_count += array_volume_cap
            available_vluns_count += array_vluns_cap
            
            total_volume_count += array.getVolumes()['total']
            total_vluns_count += array.getVLUNs()['total']
            
            space_info = array.getStorageSystemInfo()
            
            total_used = total_used + space_info['allocatedCapacityMiB']
            total_available = total_available + space_info['totalCapacityMiB']

            perf_info = array.getCPGStatData('*', interval='hourly', history='2h')

            throughput = perf_info['throughput']
            bandwidth = adjust_size(perf_info['bandwidth'])
            latency = perf_info['latency']




        # total_used = adjust_size(total_used)
        # total_available = adjust_size(total_available)

        stats = {
            'total_used': total_used,
            'total_available': total_available,
            'total_volume_count': total_volume_count,
            'available_volume_count': available_volume_count,
            'total_vluns_count': total_vluns_count,
            'available_vluns_count': available_vluns_count,
            'throughput': throughput,
            'bandwidth': bandwidth,
            'latency': latency,
        }
        return stats
    
    def get_array_list(self):
        return self._array_id_list

    def get_array_info(self, array_id, detailed=False):
        array = self._get_array(array_id)
        storage_system_info = array.getStorageSystemInfo()

        info = {}
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
        info['array_name'] = storage_system_info['name']
        info['target'] = storage_system_info['IPv4Addr']
        info['id'] = storage_system_info['id']
        info['version'] = storage_system_info['systemVersion']
        LOG.debug('Found flash array info for %s: %s' % (array_id, str(info)))
        return base.APIDictWrapper(info)
