import random

class AIManagement:
    def get_move(self, board, active_player, possible_directions):
        random_index = random.randint(0, len(possible_directions) - 1)
        return possible_directions[random_index]