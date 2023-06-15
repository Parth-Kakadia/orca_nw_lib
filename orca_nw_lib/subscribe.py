from threading import Thread
from orca_nw_lib.gnmi_pb2 import Path, PathElem
from orca_nw_lib.gnmi_util import gnmi_subscribe
from orca_nw_lib.graph_db_utils import getAllInterfacesNameOfDevice
from orca_nw_lib.interfaces import get_intfc_config_path


def subscribe_for_infc_chngs(device_ip: str):
    thread = Thread(
        target=gnmi_subscribe,
        args=(
            device_ip,
            [
                get_intfc_config_path(intfc_name)
                for intfc_name in getAllInterfacesNameOfDevice(device_ip)
            ],
        ),
    )
