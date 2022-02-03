# Copyright (C) 2021 Romain Bazile
# 
# This file is part of the PlanktoScope software.
# 
# PlanktoScope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PlanktoScope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PlanktoScope.  If not, see <http://www.gnu.org/licenses/>.

# Logger library compatible with multiprocessing
from loguru import logger

# TODO rewrite this in PlantUML
# This works with https://www.diagram.codes/d/state-machine
# "wait for pump" as pump
# "start imager" as imager
# "capture image" as capture
#
# START->stop["init"]
# imager->pump["start pumping"]
# pump->stop["stop"]
# stop->imager["start"]
# pump->capture["pumping is done"]
# capture->pump["start pump"]
# capture->stop["stop or done"]


# State machine class
class ImagerState(object):
    name = "state"
    allowed = []

    def switch(self, state):
        """Switch to new state"""
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
    """State of getting ready to start"""

    name = "imaging"
    allowed = ["waiting", "stop"]


class Waiting(ImagerState):
    """State of waiting for the pump to finish"""

    name = "waiting"
    allowed = ["stop", "capture"]


class Capture(ImagerState):
    """State of capturing image"""

    name = "capture"
    allowed = ["stop", "waiting"]


class Imager(object):
    """A class representing the imager"""

    def __init__(self):
        # State of the imager - default is stop.
        self.state = Stop()

    def change(self, state):
        """Change state"""
        self.state.switch(state)
