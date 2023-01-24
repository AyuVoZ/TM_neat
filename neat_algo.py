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
CONFIG_PATH = os.path.join(local_dir, 'config-feedforward-test')
SIMULATION_TIME = 8.0
RELOAD_PATH = None
FITNESS_TYPE = "Distance"
REPLAY = False

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
    finish = False

    while time.time()-sim_time < SIMULATION_TIME:
        if get_data.data['finish']:
            gamepad.reset()
            sim_time = 0
            finish = True
        else:
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
            # if FITNESS_TYPE == "CP1" and get_data.data['curCP']==1:
            #     break

    if FITNESS_TYPE == "Distance": #objective : 750, simu_time = 15
        fitness = -3.42466*get_data.data['posx']+4767.123
    elif FITNESS_TYPE == "CP1": #objective : 7500, simu_time = 15
        if(get_data.data['curCP']==1):
            fitness = -get_data.data['lastCPTime']+15000
        elif get_data.data['curCP']>1:
            fitness = (-get_data.data['lastCPTime']+15000)*2
        else:
            fitness = -SIMULATION_TIME*1000+15000
    elif FITNESS_TYPE == "CP2": #objective : 13000, simu_time = 20
        if(get_data.data['curCP']==2):
            fitness = -1.85714*get_data.data['lastCPTime']+37142.86
        elif get_data.data['curCP']>2:
            fitness = (-1.85714*get_data.data['lastCPTime']+37142.86)*2
        else:
            fitness = 0.0
    elif FITNESS_TYPE == "CP3": #objecttive : 15000, simu_time = 30
        if(get_data.data['curCP']==3):
            fitness = -1*get_data.data['lastCPTime']+30000
        elif get_data.data['curCP']>3:
            fitness = (-1*get_data.data['lastCPTime']+30000)*2
        else:
            fitness = 0.0
    elif FITNESS_TYPE == "finish": #objective : 26000, simu_time = 45
        if finish:
            fitness = -1.36842*get_data.data['curRaceTime']+61578.95
            keyboard.press_and_release("enter")
        else:
            fitness = 0.0

    if REPLAY:
        get_data.stop_thread()
        time.sleep(1)
        gamepad2 = vg.VX360Gamepad()
        keyboard.press_and_release("r")
        time.sleep(0.1)
        gamepad2.left_joystick_float(x_value_float=0, y_value_float=1)
        gamepad2.update()
        time.sleep(0.1)
        gamepad2.reset()
        del gamepad2
        keyboard.press_and_release("enter")
        time.sleep(0.1)
        keyboard.press_and_release("enter")
        time.sleep(0.1)
        keyboard.press_and_release("escape")
        time.sleep(0.1)
        gamepad.left_joystick_float(x_value_float=0, y_value_float=1)
        gamepad.update()
        time.sleep(0.1)
        gamepad.reset()
        time.sleep(0.1)
        keyboard.press_and_release("enter")
        time.sleep(1)
        keyboard.press_and_release("enter")
        time.sleep(4)
        get_data.start_thread()

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

    pop = None
    if(RELOAD_PATH != None):
        popu = neat.Checkpointer.restore_checkpoint(RELOAD_PATH)
        pop = neat.Population(config, (popu.population, popu.species, popu.generation+1))
    else:
        pop = neat.Population(config)
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(True))
    checkpointer = neat.Checkpointer(1, 999999, "neat-checkpoint-")
    pop.add_reporter(checkpointer)
    if DEBUG:
        print(len(pop.population))

    winner = pop.run(eval_genomes, 200)
    if DEBUG:
        print(pop.config.fitness_threshold)
    checkpointer.save_checkpoint(config, pop.population, pop.species, pop.generation)

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
            elif sys.argv[i] == "-reload":
                RELOAD_PATH = os.path.join(local_dir, sys.argv[i+1])
                print(f"Using saved config {RELOAD_PATH}")
            elif sys.argv[i] == "-fitness":
                FITNESS_TYPE = sys.argv[i+1]
            elif sys.argv[i] == "-replay":
                REPLAY = True

    run()