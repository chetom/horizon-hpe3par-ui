# The config options should align with the entries in cinder.conf

HPE3PAR_FLASH_ARRAYS = [
    {
        # Virtual IP address or FQDN for Flash Array
        'wsapi_url': 'https://xx.xx.xx.xx:8080/api/v1',

        # API Token for FlashArray
        'wsapi_user': 'xxxx',
        'wsapi_password': 'xxxx',
        # The backend name for the FlashArray, typically this is the value
        # set in the "enabled_backends" section of cinder.conf
        'backend_name': '3par-Array-fc',
    },
    # Repeat for additional arrays
]
