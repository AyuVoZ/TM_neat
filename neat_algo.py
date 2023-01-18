"""
Single-pole balancing experiment using a feed-forward neural network.
"""

from __future__ import print_function

import os
import pickle
import time
import neat
import visualize

import keyboard
import vgamepad as vg

import AI_trackmania

runs_per_net = 5
simulation_seconds = 13.0
time.sleep(2)
#get image
lidar = AI_trackmania.Lidar()
gamepad = vg.VX360Gamepad()


# Use the NN network phenotype and the discrete actuator force function.
def eval_genome(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    fitnesses = []

    # Run the given simulation for up to num_steps time steps.
    sim_time = time.time()
    fitness = 0.0
    keyboard.press('backspace')
    keyboard.release('backspace')
    is_forward = None
    while time.time()-sim_time < simulation_seconds:
        inputs = lidar.lidar_20(False)
        action = net.activate(inputs)
        # Apply action to the simulated cart-pole
        if(action[0]>0):
            if(not is_forward):
                gamepad.left_trigger_float(value_float=0)
            is_forward = True
            gamepad.right_trigger_float(value_float=action[0])
        else:
            if(is_forward):
                gamepad.right_trigger_float(value_float=0)
            is_forward= False
            gamepad.left_trigger_float(value_float=-action[0])
        gamepad.left_joystick_float(x_value_float=action[1], y_value_float=0)
        gamepad.update()

    fitness = lidar.dist()

    fitnesses.append(fitness)

    # The genome's fitness is its worst performance across all runs.
    return min(fitnesses)


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)


def run():
    # Load the config file, which is assumed to live in
    # the same directory as this script.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    pop = neat.Population(config)
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(True))

    winner = pop.run(eval_genomes, 200)

    # Save the winner.
    with open('winner-feedforward', 'wb') as f:
        pickle.dump(winner, f)

    print(winner)

    # visualize.plot_stats(stats, ylog=True, view=True, filename="feedforward-fitness.svg")
    # visualize.plot_species(stats, view=True, filename="feedforward-speciation.svg")

    # node_names = {-1: 'x', -2: 'dx', -3: 'theta', -4: 'dtheta', 0: 'control'}
    # visualize.draw_net(config, winner, True, node_names=node_names)

    # visualize.draw_net(config, winner, view=True, node_names=node_names,
    #                    filename="winner-feedforward.gv")
    # visualize.draw_net(config, winner, view=True, node_names=node_names,
    #                    filename="winner-feedforward-enabled.gv", show_disabled=False)
    # visualize.draw_net(config, winner, view=True, node_names=node_names,
    #                    filename="winner-feedforward-enabled-pruned.gv", show_disabled=False, prune_unused=True)


if __name__ == '__main__':
    run()