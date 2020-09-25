# Logger library compatible with multiprocessing
from loguru import logger

# TODO rewrite this in PlantUML
# "wait for pump" as pump
# "start imager" as imager
# "capture image" as capture
# START->imager["init"]
# imager->pump["start pumping"]
# pump->stop["stop"]
# stop->imager["start"]
# pump->capture["pumping is done"]
# capture->pump["start pump"]
# capture->stop["stop or done"]
# capture->segmentation["if segmentation"]
# segmentation->stop["done"]

# State machine class
class ImagerState(object):
    name = "state"
    allowed = []

    def switch(self, state):
        """ Switch to new state """
        if state.name in self.allowed:
            logger.info(f"Current:{self} => switched to new state {state.name}")
            self.__class__ = state
        else:
            logger.error(f"Current:{self} => switching to {state.name} not possible.")

    def __str__(self):
        return self.name


class Stop(ImagerState):
    name = "stop"
    allowed = ["imaging"]


class Imaging(ImagerState):
    """ State of getting ready to start """

    name = "imaging"
    allowed = ["waiting"]


class Waiting(ImagerState):
    """ State of waiting for the pump to finish """

    name = "waiting"
    allowed = ["stop", "capture"]


class Capture(ImagerState):
    """ State of capturing image """

    name = "capture"
    allowed = ["stop", "waiting", "segmentation"]


class Segmentation(ImagerState):
    """ State of segmenting capteured images """

    name = "segmentation"
    allowed = ["stop"]


class Imager(object):
    """ A class representing the imager """

    def __init__(self):
        # State of the imager - default is stop.
        self.state = Stop()

    def change(self, state):
        """ Change state """
        self.state.switch(state)
