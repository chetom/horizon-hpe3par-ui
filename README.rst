# horizon-hpe3par-ui
# version = 1.0.0
# by chetom 2023

Installation


git clone https://github.com/chetom/horizon-hpe3par-ui.git
cd horizon-hpe3par-ui
sudo pip install .

cp -rv ./horizon_hpe3par/enabled $HORIZON_DIR/openstack_dashboard/local/
cp -v ./horizon_hpe3par/local_settings.d/_9999_hpe3par_settings.py.example $HORIZON_DIR/openstack_dashboard/local/local_settings.d/_9999_hpe3par_settings.py

Configuration

Modify $HORIZON_DIR/openstack_dashboard/local/local_settings.d/_9999_hpe3par_settings.py to add your Cinder enabled FlashArrays:

HPE3PAR_FLASH_ARRAYS = [
    {
        # Virtual IP address or FQDN for Flash Array
        'wsapi_url': 'https://xx.xx.xx.xx:8080/api/v1',
        'wsapi_user': 'xxxx',
        'wsapi_password': 'xxxx',      
        'ssh_ip': 'xx.xx.xx.xx',
        'ssh_user': 'xxxxx',
        'ssh_password': 'xxxxx',

        # The backend name for the FlashArray, typically this is the value
        # set in the "enabled_backends" section of cinder.conf
        'backend_name': 'yyyyyyyyyy',
    },
    # Repeat for additional arrays
]


Based on:
Pure Storage horizon-pure-ui
some methods from openstack/cinder used in cinder.py 

