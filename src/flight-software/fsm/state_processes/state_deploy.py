# state_deploy.py



# ++++++++++++++ Imports/Installs ++++++++++++++ #
import board # from typings import board
import asyncio
import digitalio
from lib.pysquared.hardware.digitalio import initialize_pin
from lib.pysquared.hardware.burnwire.manager.burnwire import BurnwireManager


# ++++++++++++++ Functions: Helper ++++++++++++++ #
class StateDeploy:
    def __init__(self, dp_obj, logger):
        self.dp_obj = dp_obj
        self.logger = logger
        self.burnwire_heater = initialize_pin(logger, 
                                              board.FIRE_DEPLOY1_A, 
                                              digitalio.Direction.OUTPUT, 
                                              False)
        self.burnwire1_fire = initialize_pin(logger, 
                                             board.FIRE_DEPLOY1_B, 
                                             digitalio.Direction.OUTPUT, 
                                             False)
        self.burnwire = BurnwireManager(self.logger,
                                        self.burnwire_heater,
                                        self.burnwire1_fire)
        self.burn_duration = 5
        self.finished_burn = False
        self.running = False
        self.done = False
    
    async def run(self):
        self.running = True
        while self.running:
            await asyncio.sleep(2)
            # Burn the wire if not already done to release the payload
            if not self.finished_burn:
                self.burnwire.burn(self.burn_duration)
                self.finished_burn = True
            self.done = True
            
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