import numpy as np
import random

from mesa import Agent

from config import *

def get_next_step(x_target, x_curr):
    if x_target > x_curr:
        return x_curr + 1
    elif x_target < x_curr:
        return x_curr - 1
    return x_curr

def get_target_cell(target, curr):
    x_t, y_t = target
    x_curr, y_curr = curr
    x_new = get_next_step(x_t, x_curr)
    y_new = get_next_step(y_t, y_curr)
    return (x_new, y_new)


class EnergyResource(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.reserve = max(0, np.random.normal(MEAN_RESERVE, STDDEV_RESERVE))
        self.decay_rate = np.random.uniform(-DECAY_RATE, DECAY_RATE)
        self.type = "energy_reserve"

    def step(self):
        self.reserve -= self.decay_rate
        if self.reserve <= 0:
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)

            # remove this energy reserve from all agent's memories
            for a in self.model.schedule.agents:
                if isinstance(a, SocietyMember) and self.pos in a.memory:
                    a.memory.remove(self.pos)


class SocietyMember(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.memory = []
        self.energy = np.random.normal(MEAN_ENERGY, STDDEV_ENERGY, size=1)[0]
        self.age = 0
        self.target = None

    def move(self):
        ''' Move to a neighboring cell in grid '''
        if not self.target:
            # if no target is present, move around randomly
            possible_steps = self.model.grid.get_neighborhood(
                    self.pos,
                    moore=True,
                    include_center=False)
            new_position = random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)
            self.energy -= self.stamina
        else:
            if self.target != self.pos:
                # if not reached target yet, move towards it
                new_position = get_target_cell(self.target, self.pos)
                self.model.grid.move_agent(self, new_position)
                self.energy -= self.stamina
            else:
                # if reached target, use it to replenish energy
                self.mine_energy()

    def update_target(self):
        if self.target is None:
            if len(self.memory) > 0:
                self.target = np.random.choice(self.memory)

    def update_memory(self, max_range):
        '''
        Add new energy resources to memory which are within
        the max_range cells from curr position
        '''
        nbrs = self.model.grid.get_neighbors(self.pos, moore=True, radius=max_range)
        for e in nbrs:
            if isinstance(e, EnergyResource):
                self.memory.append(e.pos)
                if len(self.memory) == 1:
                    self.target = e.pos

    def mine_energy(self):
        cell_occupiers = self.model.grid.get_cell_list_contents(self.pos)
        reserves = [e for e in cell_occupiers if isinstance(e, EnergyResource)]
        if len(reserves) > 0:
            src = reserves[0]
        else:
            # the reserve has decayed before agent reached here
            self.update_target()
            return

        if src.reserve <= 0:
            self.update_target()
            return

        # mining increases agent's energy and reduces energy of reserve
        self.energy += self.mining_rate
        src.reserve -= self.mining_rate

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
        self.mining_rate = EXPLORER_MINING_RATE

    def step(self):
        if self.model.schedule.time % SENSE_STEPS == 0:
            self.update_memory(max_range=EXPLORER_SENSE_RANGE)
            self.update_target()

        if self.model.schedule.time % COMMUNICATION_STEPS == 0:
            self.communicate(max_range=EXPLORER_COMM_RANGE)

        self.move()
        self.age += 1
        if self.energy <= 0:
            self.die()

class Exploiter(SocietyMember):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "exploiter"
        self.stamina = np.random.normal(EXPLOITER_MEAN_STAMINA, EXPLOITER_STD_STAMINA)
        self.communication_range = EXPLOITER_COMM_RANGE
        self.sense_range = EXPLOITER_SENSE_RANGE
        self.mining_rate = EXPLOITER_MINING_RATE

    def step(self):
        self.age += 1
        if len(self.memory) > 0:
            self.move()
            self.energy -= self.stamina

        if self.energy <= 0:
            self.die()
