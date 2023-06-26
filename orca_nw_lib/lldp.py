from orca_nw_lib.interfaces import getInterfaceOfDeviceFromDB
from orca_nw_lib.gnmi_pb2 import Path, PathElem
from orca_nw_lib.gnmi_util import send_gnmi_get
from orca_nw_lib.utils import get_logging

_logger = get_logging().getLogger(__name__)


def getLLDPNeighbors(device_ip: str):
    lldp_json = get_lldp_interfaces_from_device(device_ip)
    neighbors = []
    for intfs in lldp_json.get("openconfig-lldp:interface") or []:
        local_port_name = intfs.get("name")
        if intfs.get("neighbors") or []:
            if not intfs.get("neighbors").get("neighbor"):
                _logger.error(f"Can't find neighbor in {device_ip}:{intfs.get('name')}")

            for nbr in intfs.get("neighbors").get("neighbor") or []:
                nbr_addr = nbr.get("state").get("management-address")
                if not nbr_addr:
                    _logger.error(f"can find neighbor addr in {nbr}")
                nbr_port = nbr.get("state").get("port-id")
                nbr_data = {}
                nbr_data["local_port"] = local_port_name
                nbr_data["nbr_ip"] = nbr_addr.split(",")[0]
                nbr_data["nbr_port"] = nbr_port
                neighbors.append(nbr_data)
    return neighbors


def get_lldp_interfaces_path():
    return Path(
        target="openconfig",
        origin="openconfig-lldp",
        elem=[
            PathElem(
                name="lldp",
            ),
            PathElem(
                name="interfaces",
            ),
            PathElem(
                name="interface",
            ),
        ],
    )


def get_lldp_interfaces_from_device(device_ip: str):
    return send_gnmi_get(device_ip=device_ip, path=[get_lldp_interfaces_path()])


def create_lldp_relations_in_db(topology):
    for device, neighbors in topology.items():
        for nbr in neighbors:
            local_intfc = getInterfaceOfDeviceFromDB(
                device.mgt_ip, nbr.get("local_port")
            )

            nbr_device = nbr.get("nbr_device")
            nbr_intfc = getInterfaceOfDeviceFromDB(
                nbr_device.mgt_ip, nbr.get("nbr_port")
            )
            local_intfc.lldp_neighbour.connect(nbr_intfc)