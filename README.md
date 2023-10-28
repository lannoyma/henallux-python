# henallux-python

## Presentation
Henallux AI is a game powered by AI

## Dependencies
See requirements.txt

## Installation
Run pip install -r requirements.txt

## Execution
For development purpose only. This section can be ignored
In root directory, run in command line
- .venv\Scripts\activate (To activate the server environment)
- python run.py (Lauch the application)

## Developpement:
Moves can be performed through the UI or by pressing keyboard arrows.
Already done:

- Error management: A userfriendly message is displayed to the user for any 400 HTTP error.
- Other errors redirect to a 500 error page.
- Forbidden moves taken into account
- Game over: Game ends when all points have been won by players
- Enclos detection: Working
- Database: Fully working
- Human vs Human working
- Human vs naive AI working
- Game session: You can continue a game by using its id in the browser URL : /game?gameId=11

Next steps:
  - AI

## Database schema
Game
- id: BIGINT
- started_at: DATETIME
- active_player: {0, -1, 1} // 0 = Game ended
- board: LONGTEXT // 2D array representing each cell state
- type: {HUMAN_VS_HUMAN, HUMAN_VS_AI, AI_VS_AI}
