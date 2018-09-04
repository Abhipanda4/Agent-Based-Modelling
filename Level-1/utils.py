import matplotlib.pyplot as plt
import numpy as np
import csv

x = [0, 20, 40, 60, 80, 100]
log_files = ["log_%d" %(i) for i in x]

mean_explorer_age = []
mean_exploiter_age = []
mean_age = []
mean_expected_age = []
age_dist = []

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

plt.figure(1)
plt.plot(x, mean_explorer_age, label="Mean Explorer Age")
plt.plot(x, mean_exploiter_age, label="Mean Exploiter Age")
plt.plot(x, mean_age, label="Mean Population Age")
plt.xlabel("Levels of Memory Sharing")
plt.ylabel("Number of timesteps the agents survived")
plt.legend()
plt.show()

for idx, i in enumerate(age_dist):
    plt.plot(list(range(len(i))), sorted(i), label="Memory sharing = " + str(x[idx]))
plt.xlabel("Agents in the world")
plt.ylabel("Number of timesteps the agents survived")
plt.legend()
plt.show()
