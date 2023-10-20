from flask import Flask, render_template, jsonify, g, request, session
from collections import deque
from markupsafe import escape
from .models import Game, Direction
from .management import GameManagement
from .management import app
import json
    
    
    
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
        return json.dumps(GameManagement().new_game(10).to_dict())
    return json.dumps(GameManagement().get_game(game_id).to_dict())

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
    return json.dumps(GameManagement().move(game_id, Direction.__members__.get(direction), player).to_dict())