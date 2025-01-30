# Copyright (c) 2024 STORDIS GmbH. All rights reserved.
# This code is the property of STORDIS GmbH and can not be redistributed without the written permission of STORDIS GmbH.
from .rest_client import HttpRequest, send_req

def get_bgp_show_info(device_ip: str):
    """Fetch BGP information from the device."""
    url = f"https://{device_ip}/restconf/operations/sonic-bgp-show:show-bgp"
    payload = {
        "sonic-bgp-show:input": {
            "address-family": "IPV4_UNICAST",
            "query-type": "SUMMARY"
        }
    }
    return send_req(HttpRequest.POST, url, payload)

def get_bgp_show_statistics_info(device_ip: str):
    """Fetch BGP statistics information from the device."""
    url = f"https://{device_ip}/restconf/operations/sonic-bgp-show:show-bgp-statistics"
    payload = {
        "sonic-bgp-show:input": {
        "address-family": "IPV4_UNICAST"
    }
    }
    return send_req(HttpRequest.POST, url, payload)
