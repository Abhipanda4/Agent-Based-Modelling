import numpy as np
import argparse

from server import server
from model import *

parser = argparse.ArgumentParser(description="Visualization controls")
parser.add_argument("--visualize",  action="store_true", help="whether to visualize on browser")
args = parser.parse_args()

if args.visualize:
    server.launch()

else:
    for _ in range(100):
        model = World(100)
        while len(model.schedule.agents) != 0:
            # simulate till there are agents in the world
            model.step()

        mean_age = np.mean([i[1] for i in model.ages])
        expected_age = np.mean(model.expected_ages)
        print(mean_age, expected_age)
