from orca_nw_lib.influxdb_utils import create_point, write_to_influx
from .gnmi_util import get_logging
import json

_logger = get_logging().getLogger(__name__)

def list_to_string(obj_list):
    """Helper function to convert object list to a comma-separated string."""
    return ', '.join(str(obj) for obj in obj_list)

# GET function that inserts the bgp data into influxdb
def insert_bgp_in_influxdb(device_ip: str, bgp_global_list: dict):
    """
    Retrieves discovered bgd data and inserts into influx DB.
    
    Args:
        device_ip (str): Object of type Device.
        bgp (dict): Dictionary pf key value pairs.
    """
    if not device_ip:
        _logger.error("Device object is required.")
        return
    
    if not bgp_global_list:
        _logger.error("BGP dictionary is required.")
        return
    
    try:
        point = create_point("discovered_bgp").tag("device_ip", device_ip)
        
        for bgp, family in bgp_global_list.items():
            # Adding basic BGP fields
            point.field("local_asn", int(bgp.local_asn))
            point.field("vrf_name", bgp.vrf_name)
            point.field("router_id", bgp.router_id)

            # Adding additional fields
            point.field("always_compare_med", bgp.always_compare_med)
            point.field("ebgp_requires_policy", bgp.ebgp_requires_policy)
            point.field("external_compare_router_id", bgp.external_compare_router_id)
            point.field("fast_external_failover", bgp.fast_external_failover)
            point.field("holdtime", int(bgp.holdtime))
            point.field("ignore_as_path_length", bgp.ignore_as_path_length)
            point.field("keepalive", int(bgp.keepalive))
            point.field("load_balance_mp_relax", bgp.load_balance_mp_relax)
            point.field("log_nbr_state_changes", bgp.log_nbr_state_changes)
            point.field("network_import_check", bgp.network_import_check)

            # Adding address families
            af_list = list_to_string(family.get("af", []))
            point.field("af", af_list)

            af_network_list = list_to_string(family.get("af_network", []))
            point.field("af_network", af_network_list)

            af_aggregate_addr_list = list_to_string(family.get("af_aggregate_addr", []))
            point.field("af_aggregate_addr", af_aggregate_addr_list)

            write_to_influx(point=point)
        _logger.info("BGP Global data sent to InfluxDB Successfully...")
    except Exception as e:
        _logger.error(f"Error instering in influxdb: {e}")




# GET function that inserts the bgp neighbours into influxdb
def insert_bgp_neighbor_in_influxdb(device_ip: str, bgp_neighbor_list: dict):
    """
    Retrieves discovered bgd neighbour and inserts into influx DB.
    
    Args:
        device_ip (str): Object of type Device.
        bgp (dict): Dictionary pf key value pairs.
    """

    if not device_ip:
        _logger.error("Device object is required.")
        return
    
    if not bgp_neighbor_list:
        _logger.error("BGP Neighbor dictionary is required.")
        return
    
    try:
        # Create the InfluxDB point
        point = create_point("discovered_bgp_neighbor")
        device_pnt = point.tag("device_ip", device_ip)
        
        # Iterate over the BGP neighbors in the list
        for bgp_neighbor, family in bgp_neighbor_list.items():
            # Add fields for BGP neighbor details, checking for None before converting
            admin_status = bgp_neighbor.admin_status if bgp_neighbor.admin_status is not None else False
            device_pnt.field("bn_admin_status", admin_status)
            
            local_asn = bgp_neighbor.local_asn if bgp_neighbor.local_asn is not None else 0
            device_pnt.field("bn_local_asn", int(local_asn))  # Ensure this is cast to int
            
            vrf_name = bgp_neighbor.vrf_name if bgp_neighbor.vrf_name is not None else ""
            device_pnt.field("bn_vrf_name", str(vrf_name))
            
            neighbor_ip = bgp_neighbor.neighbor_ip if bgp_neighbor.neighbor_ip is not None else ""
            device_pnt.field("bn_neighbor_ip", str(neighbor_ip))
            
            remote_asn = bgp_neighbor.remote_asn if bgp_neighbor.remote_asn is not None else 0
            device_pnt.field("bn_remote_asn", int(remote_asn))  # Ensure this is cast to int

            # Extract and format the AF list details
            af_list = family.get("neighbor_af", [])
            af_details = [f"{af.afi_safi}_{af.admin_status}" for af in af_list]  # Format as 'afi_safi_admin_status'
            af_str = list_to_string(af_details)  # Convert list to comma-separated string
            device_pnt.field("af", af_str)

            #Write the point to InfluxDB
            write_to_influx(point=point)
        _logger.info("BGP Neighbor data sent to InfluxDB Successfully...")
    except Exception as e:
        _logger.error(f"Error inserting into InfluxDB: {e}")


def insert_bgp_show_in_influxdb(device_ip: str, bgp_show_data: dict):
    """
    Inserts BGP show data into InfluxDB.

    Args:
        device_ip (str): The IP address of the device.
        bgp_show_data (dict): A dictionary containing BGP show information.

    Returns:
        None
    """
    if not device_ip:
        _logger.error("Device IP is required.")
        return

    if not bgp_show_data:
        _logger.error("BGP show data is required.")
        return

    try:
        # Create the main InfluxDB point
        point = create_point("discovered_bgp_show")
        device_ip_point = point.tag("device_ip", device_ip)

        # Insert general BGP data fields
        point.field("local_as", bgp_show_data.get("local_as"))
        point.field("router_id", bgp_show_data.get("router_id"))
        point.field("total_peers", bgp_show_data.get("total_peers"))
        point.field("peers_up", bgp_show_data.get("peers_up"))
        point.field("rib_count", bgp_show_data.get("rib_count"))
        point.field("rib_memory", bgp_show_data.get("rib_memory"))
        point.field("table_version", bgp_show_data.get("table_version"))
        point.field("vrf_id", bgp_show_data.get("vrf_id"))
        point.field("vrf_name", bgp_show_data.get("vrf_name"))
        write_to_influx(point=point)  # Write the general data first

        # Iterate through peers (list)
        for peer in bgp_show_data.get("peers", []):
            peer_ip = peer.get("peer_ip")
            if not peer_ip:
                _logger.warning("Peer IP missing, skipping entry.")
                continue

            peer_point = device_ip_point.tag("peer_ip", peer_ip)
            peer_point.field("remote_as", peer.get("remote_as"))
            peer_point.field("state", peer.get("state"))
            peer_point.field("connections_dropped", peer.get("connections_dropped"))
            peer_point.field("connections_established", peer.get("connections_established"))
            peer_point.field("messages_received", peer.get("messages_received"))
            peer_point.field("messages_sent", peer.get("messages_sent"))
            peer_point.field("uptime", peer.get("uptime"))
            peer_point.field("prefixes_received", peer.get("prefixes_received"))
            peer_point.field("prefixes_sent", peer.get("prefixes_sent"))
            peer_point.field("id_type", peer.get("id_type"))
            peer_point.field("input_queue", peer.get("input_queue"))
            peer_point.field("local_as", peer.get("local_as"))
            peer_point.field("output_queue", peer.get("output_queue"))
            peer_point.field("peer_uptime_epoch", peer.get("peer_uptime_epoch"))
            peer_point.field("peer_uptime_msec", peer.get("peer_uptime_msec"))
            peer_point.field("table_version", peer.get("table_version"))
            peer_point.field("version", peer.get("version"))
            write_to_influx(point=peer_point)
        _logger.info("BGP Show data successfully sent to InfluxDB.")
    except Exception as e:
        _logger.error(f"Error inserting BGP show data into InfluxDB: {e}")

def insert_bgp_statistics_in_influxdb(device_ip: str, bgp_statistics_list: dict):
    """
    Inserts BGP statistics data into InfluxDB.

    Args:
        device_ip (str): The IP address of the device.
        bgp_statistics_list (dict or str): A dictionary or JSON string containing BGP statistics.

    Returns:
        None
    """
    if isinstance(bgp_statistics_list, str):
        try:
            bgp_statistics_list = json.loads(bgp_statistics_list)  # Convert JSON string to dictionary
        except json.JSONDecodeError as e:
            _logger.error(f"Error decoding JSON string: {e}")
            return

    if not device_ip:
        _logger.error("Device IP is required.")
        return

    if not bgp_statistics_list:
        _logger.error("BGP statistics data is required.")
        return

    try:
        # Create the main InfluxDB point
        point = create_point("discovered_bgp_statistics")
        point.tag("device_ip", device_ip)

        # Insert fields from the IPv4 Unicast data
        for ipv4_data in bgp_statistics_list.get("ipv4Unicast", []):
            point = point.tag("instance", ipv4_data.get("instance"))  # New tag added
            point.field("instance", ipv4_data.get("instance"))
            point.field("max_prefix_len", float(ipv4_data.get("maxPrefixLen", 0)))
            point.field("total_advertisements", int(ipv4_data.get("totalAdvertisements", 0)))
            point.field("total_prefixes", int(ipv4_data.get("totalPrefixes", 0)))
            point.field("average_prefix_len", float(ipv4_data.get("averagePrefixLen", 0)))
            point.field("unaggr_prefixes", int(ipv4_data.get("unaggrPrefixes", 0)))
            point.field("aggr_advertisements", int(ipv4_data.get("aggrAdvertisements", 0)))
            point.field("addr_space_advertised", int(ipv4_data.get("addrSpaceAdvertised", 0)))
            point.field("addr_space_advertised_percent", float(ipv4_data.get("addrSpaceAdvertisedPercent", 0.0)))
            point.field("highest_asn", int(ipv4_data.get("highestAsn", 0)))
            point.field("max_aggr_prefixes", int(ipv4_data.get("maxAggrPrefixes", 0)))
            point.field("addr_space_advertised_len_8_eq", float(ipv4_data.get("addrSpaceAdvertisedLen8eq", 0.0)))
            point.field("addr_space_advertised_len_24_eq", float(ipv4_data.get("addrSpaceAdvertisedLen24eq", 0.0)))
            point.field("aspath_count", int(ipv4_data.get("aspathCount", 0)))
            point.field("max_aspath_hops", int(ipv4_data.get("maxAspathHops", 0)))
            point.field("average_aspath_length", float(ipv4_data.get("averageAspathLength", 0.0)))
            point.field("max_aspath_size", int(ipv4_data.get("maxAspathSize", 0)))
            point.field("average_aspath_size", float(ipv4_data.get("averageAspathSize", 0.0)))

            # Write to InfluxDB
            write_to_influx(point=point)
        _logger.info("BGP statistics data successfully sent to InfluxDB.")
    except Exception as e:
        _logger.error(f"Error inserting BGP statistics data into InfluxDB: {e}")

