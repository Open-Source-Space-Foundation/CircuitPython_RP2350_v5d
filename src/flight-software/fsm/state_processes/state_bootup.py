# state_bootup.py



# ++++++++++++++ Imports/Installs ++++++++++++++ #
import asyncio



# ++++++++++++++ Functions: Helper ++++++++++++++ #
class StateBootup:
    def __init__(self, dp_obj, logger):
        """
        Initialize the class object
        """
        self.dp_obj = dp_obj
        self.logger = logger
        self.done = False
        self.running = False
    
    async def run(self):
        """
        Run the deployment sequence asynchronously
        """
        self.running = True
        # TODO: tasks
        await asyncio.sleep(10)
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