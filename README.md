# henallux-python

## Presentation
Henallux AI is a game powered by AI

## Installation
To be documented

## Execution
In root directory, run python run.py

## Developpement:
Currently it's possible to start a new game and to move each smiley. Forbidden moves are already taken into account.
Moves can be performed through the UI or by pressing keyboard arrows.

For the moment no database is plugged to the application, state of the game is stored in session.

Error management: A userfriendly message is displayed to the user for any 400 HTTP error. The other errors such as 500, will redirect to a 500 error page.

Next steps:
  - database
  - redirection to 500 error page
  - Checking if game is over
