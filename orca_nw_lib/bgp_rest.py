# Copyright (c) 2024 STORDIS GmbH. All rights reserved.
# This code is the property of STORDIS GmbH and can not be redistributed without the written permission of STORDIS GmbH.
from enum import Enum
import base64
import json

from orca_nw_lib.utils import get_logging

_logger = get_logging().getLogger(__name__)

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
 
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

####
username = "admin"
password = "YourPaSsWoRd"
 
auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = {
    "Authorization": f"Basic {auth_string}",
    "Content-Type": "application/yang-data+json",
}
 
## Enum for http requests
class HttpRequest(Enum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"
 
 
def send_req(req: HttpRequest, resource_url, req_body=None, timeout_sec=5):
    response = None
    switch_case = {
        HttpRequest.GET: requests.get,
        HttpRequest.PUT: requests.put,
        HttpRequest.POST: requests.post,
        HttpRequest.PATCH: requests.patch,
        HttpRequest.DELETE: requests.delete,
    }
    try:
        response = switch_case.get(
            req, lambda: _logger.error("Invalid request type: {0}".format(req))
        )(
            resource_url,
            verify=False,
            headers=headers,
            json=req_body,
            timeout=timeout_sec,
        )
    except requests.exceptions.Timeout as e:
        _logger.error(e)
    except requests.exceptions.RequestException as e:
        _logger.error(e)
    # parse resource_url and print only the IP
    ip = resource_url.split("/")[2]
    _logger.info(f"{req} Request sent to {ip}")
    if response != None:
        _logger.info(f"{req} Response Status Code: {response.status_code}:{response.reason}")
        (
            _logger.info(json.dumps(response.json(), indent=4))
            if response.text
            else _logger.error("no output")
        )
    return response
 


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




def do_json_syntax_correction(json_text):
    return (
        json_text.replace(" ", "")
        .replace("\\n", "")
        .replace('\\"', '"')
        .replace('\\"', '"')
        .replace(':"{', ":{")
        .replace('}"}}', "}]}}")
        .replace("}{", "},{")
        .replace('"response":', '"response":[')
    )

# # Payload for the show-bgp operation
# payload = {
#     "sonic-bgp-show:input": {
#         "address-family": "IPV4_UNICAST",
#         "query-type": "SUMMARY"
#     }
# }

# #For 1 path
# # Path for the RESTCONF operation
# path = "/restconf/operations/sonic-bgp-show:show-bgp"

# # Send request to each device
# for device_ip in device_ip_list:
#     url = f"https://{device_ip}{path}"
#     response = send_req(HttpRequest.POST, url, req_body=payload)





# ## For 2 paths
# # # Define API paths and payloads
# api_calls = [
#     {
#         "path": "/restconf/operations/sonic-bgp-show:show-bgp",
#         "payload": {
#             "sonic-bgp-show:input": {
#                 "address-family": "IPV4_UNICAST",
#                 "query-type": "SUMMARY"
#             }
#         },
#     },
#     {
#         "path": "/restconf/operations/sonic-bgp-show:show-bgp-statistics",
#         "payload": {
#             "sonic-bgp-show:input": {
#                 "address-family": "IPV4_UNICAST"
#             }
#         },
#     },
# ]

# # Iterate through devices and make API calls
# for device_ip in device_ip_list:
#     for api_call in api_calls:
#         resource_url = f"https://{device_ip}{api_call['path']}"
#         print(f"Making request to {resource_url} with payload: {api_call['payload']}")
#         send_req(HttpRequest.POST, resource_url, req_body=api_call["payload"])
