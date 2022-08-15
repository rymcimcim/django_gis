import ipaddress
from typing import Union

from geolocations.models import IPTypes


def is_ip_address(input: str) -> Union[bool, tuple[bool, int]]:
    try:
        network = ipaddress.ip_network(input)
    except ValueError:
        ret = False
    else:
        ret = (True, getattr(IPTypes, f"IPV{network.version}").value)
    return ret
