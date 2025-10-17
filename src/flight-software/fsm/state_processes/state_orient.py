# state_orient.py


# ++++++++++++++ Imports/Installs ++++++++++++++ #
import asyncio
import numpy as np
from src/flight-software/lib/pysquared/hardware/light_sensor/manager import get_light

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
            # defining which variable corresponds to which coordinate/panel


            light1 = get_light(board.vsolar1)
            light2 = get_light(board.solar2)
            light3 = get_light(board.vsolar3)
            light4 = get_light(board.vsolar4)
            lights = [light1, light2, light3, light4]


            pos_xvec = np.array([1, 0])
            neg_xvec = np.array([-1, 0])
            pos_yvec = np.array([0, 1])
            neg_yvec = np.array([0, -1])
            lightvecs = [pos_xvec, neg_xvec, pos_yvec, neg_yvec]

            # weighted light vectors

            light_vec = np.array([])
            for i in range(4):
                light_vec[i] = lights[i] * lightvecs[i]


            # gets the magnitude of the sun vector

            # norm sum of weighted light vectors
            net_vec = np.linalg.norm(light_vec[1] + light_vec[2] + light_vec[3] + light_vec[4])


            pointvecs = [pos_xvec, neg_xvec, pos_yvec, neg_yvec, np.array([1, 1]), np.array([1, -1]), np.array([-1, 1]), np.array([-1, -1])]
            # find minimum dot product between the
            min_dot_product = -1
            for i in range(8):
                dot_product = np.dot(net_vec, pointvecs[i])
                if dot_product < min_dot_product:
                    min_dot_product = dot_product
                    min_index = i

            # activate the spring corresponding to min_index
        

            # NOTE:
            # get_light from light sensor in pysquared
            # board.RXO, board.TX0, board.RX1, board.TX1

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
