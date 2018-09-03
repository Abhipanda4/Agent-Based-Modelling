import numpy as np
import matplotlib.pyplot as plt

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
        self.ages = []
        self.expected_ages = []
        self.num_explorers = 0
        self.num_exploiters = 0
        self.bases = self.init_base()

        # add social agents to the world
        for i in range(1, self.num_agents + 1):
            if np.random.uniform() <= EXPLORER_RATIO:
                # create a new explorer
                a = Explorer("explorer_%d" %(i), self)
                self.num_explorers += 1
            else:
                # create a new exploiter
                a = Exploiter("exploiter_%d" %(i), self)
                self.num_exploiters += 1

            # keep society members confined at beginning
            x = np.random.randint(self.population_center_x - POP_SPREAD, self.population_center_x + POP_SPREAD)
            y = np.random.randint(self.population_center_y - POP_SPREAD, self.population_center_y + POP_SPREAD)
            self.grid.place_agent(a, (x, y))

            # add agent to scheduler
            self.schedule.add(a)
            self.expected_ages.append(a.energy / a.living_cost)

        # add energy reserves to the world
        for i in range(self.num_energy_resources):
            a = EnergyResource("energy_reserve_%d" %(i), self)

            # decide location of energy reserve
            x = np.random.randint(0, self.grid.width)
            y = np.random.randint(0, self.grid.height)
            self.grid.place_agent(a, (x, y))

            self.schedule.add(a)

    def init_base(self):
        pos = (self.population_center_x, self.population_center_y)
        return self.grid.get_neighborhood(pos, True, radius=POP_SPREAD)

    def step(self):
        self.schedule.step()
        if self.schedule.steps % NEW_ENERGY_STEPS == 0:
            if np.random.uniform() < NEW_ENERGY_PROB:
                self.num_energy_resources += 1
                a = EnergyResource("energy_reserve_%d" %(self.num_energy_resources), self)

                # decide location of energy reserve
                x = np.random.randint(0, self.grid.width)
                y = np.random.randint(0, self.grid.height)
                self.grid.place_agent(a, (x, y))

                self.schedule.add(a)

        # log info about the world
        print(self.num_explorers, self.num_exploiters)
