import neat
import os

local_dir = os.path.dirname(__file__)
RELOAD_PATH = os.path.join(local_dir, "neat-checkpoint-1")
popu = neat.Checkpointer.restore_checkpoint(RELOAD_PATH)
print(popu.fitness_criterion)
# CONFIG_PATH = os.path.join(local_dir, "config-feedforward-test")
# config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
#                          neat.DefaultSpeciesSet, neat.DefaultStagnation,
#                          CONFIG_PATH)
# pop = neat.Population(config, (popu.population, popu.species, popu.generation+1))
# checkpointer = neat.Checkpointer(1, 999999, "test-")
# pop.add_reporter(checkpointer)
# checkpointer.save_checkpoint(config, pop.population, pop.species, pop.generation)
# print(pop.fitness_criterion)
