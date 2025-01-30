from orca_nw_lib.influxdb_utils import create_point, write_to_influx
from .gnmi_util import get_logging

_logger = get_logging().getLogger(__name__)


def insert_evpn_vxlan_in_influxdb(device_ip: str, evpn_vxlan_info: dict):
    """
    Retrieves evpn vxlan tunnel data and inserts into influx DB.
    
    Args:
        device_ip (str): Device ip of the system.
        evpn_vxlan_info (dict): Dictionary pf key value pairs.
    """

    if not device_ip:
        _logger.error("Device ip is required.")
        return
    
    if not evpn_vxlan_info:
        _logger.error("EVPN VXLAN tunnel dictionary is required.")
        return

    try:
        point = create_point("evpn_vxlan_info") 
        device_ip_pnt = point.tag("device_ip", device_ip)
        device_ip_pnt.field("target", evpn_vxlan_info.get('tunnel_target', "None"))
        device_ip_pnt.field("peer_ip", evpn_vxlan_info.get('tunnel_peer_ip', "None"))
        device_ip_pnt.field("source_ip", evpn_vxlan_info.get('tunnel_source_ip', "None"))
        device_ip_pnt.field("status", evpn_vxlan_info.get('tunnel_status', "None"))
        device_ip_pnt.field("type", evpn_vxlan_info.get('tunnel_type', "None"))
        device_ip_pnt.field("in_octets", int(evpn_vxlan_info.get('in_octets', 0)))
        device_ip_pnt.field("out_octets", int(evpn_vxlan_info.get('out_octets', 0)))
        device_ip_pnt.field("in_pkts", int(evpn_vxlan_info.get('in_pkts', 0)))
        device_ip_pnt.field("out_pkts", int(evpn_vxlan_info.get('out_pkts', 0)))
        device_ip_pnt.field("in_octets_per_second", int(evpn_vxlan_info.get('in_octets_per_second', 0)))
        device_ip_pnt.field("out_octets_per_second", int(evpn_vxlan_info.get('out_octets_per_second', 0)))
        device_ip_pnt.field("in_pkts_per_second", int(evpn_vxlan_info.get('in_pkts_per_second', 0)))
        device_ip_pnt.field("out_pkts_per_second", int(evpn_vxlan_info.get('out_pkts_per_second', 0)))
            
        write_to_influx(point=point)
        _logger.debug("evpn vxlan tunnel info inserted to influxdb %s ",device_ip)
    except Exception as e:
        _logger.error(f"Error instering evpn vxlan tunnel info in influxdb: {e}")



def insert_evpn_in_influxdb(device_ip: str, evpn_info: dict):
    """
    Retrieves evnp data and inserts into influx DB.
    
    Args:
        device_ip (str): Device ip of the system.
        evpn_info (dict): Dictionary pf key value pairs.
    """

    if not device_ip:
        _logger.error("Device ip is required.")
        return
    
    if not evpn_info:
        _logger.error("EVPN dictionary is required.")
        return

    try:
        point = create_point("evpn_info") 
        device_ip_pnt = point.tag("device_ip", device_ip)
        device_ip_pnt.field("l2_vnis", float(evpn_info.get('l2_vnis', 0)))
        device_ip_pnt.field("l3_vnis", float(evpn_info.get('l3_vnis', 0)))
        device_ip_pnt.field("advertise_gateway_mac_ip", evpn_info.get('advertise_gateway_mac_ip', "None"))
        device_ip_pnt.field("advertise_svi_mac_ip", evpn_info.get('advertise_svi_mac_ip', "None"))
        device_ip_pnt.field("advertise_svi_mac", evpn_info.get('advertise_svi_mac', "None"))
        device_ip_pnt.field("duplicate_address_detection", evpn_info.get('duplicate_address_detection', "None"))
        device_ip_pnt.field("detection_max_moves", float(evpn_info.get('detection_max_moves', 0)))
        device_ip_pnt.field("detection_time", float(evpn_info.get('detection_time', 0)))
        device_ip_pnt.field("evpn_mh_mac_holdtime", evpn_info.get('mac_holdtime', "None"))
        device_ip_pnt.field("evpn_mh_df_electiontime", evpn_info.get('df_electiontime', "None"))
        device_ip_pnt.field("evpn_mh_neigh_holdtime", evpn_info.get('neigh_holdtime', "None"))
        device_ip_pnt.field("evpn_mh_es_activation_delay", evpn_info.get('es_activation_delay', "None"))
        device_ip_pnt.field("ipv4_neigh_kernel_threshold", float(evpn_info.get('ipv4_neigh_kernel_threshold', 0)))
        device_ip_pnt.field("ipv6_neigh_kernel_threshold", float(evpn_info.get('ipv6_neigh_kernel_threshold', 0)))
        device_ip_pnt.field("total_ipv4_neighbors", float(evpn_info.get('total_ipv4_neighbors', 0)))
        device_ip_pnt.field("total_ipv6_neighbors", float(evpn_info.get('total_ipv6_neighbors', 0)))
        
        write_to_influx(point=point)
        _logger.debug("evpn info inserted to influxdb %s ",device_ip)
    except Exception as e:
        _logger.error(f"Error instering evpn info in influxdb: {e}")





def insert_evpn_vni_in_influxdb(device_ip: str, evpn_vni_info: dict):
    """
    Retrieves evpn vni data and inserts into influx DB.
    
    Args:
        device_ip (str): Device ip of the system.
        evpn_vni_info (dict): Dictionary pf key value pairs.
    """

    if not device_ip:
        _logger.error("Device ip is required.")
        return
    
    if not evpn_vni_info:
        _logger.error("EVPN vni dictionary is required.")
        return
    
    try:
        vnis = evpn_vni_info.get('vnis', [])
        point = create_point("evpn_vni_info")
        device_ip_pnt = point.tag("device_ip", device_ip)
        for vni in vnis or []:
            vni_pnt = device_ip_pnt.tag("vni", vni['vni'])
            if vni['type'] == 'L2':
                vni_pnt.field("vni_id", vni["vni"])
                vni_pnt.field("type", vni["type"])
                vni_pnt.field("tenant_vrf", vni["tenant_vrf"])
                vni_pnt.field("client_state", vni["client_state"])
                vni_pnt.field("vxlan_interface", vni["vxlan_interface"])
                vni_pnt.field("vxlan_ifindex", vni["vxlan_ifindex"])
                vni_pnt.field("svi_interface", vni["svi_interface"])
                vni_pnt.field("svi_ifindex", vni["svi_ifindex"])
                vni_pnt.field("local_vtep_ip", vni["local_vtep_ip"])
                vni_pnt.field("local_external_vtep_ip", vni["local_external_vtep_ip"])
                vni_pnt.field("vxlan_external_interface", vni["vxlan_external_interface"])
                vni_pnt.field("mcast_group", vni["mcast_group"])
                vni_pnt.field("no_remote_vteps_known_for_this_vni", vni["no_remote_vteps_known_for_this_vni"])
                vni_pnt.field("number_of_macs_(local_and_remote)_known_for_this_vni", vni["number_of_macs_(local_and_remote)_known_for_this_vni"])
                vni_pnt.field("number_of_arps_(ipv4_and_ipv6,_local_and_remote)_known_for_this_vni", vni["number_of_arps_(ipv4_and_ipv6,_local_and_remote)_known_for_this_vni"])
                vni_pnt.field("advertise_gw_macip", vni["advertise_gw_macip"])
                vni_pnt.field("advertise_svi_macip", vni["advertise_svi_macip"])

            elif vni['type'] == 'L3':
                vni_pnt.field("vni_id", vni["vni"])
                vni_pnt.field("type", vni["type"])
                vni_pnt.field("tenant_vrf", vni["tenant_vrf"])
                vni_pnt.field("local_vtep_ip", vni["local_vtep_ip"])
                vni_pnt.field("local_external_vtep_ip", vni["local_external_vtep_ip"])
                vni_pnt.field("vxlan_interface", vni["vxlan_intf"])
                vni_pnt.field("svi_interface", vni["svi_if"])
                vni_pnt.field("client_state", vni["client_state"])
                vni_pnt.field("state", vni["state"])
                vni_pnt.field("vni_filter", vni["vni_filter"])
                vni_pnt.field("system_mac", vni["system_mac"])
                vni_pnt.field("router_mac", vni["router_mac"])
                vni_pnt.field("l2_vnis", vni["l2_vnis"])
            
            write_to_influx(point=point)
        _logger.debug("evpn vni info inserted to influxdb %s ",device_ip)
    except Exception as e:
        _logger.error(f"Error instering evpn vni info in influxdb: {e}")