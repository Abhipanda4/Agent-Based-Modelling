import numpy as np
import matplotlib.pyplot as plt

from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from config import *
from agent import *

class World(Model):
    def __init__(self, N, coop, e_prob, width=100, height=100):
        self.num_agents = N
        self.grid = MultiGrid(width, height, False)
        self.schedule = RandomActivation(self)
        self.running = True
        self.population_center_x = np.random.randint(POP_MARGIN, self.grid.width - POP_MARGIN)
        self.population_center_y = np.random.randint(POP_MARGIN, self.grid.height - POP_MARGIN)
        self.num_energy_resources = RESERVE_SIZE
        self.num_explorers = 0
        self.num_exploiters = 0
        self.datacollector = DataCollector(model_reporters={"Num_Explorer": "num_explorers","Num_Exploiter": "num_exploiters"})
        self.bases = self.init_base()
        self.ages = []
        self.expected_ages = []
        self.member_tracker = []
        self.energy_tracker = []
        self.decay_rates = self.init_decay_rates()

        # add social agents to the world
        for i in range(1, self.num_agents + 1):
            if np.random.uniform() <= EXPLORER_RATIO:
                # create a new explorer
                a = Explorer("explorer_%d" %(i), self, coop)
                self.num_explorers += 1
            else:
                # create a new exploiter
                a = Exploiter("exploiter_%d" %(i), self, coop, e_prob)
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
            a = EnergyResource("energy_reserve_%d" %(i), self, self.decay_rates[i])

            # decide location of energy reserve
            x = np.random.randint(0, self.grid.width)
            y = np.random.randint(0, self.grid.height)
            self.grid.place_agent(a, (x, y))

            self.schedule.add(a)

    def init_base(self):
        pos = (self.population_center_x, self.population_center_y)
        return self.grid.get_neighborhood(pos, True, radius=POP_SPREAD)

    def init_decay_rates(self):
        decay_rates = list(np.random.uniform(-DECAY_RATE, DECAY_RATE, self.num_energy_resources - 1))
        decay_rates.extend([-1 * np.sum(decay_rates)])
        decay_rates += np.random.uniform(-0.1, 0, self.num_energy_resources)
        np.random.shuffle(decay_rates)
        return decay_rates

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self.member_tracker.append((self.num_explorers, self.num_exploiters))

        # keep track of total energy in world
        energies = [e.reserve for e in self.schedule.agents if isinstance(e, EnergyResource)]
        if len(energies) > 0:
            mean_energy = np.mean(energies)
        else:
            mean_energy = 0
        self.energy_tracker.append(mean_energy)

        # change location of energy resources every 500 steps randomly
        # and change decay_rate to opposite every 100 steps
        if self.schedule.time % 50 == 0:
            for e in self.schedule.agents:
                if isinstance(e, EnergyResource) and np.random.uniform() < 0.1:
                    # change location
                    e.decay_rate *= -1
                    if self.schedule.time % 500 == 0:
                        self.grid.remove_agent(e)
                        x = np.random.randint(0, self.grid.width)
                        y = np.random.randint(0, self.grid.height)
                        self.grid.place_agent(e, (x, y))

