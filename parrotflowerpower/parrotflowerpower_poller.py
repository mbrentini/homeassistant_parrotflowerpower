"""Fecthes data from Parrot Flower Power plant devices."""

from datetime import datetime, timedelta
from struct import unpack
import logging
import math
from threading import Lock
from btlewrap.base import BluetoothInterface, BluetoothBackendException

HANDLES = [
    ["battery", 0x004c],
    ["name", 0x0003],
    ["light", 0x0025],
    ["light_int", 0x0025],
    ["conductivity", 0x0029],
    ["soil_temperature", 0x002d],
    ["air_temperature", 0x0031],
    ["moisture", 0x0035],
    ["moisture_cal", 0x003f],
    ["led", 0x003c]
]

_LOGGER = logging.getLogger(__name__)

class ParrotFlowerPowerPoller(object):
    """"
    A class to read data from Parrot Flower Power plant sensors.
    """

    def __init__(self, mac, backend, cache_timeout=600, retries=3, adapter='hci0'):
        """
        Initialize a Parrot Flower Power Poller for the given MAC address.
        """

        self._mac = mac
        self._bt_interface = BluetoothInterface(backend, adapter=adapter)
        self._cache = None
        self._cache_timeout = timedelta(seconds=cache_timeout)
        self._last_read = None
        self._fw_last_read = None
        self.retries = retries
        self.ble_timeout = 30
        self.lock = Lock()

    
    def name(self):
        """Return the name of the sensor."""
        with self._bt_interface.connect(self._mac) as connection:
            name = connection.read_handle(_HANDLE_READ_NAME)  # pylint: disable=no-member

        if not name:
            raise BluetoothBackendException("Could not read data from Parrot Flower Power sensor %s" % self._mac)
        return ''.join(chr(n) for n in name)

    
    def battery_level(self):
        """Return the battery level.

        The battery level is updated when reading the firmware version. This
        is done only once every 24h
        """
        
        with self._bt_interface.connect(self._mac) as connection:
            data = connection.read_handle(_HANDLE_READ_VERSION_BATTERY)
            _LOGGER.info('Received result for handle %s: %s',
                          _HANDLE_READ_VERSION_BATTERY, self._format_bytes(data))
            rawValue = int.from_bytes(data, byteorder='little')
            battery = rawValue * 1.0
        
        return battery

    
    def fill_cache(self):
        """Fill the cache with new data from the sensor."""
        self._cache = dict()
        _LOGGER.info('Filling cache with new sensor data for device %s.', self._mac)
        try:
            with self._bt_interface.connect(self._mac) as connection:

                for handle in HANDLES:
                    data2read = handle[0]
                    data = connection.read_handle(handle[1])
                    _LOGGER.info('Received result for %s(%x): %s',
                              data2read, handle[1], self._format_bytes(data))
                    
                    if len(data) <= 2:
                        rawValue = int.from_bytes(data, byteorder='little')
                    elif len(data) == 4:
                        rawValue = unpack('<f',  data )[0]
                    else:
                        rawValue = data
                    _LOGGER.info('Rawdata for %s: %s', data2read, rawValue)

                    if data2read == "light":
                        if rawValue == 65535:
                            value2report = 0
                        else:
                            value2report = 80000000 * (math.pow(rawValue, -1.063)) # from https://www.fanjoe.be/?p=3520
                            #value2report = 0.08640000000000001 * (192773.17000000001 * math.pow(rawValue, -1.0606619))
                    elif data2read in ["soil_temperature", "air_temperature"]:
                        value2report = 0.00000003044 * math.pow(rawValue, 3.0) - 0.00008038 * math.pow(rawValue, 2.0) + rawValue * 0.1149 - 30.449999999999999
                        if value2report < -10.0:
                            value2report = -10.0
                        elif value2report > 55.0:
                            value2report = 55.0;
                    elif data2read == "moisture":
                        soilMoisture = 11.4293 + (0.0000000010698 * math.pow(rawValue, 4.0) - 0.00000152538 * math.pow(rawValue, 3.0) +  0.000866976 * math.pow(rawValue, 2.0) - 0.169422 * rawValue)
                        value2report = 100.0 * (0.0000045 * math.pow(soilMoisture, 3.0) - 0.00055 * math.pow(soilMoisture, 2.0) + 0.0292 * soilMoisture - 0.053); # seems to be off, check https://github.com/Parrot-Developers/node-flower-power/blob/master/TSRP/flower-power-tsrp.js#L80
                        if value2report < 0.0:
                            value2report = 0.0
                        elif value2report > 60.0:
                            value2report = 60.0;
                    else:
                        value2report = rawValue

                    if isinstance(value2report, int):
                        value2report = value2report * 1.0
                    elif isinstance(value2report, float):
                        value2report = round(value2report, 1)
                    elif isinstance(value2report, str):
                        value2report = value2report
                    else:
                        value2report = ''.join(chr(n) for n in value2report)

                    _LOGGER.info('Decoded result for %s: %s',
                                data2read, value2report)
                    self._cache[data2read] = value2report
        except:
            self._cache = None
            self._last_read = datetime.now() - self._cache_timeout + timedelta(seconds=180)
            raise

        if self.cache_available():
            self._last_read = datetime.now()
        else:
            # If a sensor doesn't work, wait 3 minutes before retrying
            self._last_read = datetime.now() - self._cache_timeout + timedelta(seconds=180)

    def parameter_values(self, read_cached=False):
        """Return a value of one of the monitored paramaters.

        This method will try to retrieve the data from cache and only
        request it by bluetooth if no cached value is stored or the cache is
        expired.
        This behaviour can be overwritten by the "read_cached" parameter.
        """

        # Use the lock to make sure the cache isn't updated multiple times
        with self.lock:
            if (read_cached is False) or \
                    (self._last_read is None) or \
                    (datetime.now() - self._cache_timeout > self._last_read):
                self.fill_cache()
            else:
                _LOGGER.info("Using cache (%s < %s)",
                              datetime.now() - self._last_read,
                              self._cache_timeout)

        if self.cache_available():
            return self._cache
        else:
            raise BluetoothBackendException("Could not read data from Parrot Flower Power sensor %s" % self._mac)



    def parameter_value(self, parameter, read_cached=False):
        """Return a value of one of the monitored paramaters.

        This method will try to retrieve the data from cache and only
        request it by bluetooth if no cached value is stored or the cache is
        expired.
        This behaviour can be overwritten by the "read_cached" parameter.
        """

        return self.parameter_values(read_cached)[parameter]


    def clear_cache(self):
        """Manually force the cache to be cleared."""
        self._cache = None
        self._last_read = None

    def cache_available(self):
        """Check if there is data in the cache."""
        return ((self._cache is not None) and (self._cache))

    @staticmethod
    def _format_bytes(raw_data):
        """Prettyprint a byte array."""
        if raw_data is None:
            return 'None'
        return ' '.join([format(c, "02x") for c in raw_data]).upper()
