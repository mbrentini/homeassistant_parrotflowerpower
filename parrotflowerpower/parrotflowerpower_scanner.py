from bleak import BleakClient, BleakScanner

from .const import DOMAIN, LOGGER

"""Scan for Parrot Flower Power plant devices."""
DEVICE_PREFIX = ('A0:14:3D','90:03:B7')

def scan(backend, timeout=10):
    """Scan for Parrot Flower Power devices.
    Note: this must be run as root!
    """
    result = []
    for (mac) in backend.scan_for_devices(timeout):
        if mac is not None and mac.upper().startswith(DEVICE_PREFIX):
            result.append(mac.upper())
    return result

async def discover():
    """Discover Bluetooth LE devices."""
    devices = await BleakScanner.discover()
    LOGGER.debug("Discovered devices: %s", [{"address": device.address, "name": device.name} for device in devices])
    return [device for device in devices if device.address.upper().startswith(DEVICE_PREFIX)]