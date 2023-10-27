from flask import Flask, render_template, jsonify, g, request, session, abort
from collections import deque
from markupsafe import escape
from .models import Game, Direction, GameType
from .dao import Dao
from .management import GameManagement
import json
import pickle
import random
    
app = Flask(__name__)
app.config.from_object('config')
dao = Dao()
management = GameManagement()
    
# Waiting database to be ready to remove session variable use
@app.route('/loadGame')
def loadGame():
    """
    Initialize a new game session and respond with the initial game state.

    Returns:
        JSON: JSON data containing the initial game state.
    """
    game_id = request.args.get('gameId')
    if game_id is None:
        game_type = GameType.HUMAN_VS_AI
        board  = management.new_game(10, game_type)
        game = dao.create_one_game(board, game_type)
    else:
        print ('Game_id' + str(game_id))
        game = dao.get_one_game_by_id(game_id)
        if game is None:
            abort(404, description="NO_GAME_FOUND")
        board = pickle.loads(game.board)
        board, active_player = automatic_move(board, game.active_player, GameType[game.game_type])
        if active_player != game.active_player:
            game = dao.update_one_game(game.id, board, active_player)
    return convert_to_json(game)

@app.route('/game')
def game():
    """
    Render the game HTML template.

    Returns:
        HTML: Rendered HTML for the game.
    """
    "return index template"
    return render_template('game.html')

    
@app.route('/')
def index():
    """
    Render the index HTML template.

    Returns:
        HTML: Rendered HTML for the index page.
    """
    "return index template"
    return render_template('index.html')


@app.route('/move')
def move():
    """
    Process a player's move, update the game state, and respond with the new state.

    Returns:
        JSON/str: Updated game state in JSON format or an error message string.
    """
    game_id = request.args['gameId']
    direction = request.args['direction']
    player = int(request.args['player'])
    
    game = dao.get_one_game_by_id(game_id)
    if game is None:
        abort(404, description="NO_GAME_FOUND")
    board = pickle.loads(game.board)
    board, active_player = management.move(board, game.active_player, Direction[direction], player)
    board, active_player = automatic_move(board, active_player, GameType[game.game_type])
    game = dao.update_one_game(game.id, board, active_player)
    return convert_to_json(game)

def automatic_move(board, active_player, game_type):
    if  active_player == -1 and game_type == GameType.HUMAN_VS_AI:
        possible_directions = management.get_possible_directions(board, active_player)
        if len(possible_directions) == 0 :
            return board, active_player
        random_index = random.randint(0, len(possible_directions) - 1)
        print(str(len(possible_directions)) + ' ' +  str(list(Direction)) + '  ' + str(random_index))
        direction = list(Direction)[random_index]
        return management.move(board, active_player, direction, active_player)
    return board, active_player

def convert_to_json(game: Game):
    board = pickle.loads(game.board)
    player1_points, player2_points = management.compute_points(board)
    return json.dumps({
        "id": game.id,
        "activePlayer": game.active_player,
        "gameType": game.game_type,
        "board":  pickle.loads(game.board),
        "player1Points":  player1_points,
        "player2Points": player2_points
    })
    