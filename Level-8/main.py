import numpy as np
import argparse

from server import server
from model import World

def main():
    # constants specific to statistic collection of simulations
    NUM_SIMULATIONS = 2

    parser = argparse.ArgumentParser(description="Visualization controls")
    parser.add_argument("--visualize",  action="store_true", help="whether to visualize on browser")
    args = parser.parse_args()

    if args.visualize:
        server.launch()

    else:
        coops = np.arange(0.0, 1.1, 0.1)

        ## TESTING ##
        # coops = [0.5]
        #############

        e_prob = 0.5
        for coop in coops:
            print("Simulating with cooperation level %.2f" %(coop))
            f_name = "logs/log_%d" %(coop * 100)
            with open(f_name, 'w+') as f:
                for _ in range(NUM_SIMULATIONS):
                    model = World(100, coop, e_prob)
                    while model.schedule.time < 3000 and len(model.schedule.agents) != 0:
                        # simulate till there are agents in the world
                        model.step()

                    # explorer mean age
                    mean_explorer_age = np.mean([model.ages[i] for i in model.ages if "explorer" in i])
                    # exploiter mean age
                    mean_exploiter_age = np.mean([model.ages[i] for i in model.ages if "exploiter" in i])
                    # entire population mean age
                    mean_age = np.mean([model.ages[i] for i in model.ages])
                    # mean expected age based on initial values
                    expected_age = np.mean(model.expected_ages)

                    ages = ', '.join([str(model.ages[i]) for i in model.ages])
                    memoryLens = ', '.join([str(model.memoryLens[i]) for i in model.memoryLens])

                    total_energy = ', '.join([str(i) for i in model.energy_tracker])
                    num_explorers = ', '.join([str(i[0]) for i in model.member_tracker])
                    num_exploiters = ', '.join([str(i[1]) for i in model.member_tracker])

                    f.write("ages, " + ages + "\n")
                    f.write("memoryLens, " + memoryLens + "\n")
                    f.write("total_energy, " + total_energy + "\n")
                    f.write("num_explorers, " + num_explorers + "\n")
                    f.write("num_exploiters, " + num_exploiters + "\n")
                    f.write("%.5f, %.5f, %.5f, %.5f\n" %(mean_explorer_age, mean_exploiter_age, mean_age, expected_age))

if __name__ == "__main__":
    main()
