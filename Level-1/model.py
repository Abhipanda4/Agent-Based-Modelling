import numpy as np

from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

from config import *
from agent import *

class World(Model):
    def __init__(self, N, width=100, height=100):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True

        for i in range(self.num_agents):
            if np.random.uniform() <= EXPLORER_RATIO:
                # create a new explorer
                a = Explorer(i, self)
            else:
                # create a new exploiter
                a = Exploiter(i, self)

            # add agent to scheduler
            self.schedule.add(a)

            x = np.random.randint(0, self.grid.width)
            y = np.random.randint(0, self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.schedule.step()
