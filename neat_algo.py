"""
Single-pole balancing experiment using a feed-forward neural network.
"""

from __future__ import print_function

import os
import pickle
import time
import neat
import visualize
import socket
import threading
from struct import unpack
import numpy as np

import keyboard
import vgamepad as vg

import AI_trackmania

simulation_seconds = 13.0
time.sleep(2)
#get image
lidar = AI_trackmania.Lidar()
gamepad = vg.VX360Gamepad()

#Start a thread to get the data
data = {}

def get_data(s):
        data = dict()
        #data['time'] = time.ctime()
        data['speed'] = unpack(b'@f', s.recv(4))[0] # speed
        data['distance'] = unpack(b'@f', s.recv(4))[0] # distance
        data['finish'] = unpack(b'@f', s.recv(4))[0] # finish
        data['curCP'] = unpack(b'@f', s.recv(4))[0] # finish
        data['lastCPTime'] = unpack(b'@f', s.recv(4))[0] # finish
        data['curRaceTime'] = unpack(b'@f', s.recv(4))[0] # finish
        return data

# function that captures data from openplanet    
def data_getter_function():
        global data
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("127.0.0.1", 9000))
                while True:
                        data = get_data(s)

# start the thread
data_getter_thread = threading.Thread(target=data_getter_function, daemon=True)
data_getter_thread.start()


# Use the NN network phenotype and the discrete actuator force function.
def eval_genome(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    # Run the given simulation for up to num_steps time steps.
    sim_time = time.time()
    fitness = 0.0
    keyboard.press('delete')
    keyboard.release('delete')
    is_forward = None

    cp1_passed = False
    cp1_time = 0
    

    while time.time()-sim_time < simulation_seconds:
        inputs = lidar.lidar_20(False)
        speed_raw = data['speed']
        speed_raw = speed_raw/200-1
        speed = np.float32(speed_raw)
        inputs = np.append(inputs, speed)
        inputs = np.array(inputs, dtype=np.float32)
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

    fitness = data['distance']*(data['curCP']+1)

    # print(f"[{time.ctime()}] Fitness : {fitness}")

    # The genome's fitness is its worst performance across all runs.
    return fitness


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