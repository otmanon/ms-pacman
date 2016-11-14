# -*- coding: utf-8 -*-

import os
import pickle
import random
from transition_model import get_next_state
from game_map_objects import GameMapObjects


class Learner(object):

    WEIGHTS_FILE = "weights.p"

    def __init__(self, alpha=0.0001, gamma=0.):
        if not os.path.isfile(self.WEIGHTS_FILE):
            self.weights = [0] * 5 * 49
            # self.weights[12] = -100
            # self.weights[37] = 200
            # self.weights[62] = 10
            # self.weights[87] = 50
            # self.weights[112] = 100
        else:
            self.weights = pickle.load(open(self.WEIGHTS_FILE, "rb"))

        self.alpha = alpha
        self.gamma = gamma

    def _get_utility(self, state):
        state_rewards = self._get_state(state)
        return sum(w * r for w, r in zip(self.weights, state_rewards))

    def get_optimal_action(self, game):
        optimal_utility = float("-inf")
        optimal_actions = [0]  # noop.
        available_actions = game.available_actions()

        for a in available_actions:
            next_state = get_next_state(game, a)
            utility = self._get_utility(next_state)
            if utility > optimal_utility:
                optimal_utility = utility
                optimal_actions = [a]
            elif utility == optimal_utility:
                optimal_actions.append(a)

        return (random.choice(optimal_actions), optimal_utility)

    def update_weights(self, prev_state, game, guess_utility, reward):
        state_rewards = self._get_state(prev_state)
        real_utility = reward + self.gamma * self._get_utility(game.sliced_map.map)
        print(guess_utility, real_utility)

        error = 0.5 * (real_utility - guess_utility) ** 2
        print(error)
        for i in range(5 * 49):
            self.weights[i] += \
                self.alpha * (real_utility - guess_utility) * state_rewards[i]

    def _get_state(self, game_map):
        all_state = game_map.flatten()
        size = len(all_state)

        total_state = [0] * (5 * size)

        for i in range(size):
            classification = all_state[i]
            if classification == GameMapObjects.BAD_GHOST:
                total_state[i] = 1
            elif classification == GameMapObjects.GOOD_GHOST:
                total_state[i + size] = 1
            elif classification == GameMapObjects.PELLET:
                total_state[i + size * 2] = 1
            elif classification == GameMapObjects.POWER_UP:
                total_state[i + size * 3] = 1
            elif classification == GameMapObjects.FRUIT:
                total_state[i + size * 4] = 1

        return total_state

    def human_readable_weights(self):
        s = ""
        for i in range(5 * 49):
            s += "{:+3.2f} ".format(self.weights[i])
            if i % 7 == 6:
                s += "\n"
            if i % 49 == 48:
                s += "\n"
        return s

    def save(self):
        pickle.dump(self.weights, open(self.WEIGHTS_FILE, "wb"))
