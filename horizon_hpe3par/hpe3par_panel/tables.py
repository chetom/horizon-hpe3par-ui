from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
import logging

from horizon import tables
from horizon.templatetags import sizeformat

LOG = logging.getLogger(__name__)


class HPE3ParFilterAction(tables.FilterAction):
    name = "hpe3parfilter"


def get_hpe3par_url(array_info):
    LOG.debug('Building url for array %s' % array_info.cinder_id)
    return 'https://%s/' % array_info.target


def get_detail_url(array_info):
    LOG.debug('Building url for detail view of %s' % array_info.cinder_id)
    return reverse('horizon:admin:hpe3par_panel:flasharrays:detail',
                   kwargs={'backend_id': array_info.cinder_id})


class HPE3ParFlashArrayTable(tables.DataTable):
    array_name = tables.WrappingColumn(
        'array_name',
        verbose_name=_('Array Name'),
        link=get_hpe3par_url,
        link_attrs={"target": "_blank"}
    )
    cinder_id = tables.Column(
        'cinder_name',
        verbose_name=_('Cinder Name'),
        link=get_detail_url
    )
    status = tables.Column('status', verbose_name=_('Status'))
    version = tables.Column('version', verbose_name=_('Inform OS Version'))

    class Meta(object):
        name = 'flasharrays'
        verbose_name = _('HPE 3Par Storage FlashArrays')
        table_actions = (HPE3ParFilterAction,)
        multi_select = False
