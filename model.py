import datetime
from typing import Any
from pydantic import BaseModel
from uuid import uuid4


class RouletteUser(BaseModel):
    user_id: str
    display_name: str
    gid: str
    balance: int = 0
    wins: int = 0
    losses: int = 0
    max_win: int = 0
    last_beg: int = 0
    curr_bet: dict = {}


# class RouletteUser(BaseModel):
#     user_id: str
#     display_name: str
#     gid: str
#     balance: int = 0
#     wins: int = 0
#     losses: int = 0
#     max_win: int = 0
#     last_beg: int = 0
#     curr_bet: dict = {}

class RouletteGuild(BaseModel):
    guild_id: str
    guild_name: str
    users: list[RouletteUser] = []

    def leaderboard(self, category: str) -> list[RouletteUser] | str:
        try:
            sorted_users = sorted(self.users, key=lambda x: getattr(x, category), reverse=True)
            return sorted_users
        except AttributeError:
            return "No Such Category"


class RouletteBet(BaseModel):
    straight: dict[str, int] = {}
    colour: dict[str, int] = {}
    high_low: dict[str, int] = {}
    even_odd: dict[str, int] = {}
    dozen: dict[str, int] = {}
    column: dict[str, int] = {}

    def __init__(self, player_bets_dict: dict[str, int] = None, **data: Any):
        super().__init__(**data)
        if player_bets_dict is not None:
            for key, value in player_bets_dict.items():
                if key.isdigit():
                    # print(f'{key},isdigit-{key.isdigit()}')
                    if key == "00":
                        self.straight[key] = value
                        # self.straight.append(Bet(option='00', amount=value))
                    if 0 <= int(key) <= 36:
                        self.straight[key] = value
                        # self.straight.append(Bet(option=key, amount=value))
                elif key.isalnum():
                    # print(f'{key},isalnum{key.isalnum()}')
                    if key == "red" or key == "black":
                        self.colour[key] = value
                        # self.colour.append(Bet(option=key, amount=value))
                    elif key == "high" or key == "low":
                        self.high_low[key] = value
                        # self.high_low.append(Bet(option=key, amount=value))
                    elif key == "even" or key == "odd":
                        self.even_odd[key] = value
                        # self.even_odd.append(Bet(option=key, amount=value))
                    elif key[0] == "d":
                        self.column[key[1]] = value
                        # self.dozen.append(Bet(option=key, amount=value))
                    elif key[0] == "c":
                        self.dozen[key[1]] = value
                        # self.column.append(Bet(option=key, amount=value))

    def sum(self):
        print("in sum")
        total = 0
        total += sum(self.straight.values())
        total += sum(self.colour.values())
        total += sum(self.high_low.values())
        total += sum(self.even_odd.values())
        total += sum(self.column.values())
        total += sum(self.dozen.values())
        print("exit sum")
        return total

    def test(self):
        print(dir(self))


class BetInstance(BaseModel):
    timestamp: datetime.datetime = datetime.datetime.now(datetime.UTC)
    winning_number: int
    bettors_bets: dict[str, RouletteBet]
