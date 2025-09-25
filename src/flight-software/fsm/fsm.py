# fsm.py



# ++++++++++++++++++ Imports and Installs ++++++++++++++++++ #
import asyncio
from fsm.state_processes.state_comms import StateComms
from fsm.state_processes.state_deploy import StateDeploy
from fsm.state_processes.state_bootup import StateBootup
from fsm.state_processes.state_orient import StateOrient
from fsm.state_processes.state_antennas import StateAntennas
from fsm.state_processes.state_detumble import StateDetumble


# ++++++++++++++++++++ Class Definition ++++++++++++++++++++ #
class FSM:
    def __init__(self, dp_obj, logger, radio):
        self.dp_obj = dp_obj    # object of type DataProcess
        self.logger = logger    # logging status of FSM states
        self.state_objects = {
            "bootup"    : StateBootup(dp_obj, logger),
            "detumble"  : StateDetumble(dp_obj, logger),
            "antennas"  : StateAntennas(dp_obj, logger),
            "comms"     : StateComms(dp_obj, logger, radio),
            "deploy"    : StateDeploy(dp_obj, logger),
            "orient"    : StateOrient(dp_obj, logger),
        }
        self.curr_state_name = "bootup"
        self.curr_state_object = self.state_objects["bootup"]
        self.curr_state_run_asyncio_task = None
        self.payload_deployed_already = False
        self.antennas_deployed_already = False

    def set_state(self, new_state_name):
        """
        This function is called when we switch states from execute_fsm()
        """
        print(f"New State: {new_state_name}")

        # Stop current state's background task
        if self.curr_state_run_asyncio_task is not None:
            self.curr_state_object.stop()
            self.curr_state_run_asyncio_task.cancel()
            self.curr_state_run_asyncio_task = None

        self.curr_state_name = new_state_name
        self.curr_state_object = self.state_objects[new_state_name]
        self.curr_state_run_asyncio_task = asyncio.create_task(self.curr_state_object.run())

    def execute_fsm_step(self):
        """
        This function runs a single execution of the finite state machine (fsm)
        It checks its current state and data points and sees if we 
        need to change state, take action, etc.
        Note: because we pass in db_obj, its data variable will update 
        automatically if any changes are made for that db_obj
        """
        
        # NOTE: Emergency override for low battery and power consumption is handled in main.py
        # NOTE: Need to introduce emergency detumble post-first detumble, then continue where left off

        # Startup → Detumble
        if self.curr_state_name == "bootup" and self.curr_state_object.is_done():
            self.set_state("detumble")
            return
        
        # Emergency Detumble
        if self.dp_obj.data["data_imu_av_magnitude"] > 1:
            # Don't wait for other state to be done, shut it off immediately
            self.set_state("detumble")

        # Detumble → Antennas
        if self.curr_state_name == "detumble" and self.curr_state_object.is_done():
            if not self.antennas_deployed_already:
                self.antennas_deployed_already = True
                self.set_state("antennas")
            else:
                self.set_state("comms")
            return

        # Antennas → Comms
        if self.curr_state_name == "antennas" and self.curr_state_object.is_done():
            self.set_state("comms")
            return
        
        # TODO: need to write out orient process
            # question for orient: what pins do we read to sense light?

        # Comms → Deploy or Orient
        if self.curr_state_name == "comms" and self.curr_state_object.is_done():
            if not self.payload_deployed_already:
                self.payload_deployed_already = True
                self.set_state("deploy")
            else:
                self.set_state("orient")
            return

        # Deploy → Orient Payload
        if self.curr_state_name == "deploy" and self.curr_state_object.is_done():
            self.set_state("orient")
            return

        # Orient Payload → Comms
        if self.curr_state_name == "orient" and self.curr_state_object.is_done():
            self.set_state("comms")
            return
        
