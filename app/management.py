import pickle
from flask import Flask, g, abort
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from .models import Game, GameType, Direction
from sqlalchemy import DateTime, LargeBinary
from datetime import datetime
from collections import deque
import logging as lg

class GameManagement:
    # ----------------------------------------------------------- PUBLIC METHODS -------------------------------------------------------------------------------
    def new_game(self, dimensions, game_type = GameType.HUMAN_VS_AI):
        """ Initialize a new game board with the given dimensions.

        Args:
            dimensions (int): The width/height of the board.

        Returns:
            list: A 2D list representing the game board.
        """
        board = [[0]*dimensions for i in range(dimensions)]
        for row_index in range(dimensions):
            for col_index in range(dimensions):
                value = 0
                if row_index == 0 and col_index == 0:
                    value = 2
                elif row_index == dimensions -1 and col_index == dimensions -1:
                    value = -2
                board[row_index][col_index] = value
        return board
     
    def move(self, board, active_player,direction: Direction, player):
        lg.warning('Move player:' + str(player) + ' to ' + str(direction) + ' with active player = ' + str(active_player))
        if player != active_player:
            abort(400, description="MOVE_USER_NOT_ACTIVE")
        if self.__is_game_over(board):
            return board, 0
        possible_directions = self.get_possible_directions(board, player)
        if direction not in possible_directions:
            abort(400, description="DEPLACEMENT_NOT_ALLOWED")
        
        current_pos = self.__get_player_position(board, player)
        next_pos = self.__get_next_position(current_pos, direction) 
        
        # Set old position belong to current player
        board[current_pos["row"]][current_pos["col"]] = player
        
        # Set new position
        board[next_pos["row"]][next_pos["col"]] = 2 * player
        lg.warning('Updated board with new position ' + str(board))

        self.__update_board_according_to_enclos(board)
        lg.warning('Updated board with enclos' + str(board))
        game_over = self.__is_game_over(board)
        return board, 0 if game_over else -active_player

    def compute_points(self, board):
        """
        Compute the points for each player based on the board state.

        Args:
            board (list): The 2D list representing the game board.

        Returns:
            tuple: A tuple containing the points of player 1 and player 2.
        """
        player_1_points = 0
        player_2_points = 0
        for x in range(len(board)):
            for y in range(len(board[x])):
                value = board[x][y]
                if value > 0:
                    player_1_points += 1
                elif value < 0:
                    player_2_points += 1
        return player_1_points, player_2_points
        
    def get_possible_directions(self, board, player):
        current_pos = self.__get_player_position(board, player)
        directions = []
        for direction in Direction:
            if self.__is_cell_available(board, self.__get_next_position(current_pos, direction), player):
                directions.append(direction)
        return directions

# ----------------------------------------------------------- PRIVATE METHODS -------------------------------------------------------------------------------
        
    def __get_next_position(self, pos, direction):
        next_pos = {
                "row": pos['row'],
                "col": pos['col']
                }
        if direction == Direction.UP:
            next_pos["row"] = next_pos["row"] -1
        elif direction == Direction.DOWN:
            next_pos["row"] = next_pos["row"] + 1
        if direction == Direction.LEFT:
            next_pos["col"] = next_pos["col"] - 1
        if direction == Direction.RIGHT:
            next_pos["col"] = next_pos["col"] + 1
        return next_pos
        
        
    def __belong_cell_to_opponent(self, board, pos, current_player):
        value = board[pos['row']][pos['col']]
        return value == -1 * current_player or value == -1 * current_player

    def __is_cell_in_board(self, board, pos):
        return pos['row'] >= 0 and pos['row'] < len(board) and pos['col'] >= 0 and pos['col'] < len(board[0])

    def __is_cell_available(self, board, pos, player):
        if not self.__is_cell_in_board(board, pos) :
            return False
        return not self.__belong_cell_to_opponent(board, pos, player)
    
        
         
    def __get_player_position(self, board, player):
        for i, line in enumerate(board):
            for j, cell in enumerate(line):
                columns_count = j
                if cell == 2 * player: # Will find -2 or 2 depending on player's value
                    return {
                        "row": i,
                        "col":j 
                    }
        abort(500, description="Unable to find player position")
        
    def __is_game_over(self, board):
        """ Check if the game is over, based on the board state.

        Args:
            board (list): The 2D list representing the game board.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        player_1_points, player_2_points = self.compute_points(board)
        return len(board) * len(board[0]) == player_1_points + player_2_points
        
    def __update_board_according_to_enclos(self, board):
        """
        Update the board according to the game's enclosure rules.

        Args:
            board (list): The 2D list representing the game board.

        Returns:
            list: The updated board.
        """
        rows, cols = len(board), len(board[0])
        reachable_by_player1 = [[False] * cols for _ in range(rows)]
        reachable_by_player2 = [[False] * cols for _ in range(rows)]
        
        # Find the positions of the players
        p1i = p1j = p2i = p2j = -1
        for i, row in enumerate(board):
            for j, cell in enumerate(row):
                if cell == 2:
                    p1i, p1j = i, j
                elif cell == -2:
                    p2i, p2j = i, j
                    
        self.__bfs(board, p1i, p1j, reachable_by_player1, 1)
        self.__bfs(board, p2i, p2j, reachable_by_player2, -1)
        
        for i in range(rows):
            for j in range(cols):
                if board[i][j] == 0:
                    if reachable_by_player1[i][j] and not reachable_by_player2[i][j]:
                        board[i][j] = 1
                    elif not reachable_by_player1[i][j] and reachable_by_player2[i][j]:
                        board[i][j] = -1
        return board

    def __bfs(self, board, i, j, reachable, player):
        """
        Breadth-First Search to explore reachable positions for a player on the board.

        Args:
            board (list): The 2D list representing the game board.
            i (int): Starting row index for __bfs.
            j (int): Starting column index for __bfs.
            reachable (list): 2D boolean list indicating whether a cell is reachable.
            player (int): The player to check reachability for.
        """
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        queue = deque([(i, j)])
        
        while queue:
            x, y = queue.popleft()
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(board) and 0 <= ny < len(board[0]) and not reachable[nx][ny] and (
                    board[nx][ny] == 0 or board[nx][ny] == player or board[nx][ny] == player * 2):
                    reachable[nx][ny] = True
                    queue.append((nx, ny))
            
    