from flask import Flask, render_template, jsonify, g, request, session
from collections import deque
from markupsafe import escape

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

class GameManagement:
    def new_game(self, dimensions):
        board = [[0]*dimensions for i in range(dimensions)]
        for rowIndex in range(dimensions):
            for colIndex in range(dimensions):
                value = 0
                if rowIndex == 0 and colIndex == 0:
                    value = 2
                elif rowIndex == dimensions -1 and colIndex == dimensions -1:
                    value = -2
                board[rowIndex][colIndex] = value
        return board
    
    def is_game_over(self, board):
        player_1_points, player_2_points = self.compute_points(board)
        return len(board) * len(board[0]) == player_1_points + player_2_points
        
    def compute_points(self, board):
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
    
    
    
# Waiting database to be ready to remove session variable use
@app.route('/loadGame')
def loadGame():
    "return index template"
    session['game'] = {
        "board": GameManagement().new_game(10),
        "activePlayer": 1,
        "player1Points": 1,
        "player2Points": 1,
    }
    return jsonify(session['game'])

@app.route('/game')
def game():
    "return index template"
    return render_template('game.html')

    
@app.route('/')
def index():
    "return index template"
    return render_template('index.html')


@app.route('/move')
def move():
    direction = request.args['direction']
    player = int(request.args['player'])
    game = session["game"]
    board = game["board"]
    active_player = game["activePlayer"]
    if player != active_player:
        return "MOVE_USER_NOT_ACTIVE", 400
    if GameManagement().is_game_over(board):
        return jsonify(session['game'])
        
        
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
    if direction == 'UP':
        next_pos["row"] = next_pos["row"] -1
    if direction == 'DOWN':
        next_pos["row"] = next_pos["row"] + 1
    if direction == 'LEFT':
        next_pos["col"] = next_pos["col"] - 1
    if direction == 'RIGHT':
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
    gameOver = len(board) * len(board[0]) == player_1_points + player_2_points
           
                
    # Change user
    session["game"] = {
         "board": board,
         "activePlayer": - active_player if not gameOver else 0,
          "player1Points": player_1_points,
          "player2Points": player_2_points,
    }
        
    return jsonify(session['game'])
