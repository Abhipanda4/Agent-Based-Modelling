import matplotlib.pyplot as plt
import numpy as np
import csv
import os

from config import *

log_files = ["logs/" + f for f in os.listdir("./logs")]

comm_level = "high"
img_root_dir = "images/" + comm_level
if not os.path.exists(img_root_dir):
    os.mkdir(img_root_dir)

print("This program is going to generate "\
        "plots for data collected with following energy parameters:")
print()
print("\tCooperation between agents: %f" %(COMMUNICATION_PROB))
print()
print("Level of communication specified is: %s" %(comm_level))
print()
user_response = input("Are you sure you want to continue?[y/n] ")
if user_response == "n" or user_response == "":
    sys.exit(0)

mean_explorer_age = []
mean_exploiter_age = []
mean_age = []
mean_expected_age = []
age_dist = []
energy_dist = []
n_exploiters = []
n_explorers = []

for log in log_files:
    with open(log, 'r') as fp:
        exploiter_age = []
        explorer_age = []
        population_age = []
        expected_age = []
        reader = csv.reader(fp)
        flag = True
        for row in reader:
            if row[0] == "ages":
                if flag:
                    age_dist.append([int(i) for i in row[1:]])

            elif row[0] == "total_energy":
                if flag:
                    energy_dist.append([float(i) for i in row[1:]])

            elif row[0] == "num_explorers":
                if flag:
                    n_explorers.append([int(i) for i in row[1:]])

            elif row[0] == "num_exploiters":
                if flag:
                    n_exploiters.append([int(i) for i in row[1:]])
                    flag = False

            else:
                explorer_age.append(float(row[0]))
                exploiter_age.append(float(row[1]))
                population_age.append(float(row[2]))
                expected_age.append(float(row[3]))

        mean_explorer_age.append(np.mean(explorer_age))
        mean_exploiter_age.append(np.mean(exploiter_age))
        mean_age.append(np.mean(population_age))
        mean_expected_age.append(np.mean(expected_age))

# plot of mean age of explorer, exploiter and whole population
plt.figure(1)
x = [i * 10 for i in range(11)]
plt.plot(x, mean_explorer_age, label="Mean Explorer Age")
plt.plot(x, mean_exploiter_age, label="Mean Exploiter Age")
plt.plot(x, mean_age, label="Mean Population Age")
plt.xlabel("Levels of Memory Sharing")
plt.ylabel("Number of timesteps the agents survived")
plt.legend()
plt.savefig(img_root_dir + "/mean_ages.png")
plt.show()

# variation of balance between population of exploiters and explorers
N = len(n_exploiters)
for i in range(N):
    x_axis = list(range(len(n_explorers[i])))
    plt.plot(x_axis, n_explorers[i], label="Number of Explorers")
    plt.plot(x_axis, n_exploiters[i], label="Number of Exploiters")
    plt.xlabel("Timesteps of world")
    plt.ylabel("Number of agents")
    plt.title("Explorers and Expoiters when memory sharing = %s" %(str(i/10)))
    plt.legend()
    plt.savefig(img_root_dir + "/num_agents_at_coop_%s.png" %(str(i * 10)))
    plt.show()

# plot of age distribution in the population
for idx, i in enumerate(age_dist):
    plt.plot(list(range(len(i))), sorted(i), label="Memory sharing = " + str(x[idx]))
plt.xlabel("Agents in the world")
plt.ylabel("Number of timesteps the agents survived")
plt.legend()
plt.savefig(img_root_dir + "/age_distribution.png")
plt.show()

# plot of energy variations in world with time
for idx, i in enumerate(energy_dist):
    plt.plot(list(range(len(i))), i, label="Memory sharing = " + str(x[idx]))
plt.xlabel("Timesteps")
plt.ylabel("Total energy available in world")
plt.title("Variation of total energy in the world with time")
plt.legend()
plt.savefig(img_root_dir + "/energy_variation.png")
plt.show()
