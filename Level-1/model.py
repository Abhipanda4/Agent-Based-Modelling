import numpy as np

from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

from config import *
from agent import *

class World(Model):
    def __init__(self, N, width=100, height=100):
        self.num_agents = N
        self.grid = MultiGrid(width, height, False)
        self.schedule = RandomActivation(self)
        self.running = True
        self.population_center_x = np.random.randint(POP_MARGIN, self.grid.width - POP_MARGIN)
        self.population_center_y = np.random.randint(POP_MARGIN, self.grid.height - POP_MARGIN)
        self.num_energy_resources = RESERVE_SIZE
        self.dead_people = 0

        # add social agents to the world
        for i in range(self.num_agents):
            if np.random.uniform() <= EXPLORER_RATIO:
                # create a new explorer
                a = Explorer("explorer_%d" %(i), self)
            else:
                # create a new exploiter
                a = Exploiter("exploiter_%d" %(i), self)

            # keep society members confined at beginning
            x = np.random.randint(self.population_center_x - POP_SPREAD, self.population_center_x + POP_SPREAD)
            y = np.random.randint(self.population_center_y - POP_SPREAD, self.population_center_y + POP_SPREAD)
            self.grid.place_agent(a, (x, y))

            # add agent to scheduler
            self.schedule.add(a)

        # add energy reserves to the world
        for i in range(self.num_energy_resources):
            a = EnergyResource("energy_reserve_%d" %(i), self)

            # decide location of energy reserve
            x = np.random.randint(0, self.grid.width)
            y = np.random.randint(0, self.grid.height)
            self.grid.place_agent(a, (x, y))

            self.schedule.add(a)

    def step(self):
        self.schedule.step()
