from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, LargeBinary
import logging as lg
from datetime import datetime
from enum import Enum
from typing import List

db = SQLAlchemy()
def init_db():
    db.drop_all()
    db.create_all()
    ...
    db.session.commit()
    lg.warning('Database initialized!')

class Game(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    started_at = db.Column(DateTime, nullable=False, default=datetime.utcnow)  # Renommée et configurée avec une valeur par défaut
    active_player = db.Column(db.SmallInteger, nullable=False)
    game_type = db.Column(db.String(20), nullable=False, default='HUMAN_VS_HUMAN')  # Mis à jour avec la valeur par défaut correcte
    board = db.Column(LargeBinary)

    __table_args__ = (
        db.CheckConstraint(game_type.in_(['HUMAN_VS_HUMAN', 'HUMAN_VS_AI', 'AI_VS_AI']), name='check_game_type'),
    )
    def __repr__(self):
        return f'<Game {self.id}>'

class Direction(Enum):
    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'

class GameType(Enum):
    HUMAN_VS_HUMAN = 'HUMAN_VS_HUMAN'
    HUMAN_VS_AI = 'HUMAN_VS_AI'
    AI_VS_AI = 'AI_VS_AI'
        
        
#lass Game:
#   def __init__(self, id: int, started_at: datetime, active_player: int, game_type: GameType, board: List[List[int]], player_1_points: int, player_2_points: int):
#       self.id: int = id
#       self.started_at: datetime = started_at
#       self.active_player: int = active_player
#       self.game_type: GameType = game_type
#       self.board: List[List[int]] = board
#       self.player_1_points: int = player_1_points
#       self.player_2_points: int = player_2_points
#       
#   def to_dict(self):
#       return {
#           "id": self.id,
#           "activePlayer": self.active_player,
#           "gameType": self.game_type.name,
#           "board": self.board,
#           "player1Points": self.player_1_points,
#           "player2Points": self.player_2_points
#       }
        
