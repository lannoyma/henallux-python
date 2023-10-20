import pickle
from flask import Flask, g, abort
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from .models import Game, GameType, Direction
from sqlalchemy import DateTime, LargeBinary
from datetime import datetime
from collections import deque

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Alchemy must be initiated before import models
class GameDbEntity(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    started_at = db.Column(DateTime, nullable=False, default=datetime.utcnow)  # Renommée et configurée avec une valeur par défaut
    active_player = db.Column(db.SmallInteger, nullable=False)
    game_type = db.Column(db.String(20), nullable=False, default='HUMAN_VS_HUMAN')  # Mis à jour avec la valeur par défaut correcte
    board = db.Column(LargeBinary)

    __table_args__ = (
        db.CheckConstraint(game_type.in_(['HUMAN_VS_HUMAN', 'HUMAN_VS_AI', 'AI_VS_AI']), name='check_game_type'),
    )

    def __repr__(self):
        return f'<Game {self.id}>'

with app.app_context():
    db.create_all()
    print('hello')

class GameManagement:

    def get_game(self, game_id: int):
        return self.convert_game_entity_to_game(db.session.query(GameDbEntity).get(game_id))
    
    def new_game(self, dimensions):
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
                
                
        game = GameDbEntity(
            active_player=1,
            game_type='HUMAN_VS_HUMAN',
            board=pickle.dumps(board))
        
        try:
            db.session.add(game)
            db.session.commit()
            return self.convert_game_entity_to_game(game)
        except Exception as e:
            db.session.rollback()
            raise e
            
    def move(self, game_id: int, direction: Direction, player: int):
        game_db_entity = db.session.query(GameDbEntity).get(game_id)
        game = self.convert_game_entity_to_game(game_db_entity)
        board = game.board
        active_player = game.active_player
        if player != active_player:
            abort(400, description="MOVE_USER_NOT_ACTIVE")
        
        if GameManagement().is_game_over(board):
            return jsonify(game)
            
            
        current_pos = None
        for i, line in enumerate(board):
            for j, cell in enumerate(line):
                columns_count = j
                if cell == 2 * player: # Will find -2 or 2 depending on player's value
                    current_pos = {
                        "row": i,
                        "col":j 
                    }
                    
                    
        next_pos = {
            "row": current_pos["row"],
            "col": current_pos["col"],
        }
        if direction == Direction.UP:
            next_pos["row"] = next_pos["row"] -1
        elif direction == Direction.DOWN:
            next_pos["row"] = next_pos["row"] + 1
        if direction == Direction.LEFT:
            next_pos["col"] = next_pos["col"] - 1
        if direction == Direction.RIGHT:
            next_pos["col"] = next_pos["col"] + 1
        
        # Check if new position is correct according to grid dimensions
        if next_pos["row"] < 0 or next_pos["row"] >= len(board) or next_pos["col"] < 0 or next_pos["col"] >= len(board[0]):
            return "MOVE_OUT_OF_GRID", 400
        # Check if new position does not belong to other player
        if board[next_pos["row"]][next_pos["col"]] == -1 * player:
            return "MOVE_CELL_BELONGS_TO_OPPONENT", 400
        # Check opponent is not on new position
        if board[next_pos["row"]][next_pos["col"]] == -2 * player:
            return "MOVE_CELL_BELONGS_TO_OPPONENT", 400
        
        # Set old position belong to current player
        board[current_pos["row"]][current_pos["col"]] = player
        
        # Set new position
        board[next_pos["row"]][next_pos["col"]] = 2 * player
        
        
        # Search for enclos
        GameManagement().update_board_accoring_to_enclos(board)
        
        # Check if game is over + compute points
        empty_cell_found = False
        player_1_points, player_2_points = GameManagement().compute_points(board)
        game_over = len(board) * len(board[0]) == player_1_points + player_2_points
        
        try:
            game_db_entity.board = pickle.dumps(board)
            game_db_entity.active_player = - active_player if not game_over else 0
            db.session.commit()
            return self.convert_game_entity_to_game(game_db_entity)
        except Exception as e:
            db.session.rollback()
            raise e
            
        
    def is_game_over(self, board):
        """ Check if the game is over, based on the board state.

        Args:
            board (list): The 2D list representing the game board.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        player_1_points, player_2_points = self.compute_points(board)
        return len(board) * len(board[0]) == player_1_points + player_2_points
        
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
        
    def update_board_accoring_to_enclos(self, board):
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
                    
        self.bfs(board, p1i, p1j, reachable_by_player1, 1)
        self.bfs(board, p2i, p2j, reachable_by_player2, -1)
        
        for i in range(rows):
            for j in range(cols):
                if board[i][j] == 0:
                    if reachable_by_player1[i][j] and not reachable_by_player2[i][j]:
                        board[i][j] = 1
                    elif not reachable_by_player1[i][j] and reachable_by_player2[i][j]:
                        board[i][j] = -1
        return board

    def bfs(self, board, i, j, reachable, player):
        """
        Breadth-First Search to explore reachable positions for a player on the board.

        Args:
            board (list): The 2D list representing the game board.
            i (int): Starting row index for BFS.
            j (int): Starting column index for BFS.
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
                    
    def convert_game_entity_to_game(self, game_entity: GameDbEntity):
        board = pickle.loads(game_entity.board)
        player_1_points, player_2_points = self.compute_points(board)
        return Game(
            id = game_entity.id,
            started_at = game_entity.started_at,
            active_player = game_entity.active_player,
            game_type = GameType.__members__.get(game_entity.game_type),
            board = board,
            player_1_points = player_1_points,
            player_2_points = player_2_points)
            
    