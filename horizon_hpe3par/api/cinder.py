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


import uuid
import base64
import binascii

from openstack_dashboard.api import cinder


class HPE3ParVolume(cinder.Volume):
    _hpe3par_attrs = [
        'array_name',
        'vv_name',
    ]

    def __init__(self, apiresource):
        super(HPE3ParVolume, self).__init__(apiresource)
        self._attrs = self._attrs + self._hpe3par_attrs

    @staticmethod
    def find_name(name: str):
        uuid_str = name.replace("-", "")
        vol_uuid = uuid.UUID('urn:uuid:%s' % uuid_str)
        vol_encoded = HPE3ParVolume.encode_as_text(vol_uuid.bytes)    
        # 3par doesn't allow +, nor /
        vol_encoded = vol_encoded.replace('+', '.')
        vol_encoded = vol_encoded.replace('/', '-')
        # strip off the == as 3par doesn't like those.
        vol_encoded = vol_encoded.replace('=', '')
        return vol_encoded

    @staticmethod
    def encode_as_bytes(s, encoding='utf-8'):
        """Encode a string using Base64.

        If *s* is a text string, first encode it to *encoding* (UTF-8 by default).

        :param s: bytes or text string to be encoded
        :param encoding: encoding used to encode *s* if it's a text string
        :returns: Base64 encoded byte string (bytes)

        Use encode_as_text() to get the Base64 encoded string as text.
        """
        if isinstance(s, str):
            s = s.encode(encoding)
        return base64.b64encode(s)


    @staticmethod
    def encode_as_text(s, encoding='utf-8'):
        """Encode a string using Base64.

        If *s* is a text string, first encode it to *encoding* (UTF-8 by default).

        :param s: bytes or text string to be encoded
        :param encoding: encoding used to encode *s* if it's a text string
        :returns: Base64 encoded text string (Unicode)

        Use encode_as_bytes() to get the Base64 encoded string as bytes.
        """
        encoded = HPE3ParVolume.encode_as_bytes(s, encoding=encoding)
        return encoded.decode('ascii')

    @staticmethod
    def decode_as_bytes(encoded):
        """Decode a Base64 encoded string.

        :param encoded: bytes or text Base64 encoded string to be decoded
        :returns: decoded bytes string (bytes)

        Use decode_as_text() to get the decoded string as text.

        A TypeError is raised if the input is invalid (or incorrectly padded).
        """
        if isinstance(encoded, bytes):
            encoded = encoded.decode('ascii')
        try:
            return base64.b64decode(encoded)
        except binascii.Error as e:
            # Transform this exception for consistency.
            raise TypeError(str(e))

    @staticmethod
    def decode_as_text(encoded, encoding='utf-8'):
        """Decode a Base64 encoded string.

        Decode the Base64 string and then decode the result from *encoding*
        (UTF-8 by default).

        :param encoded: bytes or text Base64 encoded string to be decoded
        :returns: decoded text string (bytes)

        Use decode_as_bytes() to get the decoded string as bytes.
        """
        decoded = HPE3ParVolume.decode_as_bytes(encoded)
        return decoded.decode(encoding)
