from . import models
import pickle

class Dao:
    def get_one_game_by_id(self, id: int):
        """
        Retrieve a single game by its unique identifier.

        Parameters:
            - id (int): The unique identifier of the game.

        Returns:
            models.Game: The Game object corresponding to the specified ID.

        This method retrieves a single game from the database based on its unique
        identifier (ID). It returns the Game object associated with the given ID.

        Example:
            game = self.get_one_game_by_id(game_id)
        """
        return models.db.session.query(models.Game).get(id)

    def create_one_game(self, board, game_type: models.GameType):
        """
        Create a new game and store it in the database.

        Parameters:
            - board (List[List[int]]): The initial state of the game board.
            - game_type (models.GameType): The type of the game.

        Returns:
            models.Game: The newly created Game object.

        This method creates a new game with the specified initial board state and game type.
        It stores the game in the database and returns the newly created Game object.

        Example:
            new_game = self.create_one_game(initial_board, models.GameType.HUMAN_VS_AI)
        """
        game = models.Game(
            active_player=1,
            game_type=game_type.name,
            board=pickle.dumps(board))
        models.db.session.add(game)
        models.db.session.commit()
        models.db.session.flush()
        return game
        
    def update_one_game(self, id: int, board, active_player: int):
        """
            Update an existing game's board and active player and store the changes in the database.

            Parameters:
                - id (int) : The unique identifier of the game to be updated.
                - board (List[List[int]]): The updated state of the game board.
                - active_player (int): The updated active player.

            Returns:
                models.Game: The updated Game object.

            This method updates the board and active player of an existing game based on the
            specified ID. It stores the changes in the database and returns the updated Game
            object.

            Example:
                updated_game = self.update_one_game(game_id, updated_board, new_active_player)
            """
        game  = self.get_one_game_by_id(id)
        game.board = pickle.dumps(board)
        game.active_player = active_player
        models.db.session.commit()
        models.db.session.flush()
        return game
         