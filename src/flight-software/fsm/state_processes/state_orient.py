# state_orient.py


# ++++++++++++++ Imports/Installs ++++++++++++++ #
import asyncio
import board
import numpy as np
import from lib.pysquared.hardware.light_sensor.manager.veml7700 import VEML7700Manager.get_light

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


            try:
                light1 = get_light(board.vsolar1)
                light2 = get_light(board.solar2)
                light3 = get_light(board.vsolar3)
                light4 = get_light(board.vsolar4)
                lights = [light1, light2, light3, light4]
            except Exception as e:
                self.logger.error(f"Failed to read light sensors: {e}")
                # Use default values if sensors fail
                from src.flight-software.lib.pysquared.sensor_reading.light import Light
                lights = [Light(0.0), Light(0.0), Light(0.0), Light(0.0)]


            pos_xvec = np.array([1, 0])
            neg_xvec = np.array([-1, 0])
            pos_yvec = np.array([0, 1])
            neg_yvec = np.array([0, -1])
            lightvecs = [pos_xvec, neg_xvec, pos_yvec, neg_yvec]

            # weighted light vectors
            light_vec = [np.array([0.0, 0.0]) for _ in range(4)]
            for i in range(4):
                light_vec[i] = lights[i] * lightvecs[i]


            # gets the magnitude of the sun vector

            # norm sum of weighted light vectors, net_vec is the sun vector
            net_vec = np.linalg.norm(light_vec[1] + light_vec[2] + light_vec[3] + light_vec[4])


            point_vecs = [pos_xvec, neg_xvec, pos_yvec, neg_yvec, np.array([1, 1]), np.array([1, -1]), np.array([-1, 1]), np.array([-1, -1])]
            # find maximum dot product between the
            max_dot_product = -1
            best_direction = 0
            for i in range(8):
                dot_product = np.dot(net_vec, point_vecs[i])
                if dot_product > max_dot_product:
                    max_dot_product = dot_product
                    best_direction = i

            # Log the results
            self.logger.info(f"Sun vector: {net_vec}")
            self.logger.info(f"Best direction: {best_direction}, Alignment: {max_dot_product:.3f}")
            
            # activate the spring corresponding to best_direction
            # TODO: Implement actual spring activation based on best_direction
            # Direction mapping:
            # 0: +X, 1: -X, 2: +Y, 3: -Y
            # 4: +X+Y diagonal, 5: +X-Y diagonal  
            # 6: -X+Y diagonal, 7: -X-Y diagonal
            
            # NOTE:
            # consider edge case of net vec = 0, don't activate any springs?
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
