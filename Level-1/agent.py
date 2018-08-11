import numpy as np
import random

from mesa import Agent

from config import *

class SocietyMember(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.memory = []
        self.energy = np.random.normal(MEAN_ENERGY, STDDEV_ENERGY, size=1)

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False)
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def step(self):
        raise NotImplementedError

class Explorer(SocietyMember):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "explorer"
        self.stamina = np.random.normal(EXPLORER_MEAN_STAMINA, EXPLORER_STD_STAMINA)
        self.communication_range = EXPLORER_COMM_RANGE
        self.sense_range = EXPLORER_SENSE_RANGE

    def step(self):
        self.move()
        self.energy -= self.stamina

class Exploiter(SocietyMember):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "exploiter"
        self.stamina = np.random.normal(EXPLOITER_MEAN_STAMINA, EXPLOITER_STD_STAMINA)
        self.communication_range = EXPLOITER_COMM_RANGE
        self.sense_range = EXPLOITER_SENSE_RANGE

    def step(self):
        self.move()
        self.energy -= self.stamina
