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

def is_member(coord, list_of_tuples):
    coord_list = [i[0] for i in list_of_tuples]
    try:
        idx = coord_list.index(coord)
        return idx
    except ValueError:
        return None

class EnergyResource(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.reserve = max(MEAN_RESERVE/2, np.random.normal(MEAN_RESERVE, STDDEV_RESERVE))
        self.decay_rate = np.random.uniform(-DECAY_RATE, DECAY_RATE)
        self.type = "energy_reserve"

    def step(self):
        self.reserve -= self.decay_rate
        if self.reserve <= 0:
            # remove this energy reserve from all agent's memories
            for a in self.model.schedule.agents:
                if isinstance(a, SocietyMember):
                    idx = is_member(self.pos, a.memory)
                    if idx is not None:
                        a.memory.pop(idx)

            # remove enrgy from scheduler and world
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)

class SocietyMember(Agent):
    def __init__(self, unique_id, model, coop):
        super().__init__(unique_id, model)
        self.memory = []
        self.energy = np.random.normal(MEAN_ENERGY, STDDEV_ENERGY, size=1)[0]
        self.age = 0
        self.target = None
        self.share_probability = coop

    def update_target(self):
        def criteria(x):
            # define a selection criteria for target
            # it is based on amount of energy expected at the destination
            dest, reserve_size, decay, obs_time = x[0], x[1], x[2], x[3]
            d = max(dest[0] - self.pos[0], dest[1] - self.pos[1])
            reserve_size = reserve_size - (self.model.schedule.time - obs_time) * decay
            expected_energy = reserve_size - d * decay
            if expected_energy < 0:
                return 0
            return expected_energy

        if self.target is None:
            try:
                if self.is_returning_to_base:
                    self.target = random.choice(self.model.bases)
            except:
                pass

            if len(self.memory) > 0:
                # use epsilon-greedy policy for target selection
                if np.random.uniform() > EPSILON:
                    self.target = max(self.memory, key=criteria)[0]
                else:
                    expected_gain = [criteria(i) for i in self.memory]
                    total_sum = sum(expected_gain)
                    selection_p = [(i + 1)/(total_sum + len(expected_gain)) for i in expected_gain]

                    idx_list = list(range(len(self.memory)))
                    self.target = self.memory[np.random.choice(idx_list, p=selection_p)][0]

    def update_memory(self, max_range):
        '''
        Add new energy resources to memory which are within
        the max_range cells from curr position
        '''
        nbrs = self.model.grid.get_neighbors(self.pos, moore=True, radius=max_range)
        for e in nbrs:
            idx = is_member(e.pos, self.memory)
            if isinstance(e, EnergyResource):
                if idx is None:
                    # add new energy resource
                    self.memory.append((e.pos, e.reserve, e.decay_rate, self.model.schedule.time))
                else:
                    # the decay rate needs to be updated in memory
                    self.memory[idx] = (e.pos, e.reserve, e.decay_rate, self.model.schedule.time)

    def mine_energy(self):
        cell_occupiers = self.model.grid.get_cell_list_contents(self.pos)
        energy_sources = [e for e in cell_occupiers if isinstance(e, EnergyResource)]
        if len(energy_sources) > 0:
            src = energy_sources[0]
        else:
            # the reserve has decayed before agent reached here
            self.target = None
            self.update_target()
            return False

        if src.reserve <= 0:
            self.target = None
            self.update_target()
            return False

        # mining increases agent's energy and reduces energy of reserve
        self.energy += self.mining_rate
        src.reserve -= self.mining_rate
        return True

    def share_memory(self, agent):
        for m in self.memory:
            if np.random.uniform() < self.share_probability:
                idx = is_member(m[0], agent.memory)
                if idx is None:
                    agent.memory.append(m)

    def communicate(self, max_range):
        ''' Communication between 2 agents '''
        nbrs = self.model.grid.get_neighbors(self.pos, moore=True, radius=max_range)
        for a in nbrs:
            if isinstance(a, SocietyMember):
                if np.random.uniform() <= COMMUNICATION_PROB:
                    self.share_memory(a)

    def reproduce(self):
        ''' An agent reproduces to produca a new agent. The new agent is of
        same type as parent with high prob, but may also be different '''
        self.energy -= REPRODUCTION_ENERGY
        a = None
        self.model.num_agents += 1
        if self.type == "explorer":
            if np.random.uniform() < INHERITANCE_PROB:
                self.model.num_explorers += 1
                a = Explorer("explorer_%d" %(self.model.num_agents), self.model, self.share_probability)
            else:
                self.model.num_exploiters += 1
                a = Exploiter("exploiter_%d" %(self.model.num_agents), self.model, self.share_probability, 0.5)

        elif self.type == "exploiter":
            if np.random.uniform() < INHERITANCE_PROB:
                self.model.num_exploiters += 1
                a = Exploiter("exploiter_%d" %(self.model.num_agents), self.model, self.share_probability, 0.5)
            else:
                self.model.num_explorers += 1
                a = Explorer("explorer_%d" %(self.model.num_agents), self.model, self.share_probability)

        else:
            raise Exception("Alien has been found!!")

        # place the new agent in vicinity of the parent
        nbrs = self.model.grid.get_neighborhood(self.pos, moore=True, radius=3)
        pos = random.choice(nbrs)
        self.model.grid.place_agent(a, pos)

        # add the new agent to scheduler
        self.model.schedule.add(a)
        self.model.expected_ages.append(a.energy / a.living_cost)

    def step(self):
        raise NotImplementedError

class Explorer(SocietyMember):
    def __init__(self, unique_id, model, coop):
        super().__init__(unique_id, model, coop)
        self.type = "explorer"
        self.living_cost = max(0.25, np.random.normal(EXPLORER_COST_MEAN, EXPLORER_COST_STD))
        self.communication_range = EXPLORER_COMM_RANGE
        self.sense_range = EXPLORER_SENSE_RANGE
        self.mining_rate = EXPLORER_MINING_RATE
        self.drift = random.choice(DIRECTIONS)
        self.nbr_prob_dist = self.get_nbr_prob_dist()
        self.mine_mode = False
        self.change_direction_buffer_time = 0
        self.is_returning_to_base = False
        self.cycle_rate = int(np.random.uniform(BASE_RETURN_INTERVAL - BASE_RETURN_DEV, BASE_RETURN_INTERVAL + BASE_RETURN_DEV))

    def die(self):
        ''' Removes the agent from gridworld and scheduler '''
        self.model.num_explorers -= 1
        self.model.schedule.remove(self)
        self.model.grid.remove_agent(self)

    def get_nbr_prob_dist(self):
        ''' Gives a probability distribution of selecting neighbor cells
        so that overall a drift is achieved in one direction '''
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
            # agent is at boundary
            cell = random.choice(nbrs)
            self.change_direction_buffer_time += 1
            if self.change_direction_buffer_time % 15 == 0:
                self.drift = (self.drift + 2) % 4
                self.nbr_prob_dist = self.get_nbr_prob_dist()
        else:
            # drift in one direction by choosing that direction with higher probability
            nbr_idx = list(range(8))
            cell_idx = np.random.choice(nbr_idx, p=self.nbr_prob_dist)
            cell = nbrs[cell_idx]
        return cell

    def borrow_energy(self):
        nbrs = self.model.grid.get_neighborhood(self.pos, moore=True, radius=ENERGY_TRANSMIT_RADIUS)
        for a in nbrs:
            if isinstance(a, Exploiter) and np.random.uniform < a.energy_share_prob:
                if a.energy > THRESHOLD_EXPLOITER:
                    self.energy += self.mining_rate
                    a.energy -= self.mining_rate
                    return True
        return False


    def step(self):
        # sense and add new energy resources into memory
        if self.model.schedule.time % SENSE_STEPS == 0:
            self.update_memory(max_range=self.sense_range)

        # share memory with other agents
        if self.model.schedule.time % COMMUNICATION_STEPS == 0:
            self.communicate(max_range=self.communication_range)

        # return to base to communicate
        if self.model.schedule.time % BASE_RETURN_INTERVAL == 0:
            self.is_returning_to_base = not self.is_returning_to_base

        # already reached an energy source
        if self.target is not None and self.target == self.pos:
            if self.is_returning_to_base is True:
                if self.energy <= MINING_FACTOR * THRESHOLD_EXPLORER:
                    # since it is returning to base, borrow energy from exploiters
                    success = self.borrow_energy()
                    if not success:
                        self.is_returning_to_base = False
                else:
                    self.is_returning_to_base = False
                    self.drift = random.choice(DIRECTIONS)

            elif self.mine_mode is True:
                if self.energy <= MINING_FACTOR * THRESHOLD_EXPLORER:
                    # mine energy from this location if energy is low
                    success = self.mine_energy()
                    if not success:
                        # energy has depleted from this src
                        self.update_target()
                else:
                    # sufficient energy has been replenished, continue exploration
                    self.mine_mode = False
                    self.target = None

        if not self.mine_mode:
            if self.is_returning_to_base:
                self.update_target()
                new_position = get_target_cell(self.target, self.pos)
            else:
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
        self.energy -= self.living_cost

        if not self.mine_mode and not self.is_returning_to_base and self.energy < THRESHOLD_EXPLORER:
            # when energy is low, switch to mining mode
            self.mine_mode = True

        if self.model.schedule.time % REPRODUCTION_STEPS == 0:
            if self.energy >= 2 * REPRODUCTION_ENERGY and np.random.uniform() < REPRODUCE_PROB:
                self.reproduce()

        self.age += 1
        if self.energy <= 0:
            self.model.ages.append((self.unique_id, self.age))
            self.die()

class Exploiter(SocietyMember):
    def __init__(self, unique_id, model, coop, e_prob):
        super().__init__(unique_id, model, coop)
        self.type = "exploiter"
        self.living_cost = max(0.5, np.random.normal(EXPLOITER_COST_MEAN, EXPLOITER_COST_STD))
        self.static_living_cost = max(0.2, self.living_cost / 4)
        self.communication_range = EXPLOITER_COMM_RANGE
        self.sense_range = EXPLOITER_SENSE_RANGE
        self.mining_rate = EXPLOITER_MINING_RATE
        self.is_at_base = False
        self.is_exploiting = False
        self.energy_share_prob = e_prob

    def die(self):
        ''' Removes the agent from gridworld and scheduler '''
        self.model.num_exploiters -= 1
        self.model.schedule.remove(self)
        self.model.grid.remove_agent(self)

    def move(self):
        self.update_target()

        # target is not updated since no resources in memory
        if self.target is None:
            self.target = random.choice(self.model.bases)
            self.is_exploiting = False

        if self.target == self.pos:
            if self.is_at_base:
                self.is_at_base = False
                self.is_exploiting = False
                self.energy -= self.static_living_cost

            elif self.energy <= MINING_FACTOR * THRESHOLD_EXPLOITER:
                success = self.mine_energy()
                if not success:
                    # source has depleted before full energy was replenished
                    self.update_target()
                    if self.target is None:
                        # if no other target is found, go back to base
                        self.target = random.choice(self.model.bases)
                        self.is_at_base = True
                    self.energy -= self.static_living_cost

            else:
                # sufficient energy has been restored
                # remove current pos from memory and return to base
                tmp = None
                idx = is_member(self.pos, self.memory)
                if idx:
                    tmp = self.memory[idx]
                    del self.memory[idx]

                self.target = random.choice(self.model.bases)
                self.is_at_base = True

                # add current pos back in memory to mine at later times
                if idx:
                    self.memory.append(tmp)
                self.energy -= self.static_living_cost

        else:
            # move towards target
            new_position = get_target_cell(self.target, self.pos)
            self.model.grid.move_agent(self, new_position)
            self.energy -= self.living_cost


    def step(self):
        self.age += 1
        # sense and add new energy resources into memory
        if self.model.schedule.time % SENSE_STEPS == 0:
            self.update_memory(max_range=self.sense_range)

        if not self.is_exploiting and self.energy < THRESHOLD_EXPLOITER:
            if len(self.memory) > 0:
                self.is_exploiting = True

        if self.is_exploiting:
            # once agent acquires knowledge of energy resources
            # move towards it
            self.move()

        elif np.random.uniform() < EXPLOITER_MOVE_PROB:
            # move randomly with small probability
            nbrs = self.model.grid.get_neighborhood(self.pos, moore=True, radius=1)
            new_position = random.choice(nbrs)
            self.model.grid.move_agent(self, new_position)
            self.energy -= self.living_cost

        else:
            self.energy -= self.static_living_cost

        # reproduce if having sufficient energy
        if self.model.schedule.time % REPRODUCTION_STEPS == 0:
            if self.energy >= 2 * REPRODUCTION_ENERGY and np.random.uniform() < REPRODUCE_PROB:
                self.reproduce()

        if self.energy <= 0:
            self.die()
            self.model.ages.append((self.unique_id, self.age))
