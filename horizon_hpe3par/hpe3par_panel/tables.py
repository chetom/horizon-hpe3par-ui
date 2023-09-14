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


import logging
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import tables
from horizon.templatetags import sizeformat

LOG = logging.getLogger(__name__)


class HPE3ParFilterAction(tables.FilterAction):
    name = "hpe3parfilter"


def get_hpe3par_url(array_info):
    LOG.debug('Building url for array %s' % array_info.cinder_id)
    return 'ssh://%s/' % array_info.target


def get_detail_url(array_info):
    LOG.debug('Building url for detail view of %s' % array_info.cinder_id)
    return reverse('horizon:admin:hpe3par_panel:flasharrays:detail',
                   kwargs={'backend_id': array_info.cinder_id})


class HPE3ParFlashArrayTable(tables.DataTable):
    # array_name = tables.WrappingColumn(
    #     'array_name',
    #     verbose_name=_('Array Name'),
    #     link=get_hpe3par_url,
    #     link_attrs={"target": "_blank"}
    # )
    cinder_id = tables.Column(
        'cinder_name',
        verbose_name=_('Cinder Name'),
        link=get_detail_url
    )
    array_name = tables.Column('array_name', verbose_name=_('Array Name'))
    status = tables.Column('status', verbose_name=_('Status'))
    total_volume_count = tables.Column('total_volume_count',
                                       verbose_name=_('Number Of Volumes'))
    total_available = tables.Column('total_available',
                                    verbose_name=_('Total Space'),
                                    filters=[sizeformat.mb_float_format])
    total_used = tables.Column('total_used', verbose_name=_('Used Space'),
                               filters=[sizeformat.mb_float_format])
    data_reduction = tables.Column('data_reduction',
                                   verbose_name=_('Data Reduction'))
    version = tables.Column('version', verbose_name=_('Inform OS Version'))

    class Meta(object):
        name = 'flasharrays'
        verbose_name = _('HPE 3Par Storage FlashArrays')
        table_actions = (HPE3ParFilterAction,)
        multi_select = False
