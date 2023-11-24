from flask import abort
from .models import Game, GameType, Direction
from .ai import AIManagement
from collections import deque
import logging as lg
from typing import List
import random


class GameManagement:
    # ----------------------------------------------------------- PUBLIC METHODS -------------------------------------------------------------------------------
    def new_game(self, dimensions: int, game_type = GameType.HUMAN_VS_AI):
        """
        Create a new game board with the specified dimensions and game type.

        Parameters:
            - dimensions (int): The dimensions (size) of the game board.
            - game_type (GameType): The type of the game (default: GameType.HUMAN_VS_AI).

        Returns:
            List[List[int]]: A 2D list representing the initialized game board.

        This method creates a new game board with the specified dimensions and initializes
        it with values for the starting positions of players. The game board is represented
        as a 2D list of integers, where:
            - 1 indicates cell belonging to Player 1
            - 2  indicates Player 1 position
            - -1 indicates cell belonging to Player 2
            - -2  indicates Player 2 position
        Example:
            new_board = self.new_game(8)  # Creates a new 8x8 game board for HUMAN_VS_AI.
        """
        if dimensions > 100:
            abort(500, description="BOARD_TOO_BIG")
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
     
    def move(self, board: List[List[int]], active_player: int , direction: Direction, player: int):
        """
        Perform a move on the game board.

        Parameters:
            - board (List[List[int]]): The current state of the game board.
            - active_player (int): The player who is currently taking their turn.
            - direction (Direction): The direction in which to make the move.
            - player (int): The player making the move.

        Returns:
            Tuple[List[List[int]], int]: A tuple containing the updated game board and the
            result of the move (0 for game over, -active_player otherwise).

        This method performs a move on the game board in the specified direction for the
        given player. It checks if the move is valid, updates the board accordingly, and
        checks for enclosures and game over conditions.

        Example:
            new_board, move_result = self.move(current_board, active_player, Direction.UP, player)
        """
        print('Move player:' + str(player) + ' to ' + str(direction) + ' with active player = ' + str(active_player))
        self.__print_board(board)
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
        #lg.warning('Updated board with new position ' + str(board))

        print('After move')
        self.__print_board(board)
        self.__update_board_according_to_enclos(board)
        print('After enclos')
        self.__print_board(board)
        #lg.warning('Updated board with enclos' + str(board))
        game_over = self.__is_game_over(board)
        return board, 0 if game_over else -active_player
        
    def automatic_move(self, board, active_player, game_type):
        """
        Perform an automatic move in the game.

        Parameters:
            - board (bi dimensional array of int): A bi-directional array representing the current state of the game.
            - active_player (int): The active player: Possible values values are -1 and 1
            - game_type (GameType): The game type (e.g., GameType.HUMAN_VS_AI).

        Returns:
            tuple: A tuple containing the updated board and the active player.

        If active_player is -1 and game_type is GameType.HUMAN_VS_AI, the method attempts
        to make an automatic move for the AI by selecting a random direction among the
        available directions. If no possible directions are available, it returns the
        unchanged board and the active player. Otherwise, it makes the move and returns
        the updated board with the new active player.

        Example:
            board, active_player = automatic_move(board, active_player, GameType.HUMAN_VS_AI)
        """
        if  active_player == -1 and game_type == GameType.HUMAN_VS_AI:
            possible_directions = self.get_possible_directions(board,  active_player)
            direction = AIManagement().get_move(board,  active_player, possible_directions)
            if  direction != None :
                return self.move(board, active_player, direction, active_player)
        return board, active_player

    def compute_points(self, board: List[List[int]]):
        """
        Compute the points for each player based on the board state.

        Args:
            board (list): The 2D list representing the game board.

        Returns:
            tuple: A tuple containing the points of player 1 and player 2.
        """
        # functionnal
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
        
    def get_possible_directions(self, board: List[List[int]], player: int):
        """
        Get a list of possible directions for a player's move on the game board.

        Parameters:
            - board (List[List[int]]): The current state of the game board.
            - player (int): The player for whom to find possible directions.

        Returns:
            List[Direction]: A list of directions in which the player can make a move.

        This method calculates and returns a list of possible directions in which a player
        can make a move on the game board based on the current game state and player's
        position. The directions are represented as Direction enum values.

        Example:
            possible_directions = self.get_possible_directions(current_board, active_player)
        """
        current_pos = self.__get_player_position(board, player)
        directions = []
        for direction in Direction:
            if self.__is_cell_available(board, self.__get_next_position(current_pos, direction), player):
                directions.append(direction)
        return directions

# ----------------------------------------------------------- PRIVATE METHODS -------------------------------------------------------------------------------
        
    def __get_next_position(self, pos, direction: Direction):
        """
        Get the next position based on the current position and direction.

        Parameters:
            - pos (Dict[int, int]): The current position as a dictionary with 'row' and 'col'.
            - direction (Direction): The direction in which to calculate the next position.

        Returns:
            Dict[int, int]: A dictionary representing the next position with 'row' and 'col' keys.

        This private method calculates and returns the next position based on the current
        position and the specified direction. The result is a dictionary with 'row' and 'col'
        keys representing the new position coordinates.

        Example:
            next_position = self.__get_next_position(current_position, Direction.UP)
        """
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

    def __is_cell_available(self, board: List[List[int]], pos, player: int):
        """
        Check if a cell at a given position is available for the current player.

        Parameters:
            - board (List[List[int]]): The current state of the game board.
            - pos (Dict[int, int]): The position to check as a dictionary with 'row' and 'col'.
            - player (int): The current player for whom to check cell availability.

        Returns:
            bool: True if the cell is available for the current player, False otherwise.

        This private method checks if a cell at a given position is available for the current
        player to make a move. It returns True if the cell is within the board's bounds and
        does not belong to the opponent of the current player.

        Example:
            is_available = self.__is_cell_available(current_board, cell_position, active_player)
        """
        if not self.__is_cell_in_board(board, pos) :
            return False
        return not self.__belong_cell_to_opponent(board, pos, player)
        
    def __belong_cell_to_opponent(self, board: List[List[int]], pos, current_player: int):
        """
        Check if a cell on the game board belongs to the opponent of the current player.

        Parameters:
            - board (List[List[int]]): The current state of the game board.
            - pos (Dict[int, int]): The position to check as a dictionary with 'row' and 'col'.
            - current_player (int): The current player for whom to check cell ownership.

        Returns:
            bool: True if the cell belongs to the opponent, False otherwise.

        This private method checks if a cell on the game board belongs to the opponent of
        the current player. It returns True if the cell value is equal to the negation of
        the current player's value.

        Example:
            is_opponent_cell = self.__belong_cell_to_opponent(current_board, cell_position, active_player)
        """
        value = board[pos['row']][pos['col']]
        return value == -1 * current_player or value == -2 * current_player

    def __is_cell_in_board(self, board: List[List[int]], pos):
        """
        Check if a given position is within the bounds of the game board.

        Parameters:
            - board (List[List[int]]): The current state of the game board.
            - pos (Dict[int, int]): The position to check as a dictionary with 'row' and 'col'.

        Returns:
            bool: True if the position is within the board's bounds, False otherwise.

        This private method checks if a given position is within the bounds of the game board.
        It returns True if the position's row and column values are within the valid range of
        the board dimensions.

        Example:
            is_in_board = self.__is_cell_in_board(current_board, cell_position)
        """
        return pos['row'] >= 0 and pos['row'] < len(board) and pos['col'] >= 0 and pos['col'] < len(board[0])
    
        
         
    def __get_player_position(self, board: List[List[int]], player: int):
        """
        Get the position of a player on the game board.

        Parameters:
            - board (List[List[int]]): The current state of the game board.
            - player (int): The player for whom to find the position.

        Returns:
            Dict[int, int]: A dictionary representing the position with 'row' and 'col' keys.

        This private method searches the game board to find the position of a player's piece.
        It returns a dictionary with 'row' and 'col' keys representing the player's position.

        Example:
            player_position = self.__get_player_position(current_board, active_player)
        """
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

    def __bfs(self, board, i, j, reachable, player: int):
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
            
    def __print_board(self, board):
        for row in board:
            # Parcours des éléments de chaque ligne
            for element in row:
                print(element, end=' ')
                # Passage à la ligne suivante après chaque ligne
            print('')