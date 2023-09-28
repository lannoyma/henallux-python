from flask import Flask, render_template, jsonify, g, request, session
from markupsafe import escape

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
    
    
# Waiting database to be ready to remove session variable use
@app.route('/loadGame')
def loadGame():
    "return index template"
    session['game'] = {
        "state": [
        [2, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, -2],
        ],
        "activePlayer": 1
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
    state = game["state"]
    active_player = game["activePlayer"]
    if player != active_player:
        return "MOVE_USER_NOT_ACTIVE", 400
    current_pos = None
    for i, line in enumerate(state):
        for j, cell in enumerate(line):
            if cell == 2 * player: # Will find -2 or 2 depending on player's value
                current_pos = {
                    "row": i,
                    "col":j 
                }
                row = i
                col = j
                
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
    if next_pos["row"] < 0 or next_pos["row"] >= len(state) or next_pos["col"] < 0 or next_pos["col"] >= len(state[0]):
        return "MOVE_OUT_OF_GRID", 400
    # Check if new position does not belong to other player
    if state[next_pos["row"]][next_pos["col"]] == -1 * player:
        return "MOVE_CELL_BELONGS_TO_OPPONENT", 400
    # Check opponent is not on new position
    if state[next_pos["row"]][next_pos["col"]] == -2 * player:
        return "MOVE_CELL_BELONGS_TO_OPPONENT", 400
    
    # Set old position belong to current player
    state[current_pos["row"]][current_pos["col"]] = player
    
    # Set new position
    state[next_pos["row"]][next_pos["col"]] = 2 * player
    
    # Change user
    session["game"] = {
         "state": state,
        "activePlayer": - active_player
    }
    return jsonify(session['game'])