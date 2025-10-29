import json
import os
import time

import board
import digitalio
from lib.adafruit_mcp230xx.mcp23017 import MCP23017
from lib.adafruit_tca9548a import TCA9548A
from lib.pysquared.beacon import Beacon
from lib.pysquared.cdh import CommandDataHandler
from lib.pysquared.config.config import Config
from lib.pysquared.config.jokes_config import JokesConfig
from lib.pysquared.file_validation.manager.file_validation import FileValidationManager
from lib.pysquared.hardware.burnwire.manager.burnwire import BurnwireManager
from lib.pysquared.hardware.busio import _spi_init, initialize_i2c_bus
from lib.pysquared.hardware.digitalio import initialize_pin
from lib.pysquared.hardware.imu.manager.lsm6dsox import LSM6DSOXManager
from lib.pysquared.hardware.light_sensor.manager.veml6031x00 import VEML6031X00Manager
from lib.pysquared.hardware.load_switch.manager.loadswitch_manager import (
    LoadSwitchManager,
)
from lib.pysquared.hardware.magnetometer.manager.lis2mdl import LIS2MDLManager
from lib.pysquared.hardware.power_monitor.manager.ina219 import INA219Manager
from lib.pysquared.hardware.radio.manager.rfm9x import RFM9xManager
from lib.pysquared.hardware.radio.manager.sx1280 import SX1280Manager
from lib.pysquared.hardware.radio.packetizer.packet_manager import PacketManager
from lib.pysquared.hardware.temperature_sensor.manager.mcp9808 import MCP9808Manager
from lib.pysquared.logger import Logger
from lib.pysquared.nvm.counter import Counter
from lib.pysquared.protos.power_monitor import PowerMonitorProto
from lib.pysquared.rtc.manager.microcontroller import MicrocontrollerManager
from lib.pysquared.watchdog import Watchdog
from version import __version__

rtc = MicrocontrollerManager()


logger: Logger = Logger(
    error_counter=Counter(0),
    colorized=False,
)

logger.info(
    "Booting",
    hardware_version=os.uname().version,  # type: ignore[attr-defined]
    software_version=__version__,
)

watchdog = Watchdog(logger, board.WDT_WDI)
watchdog.pet()

logger.debug("Initializing Config")
config: Config = Config("config.json")
jokes_config: JokesConfig = JokesConfig("jokes.json")


def get_temp(sensor):
    for i in range(1000):
        print(sensor.get_temperature().value)
        time.sleep(0.1)


SPI0_CS0 = initialize_pin(logger, board.SPI0_CS0, digitalio.Direction.OUTPUT, True)
SPI1_CS0 = initialize_pin(logger, board.SPI1_CS0, digitalio.Direction.OUTPUT, True)

# manually set the pin high to allow mcp to be detected
GPIO_RESET = (
    initialize_pin(logger, board.GPIO_EXPANDER_RESET, digitalio.Direction.OUTPUT, True),
)

i2c1 = initialize_i2c_bus(
    logger,
    board.SCL1,
    board.SDA1,
    100000,
)

i2c0 = initialize_i2c_bus(
    logger,
    board.SCL0,
    board.SDA0,
    100000,
)


mcp = MCP23017(i2c1)


# #GPB
FACE4_ENABLE = mcp.get_pin(8)
FACE0_ENABLE = mcp.get_pin(9)
FACE1_ENABLE = mcp.get_pin(10)
FACE2_ENABLE = mcp.get_pin(11)
FACE3_ENABLE = mcp.get_pin(12)
FACE5_ENABLE = mcp.get_pin(13)
# READ ONLY
# CHARGE

# GPA
ENABLE_HEATER = mcp.get_pin(0)
PAYLOAD_PWR_ENABLE = mcp.get_pin(1)
FIRE_DEPLOY2_B = mcp.get_pin(2)
PAYLOAD_BATT_ENABLE = mcp.get_pin(3)
RF2_IO2 = mcp.get_pin(4)
RF2_IO1 = mcp.get_pin(5)
RF2_IO0 = mcp.get_pin(6)
RF2_IO3 = mcp.get_pin(7)

# # This defines the direction of the GPIO pins
FACE4_ENABLE.direction = digitalio.Direction.OUTPUT
FACE0_ENABLE.direction = digitalio.Direction.OUTPUT
FACE1_ENABLE.direction = digitalio.Direction.OUTPUT
FACE2_ENABLE.direction = digitalio.Direction.OUTPUT
FACE3_ENABLE.direction = digitalio.Direction.OUTPUT
ENABLE_HEATER.direction = digitalio.Direction.OUTPUT
PAYLOAD_PWR_ENABLE.direction = digitalio.Direction.OUTPUT


# # TODO(nateinaction): fix spi init
spi0 = _spi_init(
    logger,
    board.SPI0_SCK,
    board.SPI0_MOSI,
    board.SPI0_MISO,
)

spi1 = _spi_init(
    logger,
    board.SPI1_SCK,
    board.SPI1_MOSI,
    board.SPI1_MISO,
)

sband_radio = SX1280Manager(
    logger,
    config.radio,
    spi1,
    SPI1_CS0,
    initialize_pin(logger, board.RF2_RST, digitalio.Direction.OUTPUT, True),
    RF2_IO0,
    2.4,
    initialize_pin(logger, board.RF2_TX_EN, digitalio.Direction.OUTPUT, False),
    initialize_pin(logger, board.RF2_RX_EN, digitalio.Direction.OUTPUT, False),
)


# sleep_helper = SleepHelper(logger, config, watchdog)

uhf_radio = RFM9xManager(
    logger,
    config.radio,
    spi0,
    SPI0_CS0,
    initialize_pin(logger, board.RF1_RST, digitalio.Direction.OUTPUT, True),
)

magnetometer = LIS2MDLManager(logger, i2c1)

imu = LSM6DSOXManager(logger, i2c1, 0x6B)

uhf_packet_manager = PacketManager(
    logger,
    uhf_radio,
    config.radio.license,
    Counter(2),
    0.2,
)

cdh = CommandDataHandler(logger, config, uhf_packet_manager, jokes_config)
beacon = Beacon(
    logger,
    config.cubesat_name,
    uhf_packet_manager,
    time.monotonic(),
    imu,
    magnetometer,
    uhf_radio,
    sband_radio,
)

load_switch_0 = LoadSwitchManager(FACE0_ENABLE, True)
load_switch_1 = LoadSwitchManager(FACE1_ENABLE, True)
load_switch_2 = LoadSwitchManager(FACE2_ENABLE, True)
load_switch_3 = LoadSwitchManager(FACE3_ENABLE, True)
load_switch_4 = LoadSwitchManager(FACE4_ENABLE, True)


load_switch_0 = LoadSwitchManager(FACE0_ENABLE, True)  # type: ignore , upstream on mcp TODO
load_switch_1 = LoadSwitchManager(FACE1_ENABLE, True)  # type: ignore , upstream on mcp TODO
load_switch_2 = LoadSwitchManager(FACE2_ENABLE, True)  # type: ignore , upstream on mcp TODO
load_switch_3 = LoadSwitchManager(FACE3_ENABLE, True)  # type: ignore , upstream on mcp TODO
load_switch_4 = LoadSwitchManager(FACE4_ENABLE, True)  # type: ignore , upstream on mcp TODO


# Face Control Helper Functions
def all_faces_off():
    """
    This function turns off all of the faces. Note the load switches are disabled low.
    """
    load_switch_0.disable_load()
    load_switch_1.disable_load()
    load_switch_2.disable_load()
    load_switch_3.disable_load()
    load_switch_4.disable_load()


def all_faces_on():
    """
    This function turns on all of the faces. Note the load switches are enabled high.
    """
    load_switch_0.enable_load()
    load_switch_1.enable_load()
    load_switch_2.enable_load()
    load_switch_3.enable_load()
    load_switch_4.enable_load()


file_validator = FileValidationManager(logger)

## Face Sensor Stuff ##

# This is the TCA9548A I2C Multiplexer

mux_reset = initialize_pin(logger, board.MUX_RESET, digitalio.Direction.OUTPUT, False)
all_faces_on()
time.sleep(0.1)
mux_reset.value = True
tca = TCA9548A(i2c0, address=int(0x77))  # all 3 connected to high


# # Light Sensors
light_sensors = []
try:
    sensor = VEML6031X00Manager(logger, tca[0])  # type: ignore[arg-type]
    light_sensors.append(sensor)
except Exception:
    logger.debug("WARNING!!! Light sensor 0 failed to initialize")
    light_sensors.append(None)
try:
    sensor = VEML6031X00Manager(logger, tca[1])  # type: ignore[arg-type]
    light_sensors.append(sensor)
except Exception:
    logger.debug("WARNING!!! Light sensor 1 failed to initialize")
    light_sensors.append(None)
try:
    sensor = VEML6031X00Manager(logger, tca[2])  # type: ignore[arg-type]
    light_sensors.append(sensor)
except Exception:
    logger.debug("WARNING!!! Light sensor 2 failed to initialize")
    light_sensors.append(None)
try:
    sensor = VEML6031X00Manager(logger, tca[3])  # type: ignore[arg-type]
    light_sensors.append(sensor)
except Exception:
    logger.debug("WARNING!!! Light sensor 3 failed to initialize")
    light_sensors.append(None)
try:
    sensor = VEML6031X00Manager(logger, tca[5])  # type: ignore[arg-type]
    light_sensors.append(sensor)
except Exception:
    logger.debug("WARNING!!! Light sensor 4 failed to initialize")
    light_sensors.append(None)


# Onboard Temp Sensors
temp_sensors = []

# # Direct I2C sensors
# try:
#     temp_sensor5 = MCP9808Manager(logger, i2c0, addr=40)  # Antenna Board
# except Exception:
#     logger.debug("WARNING!!! Temp sensor (Antenna Board) failed")
#     temp_sensor5 = None
# temp_sensors.append(temp_sensor5)

# try:
#     temp_sensor6 = MCP9808Manager(logger, i2c1, addr=41)  # Flight Controller Board
# except Exception:
#     logger.debug("WARNING!!! Temp sensor  (Flight Controller Board) failed")
#     temp_sensor6 = None
# temp_sensors.append(temp_sensor6)

# TCA-connected temp sensors
try:
    sensor = MCP9808Manager(logger, tca[0], addr=27)
    temp_sensors.append(sensor)
except Exception:
    logger.debug("WARNING!!! Temp sensor (TCA[0]) failed")
    temp_sensors.append(None)
try:
    sensor = MCP9808Manager(logger, tca[1], addr=27)
    temp_sensors.append(sensor)
except Exception:
    logger.debug("WARNING!!! Temp sensor 1 failed")
    temp_sensors.append(None)
try:
    sensor = MCP9808Manager(logger, tca[2], addr=27)
    temp_sensors.append(sensor)
except Exception:
    logger.debug("WARNING!!! Temp sensor 2 failed")
    temp_sensors.append(None)
try:
    sensor = MCP9808Manager(logger, tca[3], addr=27)
    temp_sensors.append(sensor)
except Exception:
    logger.debug("WARNING!!! Temp sensor 3 failed")
    temp_sensors.append(None)
try:
    sensor = MCP9808Manager(logger, tca[5], addr=24)
    temp_sensors.append(sensor)
except Exception:
    logger.debug("WARNING!!! Temp sensor 4 failed (Z- Face Bottom pins")
    temp_sensors.append(None)
# these are the bottom 6 pins on the z- face connection, uncomment if that is where you plug in a face for the z- board
# try:
#     sensor = MCP9808Manager(logger, tca[6], addr=24)
#     temp_sensors.append(sensor)
# except Exception:
#     logger.debug("WARNING!!! Temp sensor 4 failed (Z- Face Top pins)")
# #     temp_sensors.append(None)
try:
    sensor = MCP9808Manager(logger, tca[7], addr=25)
    temp_sensors.append(sensor)
except Exception:
    logger.debug("WARNING!!! Temp sensor 5 failed (Antenna Board)")
    temp_sensors.append(None)

battery_power_monitor: PowerMonitorProto = INA219Manager(logger, i2c0, 0x40)
solar_power_monitor: PowerMonitorProto = INA219Manager(logger, i2c0, 0x41)

burnwire_heater_enable = initialize_pin(
    logger, board.FIRE_DEPLOY1_A, digitalio.Direction.OUTPUT, False
)
burnwire1_fire = initialize_pin(
    logger, board.FIRE_DEPLOY1_B, digitalio.Direction.OUTPUT, False
)

## Initializing the Burn Wire ##
antenna_deployment = BurnwireManager(
    logger, burnwire_heater_enable, burnwire1_fire, enable_logic=True
)


def test_magnetorquer():
    print("____ Test: Magnetorquer _______")
    m_val_1 = magnetometer.get_magnetic_field().value
    print("Magnetorquer value (initial):", m_val_1)
    print("You have 2 seconds to move the FC board")
    time.sleep(2)
    m_val_2 = magnetometer.get_magnetic_field().value
    print("Magnetorquer value (after):", m_val_2)
    diff = tuple(m_val_1[i] - m_val_2[i] for i in range(3))
    print("Difference:", diff)
    return input("Is this acceptable? (Y/N): ").strip().upper()


def test_imu():
    print("\n____ Test: IMU Sensors _______")
    imu_results = {}
    # Acceleration
    acc1 = imu.get_acceleration().value
    print("Initial acceleration:", acc1)
    print("You have 2 seconds to move the FC board")
    time.sleep(2)
    acc2 = imu.get_acceleration().value
    print("New acceleration:", acc2)
    acc_diff = tuple(acc1[i] - acc2[i] for i in range(3))
    print("Acceleration difference:", acc_diff)
    imu_results["acceleration"] = input("Is this acceptable? (Y/N): ").strip().upper()
    # Angular velocity
    ang1 = imu.get_angular_velocity().value
    print("Initial angular velocity:", ang1)
    print("You have 2 seconds to move the FC board")
    time.sleep(2)
    ang2 = imu.get_angular_velocity().value
    print("New angular velocity:", ang2)
    ang_diff = tuple(ang1[i] - ang2[i] for i in range(3))
    print("Angular velocity difference:", ang_diff)
    imu_results["angular_velocity"] = (
        input("Is this acceptable? (Y/N): ").strip().upper()
    )
    # Temperature
    temp1 = imu.get_temperature().value
    print("Initial temperature:", temp1)
    print("You have 10 seconds to heat the temp sensor")
    time.sleep(10)
    temp2 = imu.get_temperature().value
    print("New temperature:", temp2)
    temp_diff = temp1 - temp2
    print("Temperature difference:", temp_diff)
    imu_results["temperature"] = input("Is this acceptable? (Y/N): ").strip().upper()
    return imu_results


def test_burnwire():
    print("\n____ Test: Burnwire _______")
    choice = input("Would you like to try the burnwire test (Y/N)?: ").strip().lower()
    if choice == "y":
        print("Burning for 5 seconds....")
        antenna_deployment.burn(5)
        print("Finished burning.")
        return input("Did the burnwire get hot? (Y/N): ").strip().upper()
    return "N/A"


def test_light_sensors():
    print("\n____ Test: LEDs and Light Sensors _______")
    load_switches = [
        load_switch_0,
        load_switch_1,
        load_switch_2,
        load_switch_3,
        load_switch_4,
    ]
    light_results = {}
    for i, switch in enumerate(load_switches):
        print(f"\nTesting Load Switch {i}")
        switch.disable_load()
        led_off = input("Did a face LED turn OFF? (Y/N): ").strip().upper()
        switch.enable_load()
        led_on = input("Did the face LED turn ON? (Y/N): ").strip().upper()
        sensor = light_sensors[i]
        if sensor is not None:
            lux_before = sensor.get_lux().value
            print("Initial lux:", lux_before)
            time.sleep(2)
            lux_after = sensor.get_lux().value
            print("New lux:", lux_after)
            sensor_result = (
                input("Did the lux value change noticeably? (Y/N): ").strip().upper()
            )
        else:
            lux_before = lux_after = "N/A"
            sensor_result = "N"
        light_results[f"load_switch_{i}"] = {
            "led_off": led_off,
            "led_on": led_on,
            "lux_changed": sensor_result,
        }
    return light_results


def test_radio():
    print("\n____ Test: UHF Radio _______")
    message = {"command": "ping"}
    print("Sending Ping Command...")
    uhf_packet_manager.send(json.dumps(message).encode("utf-8"))
    count = 0
    result = "N"
    while count < 10:
        count += 1
        b = uhf_packet_manager.listen(1)
        time.sleep(1)
        uhf_packet_manager.send(json.dumps(message).encode("utf-8"))

        if b is not None:
            if b != b"ACK":
                print("Received not ACK :")
            else:
                print("Received ACK response:", b.decode("utf-8"))
                result = "Y"
                break
    return result


def test_battery_monitor():
    print("\n____ Test: Battery Power Monitor _______")
    value_with_batteries = battery_power_monitor.get_bus_voltage().value
    print("Voltage with batteries:", value_with_batteries)
    input("Please unplug the batteries and press Enter when done.")
    value_without_batteries = battery_power_monitor.get_bus_voltage().value
    print("Voltage without batteries:", value_without_batteries)
    if (value_with_batteries - value_without_batteries) >= 4.0:
        print("Voltage dropped by more than 4V. PASS.")
        return "Y"
    else:
        print("Voltage drop too small. FAIL.")
        return "N"


def test_solar_monitor():
    print("\n____ Test: Solar Power Monitor _______")
    solar_with_light = solar_power_monitor.get_bus_voltage().value
    print("Voltage with light:", solar_with_light)
    input("Please cover the solar panels and press Enter when ready.")
    solar_without_light = solar_power_monitor.get_bus_voltage().value
    print("Voltage without light:", solar_without_light)
    if (solar_with_light - solar_without_light) >= 0.5:
        print("Solar voltage dropped significantly. PASS.")
        return "Y"
    else:
        print("Solar voltage did not drop enough. FAIL.")
        return "N"


# ========== MAIN FUNCTION ==========


def test_all():
    results = {}
    results["magnetorquer"] = test_magnetorquer()
    imu_results = test_imu()
    results.update({f"imu_{k}": v for k, v in imu_results.items()})
    results["burnwire"] = test_burnwire()
    light_results = test_light_sensors()
    results.update(light_results)
    results["radio_send"] = test_radio()
    results["battery_power_monitor"] = test_battery_monitor()
    results["solar_power_monitor"] = test_solar_monitor()
    print("\n===== FINAL RESULTS =====")
    for key, val in results.items():
        print(f"{key}: {val}")
