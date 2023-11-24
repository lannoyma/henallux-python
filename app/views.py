from flask import Flask, render_template, jsonify, g, request, abort
from .models import Game, Direction, GameType
from .dao import Dao
from .management import GameManagement
import json
import pickle
import logging as lg
    
app = Flask(__name__)
app.config.from_object('config')
dao = Dao()
management = GameManagement()

@app.route('/loadGame')
def loadGame():
    """
    Load or create a game based on the provided 'gameId' query parameter.

    Returns:
        str: JSON-formatted string representing the game state.

    This function checks if a 'gameId' query parameter is provided in the request.
    If 'gameId' is None, it creates a new game of type 'GameType.HUMAN_VS_AI' with a
    5x5 board and returns its JSON representation. If 'gameId' is provided, it attempts
    to load the corresponding game from the database and, if found, performs an automatic
    move based on the game's state and returns the updated JSON representation of the game.

    Raises:
        HTTPException(404): If no game is found with the provided 'gameId'.
    """
    game_id = request.args.get('gameId')
    if game_id is None:
        game_type = GameType.HUMAN_VS_AI
        board  = management.new_game(5, game_type)
        game = dao.create_one_game(board, game_type)
    else:
        print ('Game_id' + str(game_id))
        game = dao.get_one_game_by_id(game_id)
        if game is None:
            abort(404, description="NO_GAME_FOUND")
        board = pickle.loads(game.board)
        board, active_player = management.automatic_move(board, game.active_player, GameType[game.game_type])
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
    "return game template"
    return render_template('game.html')

@app.route('/error')
def error():
    """
    Render the error HTML template.

    Returns:
        HTML: Rendered HTML for the error.
    """
    "return error template"
    return render_template('error.html')
    
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
        JSON/str: Updated game state in JSON format or a 400 error if the move is not allowed
    """
    game_id = request.args['gameId']
    direction = request.args['direction']
    player = int(request.args['player'])
    
    game = dao.get_one_game_by_id(game_id)
    if game is None:
        abort(404, description="NO_GAME_FOUND")
    board = pickle.loads(game.board)
    board, active_player = management.move(board, game.active_player, Direction[direction], player)
    board, active_player = management.automatic_move(board, active_player, GameType[game.game_type])
    game = dao.update_one_game(game.id, board, active_player)
    return convert_to_json(game)

def convert_to_json(game: Game):
    """
    Convert a Game object to a JSON-formatted string.

    Parameters:
        - game (Game): The Game object to convert to JSON.

    Returns:
        str: A JSON-formatted string representing the Game object.

    This function takes a Game object and converts it into a JSON-formatted string
    that includes various properties of the game, such as its ID, active player,
    game type, board state, and player points.

    Example:
        game_json = convert_to_json(game_instance)
    """
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
    