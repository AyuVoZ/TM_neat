import os
import pickle
import time
import neat
import visualize
import numpy as np
import sys

#Control car and environement
import keyboard
import vgamepad as vg

#import other files
import Lidar
import get_data

#Init variable for the simulation
lidar = Lidar.Lidar()
gamepad = vg.VX360Gamepad()

# start the thread
get_data.start_thread()

DEBUG = False
local_dir = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(local_dir, 'config-feedforward-start-hidden-2')
SIMULATION_TIME = 20.0

# Use the NN network phenotype and the discrete actuator force function.
def eval_genome(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    # Run the given simulation for up to num_steps time steps.
    sim_time = time.time()
    fitness = 0.0
    #restart race
    keyboard.press('delete')
    keyboard.release('delete')
    is_forward = None

    while time.time()-sim_time < simulation_seconds:
        inputs = lidar.lidar_20(False)
        speed_raw = get_data.data['speed']
        speed_raw = speed_raw/200-1
        speed = np.float32(speed_raw)
        inputs = np.append(inputs, speed)
        inputs = np.array(inputs, dtype=np.float32)
        action = net.activate(inputs)
        
        # Apply action to the game
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

    fitness = get_data.data['distance']*(get_data.data['curCP']+1)

    if DEBUG: 
        print(f"[{time.ctime()}] Fitness : {fitness}")

    # The genome's fitness is its worst performance across all runs.
    return fitness


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)


def run():
    # Load the config file, which is assumed to live in
    # the same directory as this script.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         CONFIG_PATH)

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
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)):
            if sys.argv[i] == '-d':
                DEBUG = True
                print("DEBUG MODE ON")
            elif sys.argv[i] == '-config':
                CONFIG_PATH = os.path.join(local_dir, sys.argv[i+1]) 
                print(f"Using config file {CONFIG_PATH}")
            elif sys.argv[i] == "-time":
                SIMULATION_TIME = float(sys.argv[i+1])

    run()