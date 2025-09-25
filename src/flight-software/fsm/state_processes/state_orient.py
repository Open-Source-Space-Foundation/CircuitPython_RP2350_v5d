# state_orient.py



# ++++++++++++++ Imports/Installs ++++++++++++++ #
import board
import asyncio
import digitalio
from lib.pysquared.hardware.digitalio import initialize_pin


# ++++++++++++++ Functions: Helper ++++++++++++++ #
class StateOrient:
    def __init__(self, dp_obj, logger):
        """
        Initialize the class object
        """
        self.dp_obj = dp_obj
        self.logger = logger
        self.running = False
        self.done = False
    
    async def run(self):
        """
        Run the deployment sequence asynchronously
        """
        self.running = True
        while self.running:
            await asyncio.sleep(2)
            # TODO: we need to decide which springs to run current through
            # this should be based on the sun sensor
            # potential idea: use solar_power_monitor: PowerMonitorProto = INA219Manager(logger, i2c1, 0x44)

    def stop(self):
        """
        Used by FSM to manually stop run()
        """
        self.running = False

    def is_done(self):
        """
        Checked by FSM to see if the run() completed on its own
        If it did complete, it shuts down the async task run()
        """
        return self.done