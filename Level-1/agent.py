import numpy as np
import random

from mesa import Agent

from config import *

class SocietyMember(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.memory = None
        self.energy = np.random.normal(MEAN_ENERGY, STDDEV_ENERGY, size=1)
        self.age = 0

    def move(self):
        ''' Move to a neighboring cell in grid '''
        possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False)
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def update_memory(self):
        ''' Add new energy resources to memory '''
        pass

    def share_memory(self, agent):
        pass

    def communicate(self, max_range):
        ''' Communication between 2 agents '''
        nbrs = self.model.grid.get_neighbors(self.pos, moore=True, radius=max_range)
        for a in nbrs:
            if isinstance(a, SocietyMember):
                if np.random.uniform() <= COMMUNICATION_PROB:
                    self.share_memory(a)

    def die(self):
        ''' Removes the agent from gridworld and scheduler '''
        self.model.schedule.remove(self)
        self.model.grid.remove_agent(self)

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
        self.age += 1
        self.energy -= self.stamina
        if self.energy <= 0:
            self.die()

class Exploiter(SocietyMember):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "exploiter"
        self.stamina = np.random.normal(EXPLOITER_MEAN_STAMINA, EXPLOITER_STD_STAMINA)
        self.communication_range = EXPLOITER_COMM_RANGE
        self.sense_range = EXPLOITER_SENSE_RANGE

    def step(self):
        self.age += 1
        if self.memory is not None:
            # try to explore with some small prob
            self.move()
            self.energy -= self.stamina

        if self.energy <= 0:
            self.die()
