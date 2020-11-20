"""Scan for Parrot Flower Power plant devices."""
DEVICE_PREFIX = 'A0:14:3D:'

def scan(backend, timeout=10):
    """Scan for Parrot Flower Power devices.
    Note: this must be run as root!
    """
    result = []
    for (mac) in backend.scan_for_devices(timeout):
        if mac is not None and mac.upper().startswith(DEVICE_PREFIX):
            result.append(mac.upper())
    return result
