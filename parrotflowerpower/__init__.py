"""Parrot Flower Power BLE plant sensor integration"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_MAC

from .const import DOMAIN

PLATFORMS = ["parrotflowerpower", "sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Parrot Flower Power from a config entry."""
    instance = ParrotFlowerPowerInstance(entry.data[CONF_MAC])
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = instance
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unload_ok
    
class ParrotFlowerPowerInstance:
    def __init__(self, mac: str) -> None:
        self._mac = CONF_MAC

    @property
    def mac(self):
        return self._mac