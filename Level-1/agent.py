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
            # remove this energy reserve from all agent's memories
            for a in self.model.schedule.agents:
                if isinstance(a, SocietyMember) and self.pos in a.memory:
                    a.memory.remove(self.pos)

            # remove enrgy from scheduler and world
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)

class SocietyMember(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.memory = []
        self.energy = np.random.normal(MEAN_ENERGY, STDDEV_ENERGY, size=1)[0]
        self.age = 0
        self.target = None

    def update_target(self):
        if self.target is None:
            if len(self.memory) > 0:
                self.target = min(self.memory, key=lambda x: max(x[0] - self.pos[0], x[1] - self.pos[1]))

    def update_memory(self, max_range):
        '''
        Add new energy resources to memory which are within
        the max_range cells from curr position
        '''
        nbrs = self.model.grid.get_neighbors(self.pos, moore=True, radius=max_range)
        for e in nbrs:
            if isinstance(e, EnergyResource) and e.pos not in self.memory:
                self.memory.append(e.pos)
                if len(self.memory) == 1:
                    self.target = e.pos

    def mine_energy(self):
        cell_occupiers = self.model.grid.get_cell_list_contents(self.pos)
        energy_sources = [e for e in cell_occupiers if isinstance(e, EnergyResource)]
        if len(energy_sources) > 0:
            src = energy_sources[0]
        else:
            # the reserve has decayed before agent reached here
            self.target = None
            self.update_target()
            return

        if src.reserve <= 0:
            self.target = None
            self.update_target()
            return

        # mining increases agent's energy and reduces energy of reserve
        self.energy += self.mining_rate
        src.reserve -= self.mining_rate

    def share_memory(self, agent):
        cooperation = 0.5
        for m in self.memory:
            if np.random.uniform() < cooperation and m not in agent.memory:
                agent.memory.append(m)

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
        print("Agent %s is dying at an age of %d" %(self.unique_id, self.age))
        self.model.dead_people += 1

    def move(self):
        ''' Move to a neighboring cell in grid '''
        raise NotImplementedError

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
        self.drift = random.choice(DIRECTIONS)
        self.nbr_prob_dist = self.get_nbr_prob_dist()
        self.mine_mode = False

    def get_nbr_prob_dist(self):
        dist = [0.25 / 5] * 8
        if self.drift == 0:
            idx = [5, 6, 7]
        elif self.drift == 1:
            idx = [2, 4, 7]
        elif self.drift == 2:
            idx = [0, 1, 2]
        elif self.drift == 3:
            idx = [0, 3, 5]

        for i in idx:
            dist[i] = 0.25
        return dist

    def get_next_cell(self):
        nbrs = self.model.grid.get_neighborhood(self.pos, moore=True, radius=1)
        if len(nbrs) != 8:
            cell = random.choice(nbrs)
        else:
            nbr_idx = list(range(8))
            cell_idx = np.random.choice(nbr_idx, p=self.nbr_prob_dist)
            cell = nbrs[cell_idx]
        return cell

    def get_target(self):
        return self.pos

    def step(self):
        # add new energy resources into memory
        if self.model.schedule.time % SENSE_STEPS == 0:
            self.update_memory(max_range=EXPLORER_SENSE_RANGE)

        # share memory with other agents
        if self.model.schedule.time % COMMUNICATION_STEPS == 0:
            self.communicate(max_range=EXPLORER_COMM_RANGE)

        if self.target is not None and self.target == self.pos:
            # already reached an energy source
            if self.energy <= 2 * THRESHOLD_EXPLORER:
                # mine energy from this location if energy is low
                self.mine_energy()
            else:
                self.mine_mode = False
                self.target = None
            self.age += 1
            return

        if not self.mine_mode:
            # move randomly with higher probability towards drift direction
            new_position = self.get_next_cell()
        else:
            # decide a target to move towards
            self.update_target()

            if self.target is not None:
                # move towards target in least distance path
                new_position = get_target_cell(self.target, self.pos)
            else:
                # since no energy resource is located yet, move randomly
                new_position = self.get_next_cell()

        self.model.grid.move_agent(self, new_position)
        self.energy -= self.stamina

        if not self.mine_mode and self.energy < THRESHOLD_EXPLORER:
            self.mine_mode = True

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

    def move(self):
        if self.target is None:
            self.update_target()

        if self.target == self.pos:
            self.mine_energy()

        if self.target is not None:
            new_position = get_target_cell(self.target, self.pos)

        self.model.grid.move_agent(self, new_position)
        self.energy -= self.stamina

    def step(self):
        self.age += 1
        if len(self.memory) > 0:
            self.move()
        elif np.random.uniform() < 0.2:
            nbrs = self.model.grid.get_neighborhood(self.pos, moore=True, radius=1)
            new_position = random.choice(nbrs)
            self.model.grid.move_agent(self, new_position)
            self.energy -= self.stamina


        if self.energy <= 0:
            self.die()
