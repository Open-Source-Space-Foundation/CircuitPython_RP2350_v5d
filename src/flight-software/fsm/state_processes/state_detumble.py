# state_detumble.py



# ++++++++++++++ Imports/Installs ++++++++++++++ #
import asyncio
from lib.pysquared.detumble import magnetorquer_dipole


# ++++++++++++++ Functions: Helper ++++++++++++++ #
class StateDetumble:
    def __init__(self, dp_obj, logger):
        """
        Initialize the class object
        """
        self.dp_obj = dp_obj
        self.logger = logger
        self.running = False
        self.done = False
        self.detumble_frequency = 5 # in seconds; how long to wait between data reads
        self.detumble_threshold = 0.05
    
    async def run(self):
        """
        Run the deployment sequence asynchronously
        """
        self.running = True
        while self.running:
            await asyncio.sleep(self.detumble_frequency)
            # Pull data from dp_obj
            mag_field = self.dp_obj.data["data_magnetometer_vector"]
            ang_vel = self.dp_obj.data["data_imu_av_magnitude"]
            # Verify data is present, if not, skip calculations
            if mag_field is None or ang_vel is None:
                note1 = "[FSM: Detumble] Waiting on Mag Field"
                note2 = "[FSM: Detumble] Waiting on Ang Vel"
                self.logger.info(note1) if mag_field is None else self.logger.info(note2)
                continue
            # If Ang Vel is sufficintly stabilized, return
            if ang_vel < self.detumble_threshold:
                self.logger.info("[FSM: Detumble] Ang Vel Sufficiently Stabilized")
                self.done = True
                continue
            # If Ang Vel is not stable, compute dipole
            # This is the quantity you want your magnetorquers to generate to stabilize CubeSAT
            dipole_vector = magnetorquer_dipole(tuple(mag_field), tuple(ang_vel))
            # TODO: Send result to magnetorquer

            # NOTE:
            # we'll be using magnetorquers on the 4 sides of the satellite
            # aka the solar panel cells

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