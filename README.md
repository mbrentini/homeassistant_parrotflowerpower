# Parrot Flower Power BLE sensor integration for Home Assistant

It's sketchy but it works.

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

Values for config :
```yaml
mac: the MAC address of the sensor
name: the name of the sensor
scan_interval: refresh interval in seconds (e.g. 1800 = every 30 mn)
```

- Reboot Home Assistant
- Check sensor values under Developer Tools section
- You can also add a plant into configuration.yaml, as described here : https://www.home-assistant.io/integrations/plant/

Useful and used resources :
- https://www.home-assistant.io/integrations/miflora/
- https://github.com/sandeepmistry/node-flower-power
- https://forum.developer.parrot.com/t/simple-read-of-moisture-levels-via-cron-job-to-text-file/1599
- https://github.com/BuBuaBu/flower-power-history/blob/master/index.js
- https://www.fanjoe.be/?p=3520
