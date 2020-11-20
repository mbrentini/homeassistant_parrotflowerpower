# homeassistant_parrotflowerpower
Parrot Flower Power BLE sensor integration for Home Assistant

Usage : 
- Copy folder "parrotflowerpower" to /config
- Edit configuration.yaml by adding :

```yaml
sensor:
  - platform: parrotflowerpower
    mac: 'A0:14:3D:xx:xx:xx'
    name: "Flower Power xxxx"
    scan_interval: 1800
```

- Reboot Home Assistant

Values for config :
```yaml
mac: the MAC address of the sensor
name: the name of the sensor
scan_interval: refresh interval in seconds (e.g. 1800 = every 30 mn)
```
