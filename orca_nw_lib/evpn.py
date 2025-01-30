import json
from orca_nw_lib.evpn_gnmi import get_evpn_vxlan_tunnel_info_from_device
from orca_nw_lib.evpn_influxdb import insert_evpn_in_influxdb, insert_evpn_vni_in_influxdb, insert_evpn_vxlan_in_influxdb
from orca_nw_lib.evpn_rest import get_evpn_details_rest, get_evpn_vni_detail_rest
from orca_nw_lib.utils import get_logging, get_telemetry_db

_logger=logger = get_logging().getLogger(__name__)

def get_vxlan_details(ip_addr: str) -> dict:
    """
    Create a evpn details dictionary based on the given IP address.

    Args:
        ip_addr (str): The IP address of the device.

    Returns:
        dict: A dictionary containing device evpn vxlan details.
    """
    
    vxlan_data = get_evpn_vxlan_tunnel_info_from_device(ip_addr)
   
    vxlan_details = {}

    tunnel_stats = vxlan_data.get('statistics', {})
    vxlan_details.update({
        "tunnel_target": vxlan_data.get('target', "None"),
        "tunnel_peer_ip": vxlan_data.get('peer-ip', "None"),
        "tunnel_source_ip": vxlan_data.get('source-ip', "None"),
        "tunnel_status": vxlan_data.get('status', "None"),
        "tunnel_type": vxlan_data.get('type', "None"),
        "in_octets": int(tunnel_stats.get('in-octets', 0)),
        "out_octets": int(tunnel_stats.get('out-octets', 0)),
        "in_pkts": int(tunnel_stats.get('in-pkts', 0)),
        "out_pkts": int(tunnel_stats.get('out-pkts', 0)),
        "in_octets_per_second": int(tunnel_stats.get('in-octets-per-second', 0)),
        "out_octets_per_second": int(tunnel_stats.get('out-octets-per-second', 0)),
        "in_pkts_per_second": int(tunnel_stats.get('in-pkts-per-second', 0)),
        "out_pkts_per_second": int(tunnel_stats.get('out-pkts-per-second', 0)),
    })
    
    return vxlan_details



def discover_evpn(device_ip:str):
    """
    Discover a EVPN by its IP address and insert the evpn details into the database.

    Args:
        device_ip (str): The IP address of the device to be discovered.

    Raises:
        Exception: If an error occurs during the discovery process.
    """
    _logger.debug("Discovering device with IP: %s", device_ip)
    try:
        _logger.info("Discovering EVPN with IP: %s", device_ip)
        vxlan_data = get_vxlan_details(device_ip)
        evpn_data = get_evpn_details_rest(device_ip)
        vni_data = get_evpn_vni_detail_rest(device_ip)

        ## Check if the telemetry DB is influxdb or prometheus for inserting device info.
        if get_telemetry_db() == "influxdb":
            insert_evpn_vxlan_in_influxdb(device_ip, vxlan_data)
            if evpn_data:
                insert_evpn_in_influxdb(device_ip, evpn_data)
            if vni_data:
                insert_evpn_vni_in_influxdb(device_ip, vni_data)
        elif get_telemetry_db() == "prometheus":
            pass
        else:
            _logger.debug("Telemetry DB not configured, skipping evpn info insertion for IP: %s", device_ip)

    except Exception as e:
        _logger.error("Error discovering device with IP %s: %s", device_ip, str(e))
        raise