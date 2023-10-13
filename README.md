# henallux-python

## Presentation
Henallux AI is a game powered by AI

## Installation
- Install Python >= 3.11
- Install Flask >= 2.3.3

## Execution
In root directory, run in command line
- .venv\Scripts\activate (To activate the server environment)
- python run.py (Lauch the application)

## Developpement:
Currently it's possible to start a new game and to move each smiley. Forbidden moves are already taken into account.
Moves can be performed through the UI or by pressing keyboard arrows.

For the moment no database is plugged to the application, state of the game is stored in session.

Error management: A userfriendly message is displayed to the user for any 400 HTTP error. The other errors such as 500, will redirect to a 500 error page.

Game over: Game ends when all points have been won by players

Enclos detection: Working

Next steps:
  - database
  - redirection to 500 error page
