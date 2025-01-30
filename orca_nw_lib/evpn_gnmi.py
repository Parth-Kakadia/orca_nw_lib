from .gnmi_util import get_gnmi_path, send_gnmi_get


# EVPN VXLAN tunne info
def get_evpn_vxlan_tunnel_info_from_device(device_ip: str):
    tunnel_path = get_gnmi_path("openconfig-vxlan:vxlan/vxlan-tunnel-infos/vxlan-tunnel-info/state")
    return send_gnmi_get(
        path=[tunnel_path,],
        device_ip=device_ip,
    )

