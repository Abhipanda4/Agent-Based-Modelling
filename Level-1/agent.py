from mesa import Agent

from config import *

class SocietyMember(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # define all common attributes here
        pass

    def step(self):
        raise NotImplementedError

class Explorer(SocietyMember):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # attributes related to requirements, communication
        pass

    def step(self):
        pass

class Exploiter(SocietyMember):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # attributes related to requirements, communication
        pass

    def step(self):
        pass

