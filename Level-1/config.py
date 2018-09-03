# define all the global constants in this file

# margin from boundary where population gets initialized
POP_MARGIN = 20
POP_SPREAD = 20

# mean and std of energy of new born agents
MEAN_ENERGY = 150
STDDEV_ENERGY = 10

# number of energy resources
RESERVE_SIZE = 20

# capacity of energy resources
MEAN_RESERVE = 500
STDDEV_RESERVE = 20
DECAY_RATE = 1

# living cost for explorers(lower than exploiters)
EXPLORER_COST_MEAN = 0.5
EXPLORER_COST_STD = 0.25

# living cost for exploiters
EXPLOITER_COST_MEAN = 1.0
EXPLOITER_COST_STD = 0.5

# ranges for sensing and communication
EXPLORER_SENSE_RANGE = 15
EXPLORER_COMM_RANGE = 20
EXPLOITER_SENSE_RANGE = 8
EXPLOITER_COMM_RANGE = 5

# no of steps at which communication and discovery occur
SENSE_STEPS = 10
COMMUNICATION_STEPS = 10
COMMUNICATION_PROB = 0.3

# rate at which energy is extracted from energy resources
EXPLORER_MINING_RATE = 0.5
EXPLOITER_MINING_RATE = 1

# prob with which exploiter moves randomly
EXPLOITER_MOVE_PROB = 0.2

# expected ratio of explorers in the population
EXPLORER_RATIO = 0.1
DIRECTIONS = [0, 1, 2, 3]

# energy threshold at which agent looks actively for mining energy resources
THRESHOLD_EXPLORER = 50
THRESHOLD_EXPLOITER = 80
MINING_FACTOR = 2

# reproduction related parameters
REPRODUCTION_STEPS = 20
REPRODUCTION_ENERGY = 30
REPRODUCE_PROB = 0.05
INHERITANCE_PROB = 0.75

# spawn new energy resources
NEW_ENERGY_PROB = 0.2
NEW_ENERGY_STEPS = 75

# probability of sharing a memory fragment with another agent
SHARE_PROB = 0.5
