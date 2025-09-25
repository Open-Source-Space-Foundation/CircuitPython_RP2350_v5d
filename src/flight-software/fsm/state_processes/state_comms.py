# state_comms.py



# ++++++++++++++ Imports/Installs ++++++++++++++ #
import asyncio
from lib.pysquared.protos.radio import RadioProto


# ++++++++++++++ Functions: Helper ++++++++++++++ #
class StateComms:
    def __init__(self, dp_obj, logger, radio):
        self.dp_obj = dp_obj
        self.logger = logger
        self.running = False
        self.done = True
        self.radio : RadioProto = radio
    
    async def run(self):
        self._running = True
        while self._running:
            await asyncio.sleep(2)
            # NOTE: add some custom data as needed   
            self.radio.send("We're in comms.  Setup is going well.")  
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