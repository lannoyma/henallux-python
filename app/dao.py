from . import models
import pickle

class Dao:
    def get_one_game_by_id(self, id):
        print('id ' + str(id))
        return models.db.session.query(models.Game).get(id)

    def create_one_game(self, board, game_type: models.GameType):
        game = models.Game(
            active_player=1,
            game_type=game_type.name,
            board=pickle.dumps(board))
        models.db.session.add(game)
        models.db.session.commit()
        models.db.session.flush()
        return game
        
    def update_one_game(self, id, board, active_player):
        game  = self.get_one_game_by_id(id)
        game.board = pickle.dumps(board)
        game.active_player = active_player
        models.db.session.commit()
        models.db.session.flush()
        return game
         