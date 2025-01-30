import json
from orca_nw_lib.rest_client import HttpRequest, send_req, do_json_syntax_correction
from orca_nw_lib.utils import get_logging


_logger=logger = get_logging().getLogger(__name__)


def get_evpn_details_rest(ip_addr: str) -> dict:
    """
    Create a evpn details dictionary based on the given IP address.

    Args:
        ip_addr (str): The IP address of the device.

    Returns:
        dict: A dictionary containing device evpn details.
    """
    
    url = f"https://{ip_addr}/restconf/operations/sonic-bgp-show:show-bgp-evpn"
    req_body={"sonic-bgp-show:input": {"cmd": "show evpn"}}

    try:
        resp = send_req(HttpRequest.POST, url, req_body)
        if resp:
            info = parse_bgp_show_response(json.loads(resp.text))
            if not info:
                return info
            detection = ""
            for key in info.keys():
                if key.startswith("detection"):
                    detection = key
            detection_key = detection.split(",")
            max_moves_n = detection_key[0].split("_")[-1]
            time_n = detection_key[1].split("_")[-1]
            detection_max_moves = int(max_moves_n) if max_moves_n.isdigit() else 0
            detection_time = int(time_n) if time_n.isdigit() else 0
            
            evpnmh1 = info['mac_holdtime'].split(",")
            evpnmh2 = info['df_electiontime'].split(",")

            evpn_mh_mac_holdtime = evpnmh1[0]
            evpn_mh_df_electiontime = evpnmh2[0]
            evpn_mh_neigh_holdtime = evpnmh1[1].split(" ")[-1]
            evpn_mh_es_activation_delay = evpnmh2[1].split(" ")[-1]
            
            info.update({
                "detection_max_moves": detection_max_moves,
                "detection_time": detection_time,
                "mac_holdtime": evpn_mh_mac_holdtime,
                "df_electiontime": evpn_mh_df_electiontime,
                "neigh_holdtime": evpn_mh_neigh_holdtime,
                "es_activation_delay": evpn_mh_es_activation_delay
            })

            info.pop("detection_max_moves_5,_time_180", None)
            return(info) 
        else:
            _logger.debug('REST Call response for evpn is None: ', resp)
    except Exception as e:
        _logger.error(f"Error getting sonic-bgp-show evpn data: {e}")



def get_evpn_vni_detail_rest(ip_addr: str) -> dict:
    """
    Create a evpn vni details dictionary based on the given IP address.

    Args:
        ip_addr (str): The IP address of the device.

    Returns:
        dict: A dictionary containing device evpn vni details.
    """
    
    url = f"https://{ip_addr}/restconf/operations/sonic-bgp-show:show-bgp-evpn"
    req_body={"sonic-bgp-show:input": {"cmd": "show evpn vni detail"}}

    try:
        resp = send_req(HttpRequest.POST, url, req_body)
        if resp:
            info = parse_bgp_show_response(json.loads(resp.text))
            if not info:
                return info
            return info
        else:
            _logger.debug('Response body for evpn vni ', resp)
            return
    except Exception as e:
        _logger.error(f"Error getting sonic-bgp-show evpn vni data: {e}")



def get_l2vpn_evpn_route_detail_rest(ip_addr: str) -> dict:
    """
    Create a l2vpn evpn route details dictionary based on the given IP address.

    Args:
        ip_addr (str): The IP address of the device.

    Returns:
        dict: A dictionary containing device l2vpn evpn route details.
    """
    
    url = f"https://{ip_addr}:8080/restconf/operations/sonic-bgp-show:show-bgp-evpn"
    req_body = {"sonic-bgp-show:input": {"cmd": "show bgp l2vpn evpn route"}}

    try:
        resp = send_req(HttpRequest.POST, url, req_body)
        if resp is not None:
            info = parse_bgp_show_response(json.loads(resp.text))
            return(info)
        else:
            print('Response body for sonic-bgp-show: ', resp)
            _logger.debug('Response body for sonic-bgp-show: ', resp)
            return
    except Exception as e:
        _logger.error(f"Error getting sonic-bgp-show evpn route data: {e}")




# JSON formater for EVPN
def parse_bgp_show_response(response) -> dict:
    response_str = response.get("sonic-bgp-show:output", {}).get("response", "")
    if not response_str:
        return {}
    lines = response_str.split('\n')

    general_info = {}
    vnis = []
    current_vni = None

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        if stripped_line.lower().startswith('vni:'):
            if current_vni is not None:
                vnis.append(current_vni)
            current_vni = {}
            key, value = split_line(stripped_line)
            current_vni[key] = value
        else:
            key, value = split_line(stripped_line)
            if current_vni is not None:
                current_vni[key] = value
            else:
                general_info[key] = value

    if current_vni is not None:
        vnis.append(current_vni)

    output = {**general_info, "vnis": vnis}
    return output


def split_line(line):
        parts = line.split(':', 1)
        key_part = parts[0].strip()
        value_part = parts[1].strip() if len(parts) > 1 else ''
        key = key_part.lower().replace(' ', '_').replace('-', '_')
        return key, value_part