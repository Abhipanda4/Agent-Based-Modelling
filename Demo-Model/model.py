import random

from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.time import RandomActivation

class MoneyAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.type = 1

    def step(self):
        for c in self.model.grid.coord_iter():
            print(c)


class EnergyAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.type = 2

    def step(self):
        pass

class MoneyModel(Model):
    def __init__(self, N):
        self.num_agents = N
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(30, 30, True)
        for i in range(self.num_agents):
            a = MoneyAgent(i, self)
            self.schedule.add(a)

            # add agent to grid
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.num_energy_sources = 5
        for idx in range(self.num_energy_sources):
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)

            pos = self.grid.get_neighborhood((x, y), moore=True, include_center=True, radius=1)
            for i, coord in enumerate(pos):
                e = EnergyAgent("%d_%d" %(idx, i), self)
                self.grid.place_agent(e, coord)

    def step(self):
        self.schedule.step()
        print("*" * 50)
