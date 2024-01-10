import random
from typing import Any, Tuple
from model import RouletteBet
import yaml

with open("config.yaml", 'r') as file:
    config = yaml.safe_load(file)
roulette_values = config["roulette"]

# valid_bet_choices = ["00", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16",
#                      "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32",
#                      "33", "34", "35", "36", "red", "black", "even", "odd", "c1", "c2", "c3", "d1", "d2", "d3", "high",
#                      "low"]
#
# black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
# red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
# column1_numbers = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
# column2_numbers = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
# column3_numbers = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
# payout_values = {"straight": 32, "colour": 2, "high_low": 2, "even_odd": 2, "dozen": 3, "column": 3}

valid_bet_choices = roulette_values["valid_bet_choices"]
black_numbers = roulette_values["black_numbers"]
red_numbers = roulette_values["red_numbers"]
column1_numbers = roulette_values["column1_numbers"]
column2_numbers = roulette_values["column2_numbers"]
column3_numbers = roulette_values["column3_numbers"]
payout_values = roulette_values["payout_values"]


def is_valid_bet(bet: str) -> bool:
    return bet in valid_bet_choices


def winning_bets(winning_number: int) -> dict:
    # bets = {str(winning_number): winning_number}
    bets = {}
    if winning_number == 0:
        bets["straight"] = "0"
        bets['colour'] = "n/a"
        bets["high_low"] = "n/a"
        bets["even_odd"] = "n/a"
        bets["dozen"] = "n/a"
        bets["column"] = "n/a"
        return bets
    if winning_number == -1:
        bets["straight"] = "00"
        bets['colour'] = "n/a"
        bets["high_low"] = "n/a"
        bets["even_odd"] = "n/a"
        bets["dozen"] = "n/a"
        bets["column"] = "n/a"
        return bets
    bets["straight"] = (str(winning_number))
    if winning_number in black_numbers:
        bets["colour"] = "black"
    if winning_number in red_numbers:
        bets["colour"] = "red"
    if 1 <= winning_number <= 18:
        bets["high_low"] = "low"
    if 19 <= winning_number <= 36:
        bets["high_low"] = "high"
    if winning_number % 2 == 0:
        bets["even_odd"] = "even"
    if winning_number % 2 != 0:
        bets["even_odd"] = "odd"
    if 1 <= winning_number <= 12:
        bets["dozen"] = "1"
    if 13 <= winning_number <= 24:
        bets["dozen"] = "2"
    if 25 <= winning_number <= 36:
        bets["dozen"] = "3"
    if winning_number in column1_numbers:
        bets["column"] = "1"
    if winning_number in column2_numbers:
        bets["column"] = "2"
    if winning_number in column3_numbers:
        bets["column"] = "3"
    return bets


def payout(player_bets: RouletteBet, win_bet: dict, returns: dict[str:int]) -> Tuple[RouletteBet, int, int]:
    bet_payout = RouletteBet()
    print("in payout")
    print(f'playerbet - {player_bets}')
    print(f'winbet - {win_bet}')
    if win_bet["straight"] in player_bets.straight.keys():
        bet_payout.straight[win_bet["straight"]] = (player_bets.straight[win_bet["straight"]]) * int(
            returns["straight"])
        # total_winnings += bet_payout.straight[win_bet["straight"]]

    if win_bet["colour"] in player_bets.colour.keys():
        bet_payout.colour[win_bet["colour"]] = player_bets.colour[win_bet["colour"]] * int(returns["colour"])
        # total_winnings += bet_payout.colour[win_bet["colour"]]

    if win_bet["high_low"] in player_bets.high_low.keys():
        bet_payout.high_low[win_bet["high_low"]] = player_bets.high_low[win_bet["high_low"]] * int(returns["high_low"])
        # total_winnings += bet_payout.high_low[win_bet["high_low"]]

    if win_bet["even_odd"] in player_bets.even_odd.keys():
        bet_payout.even_odd[win_bet["even_odd"]] = player_bets.even_odd[win_bet["even_odd"]] * int(returns["even_odd"])
        # total_winnings += bet_payout.even_odd[win_bet["even_odd"]]

    if win_bet["dozen"] in player_bets.dozen.keys():
        bet_payout.dozen[win_bet["dozen"]] = player_bets.dozen[win_bet["dozen"]] * int(returns["dozen"])
        # total_winnings += bet_payout.dozen[win_bet["dozen"]]

    if win_bet["column"] in player_bets.column.keys():
        bet_payout.column[win_bet["column"]] = player_bets.column[win_bet["column"]] * int(returns["column"])
        # total_winnings += bet_payout.column[win_bet["column"]]
    print("pre sum")
    print(f"player_bets - {player_bets}")
    print(f"bet_payout - {bet_payout}")

    player_wager = player_bets.sum()
    win_loss = bet_payout.sum() - player_wager
    print("end of payout")
    return bet_payout, win_loss, player_wager


def roulette(p_bet) -> [int, int, int]:
    # winning_number = random.randint(-1, 36)
    winning_number = 3
    print(winning_number)
    winner = winning_bets(winning_number)
    print(winner)
    player_bet_obj = RouletteBet(p_bet)
    print(player_bet_obj)
    # print("_________________________")
    result, winnings, wagered = payout(player_bet_obj, winner, payout_values)
    print(result)
    print(winnings)
    if winning_number == -1:
        winning_number = "00"
    return winning_number, winnings, wagered

# bet = {"red": 5}
#
# roulette(bet)
# running_total = 0
# wins = 0
# losses = 0
#
# for i in range(10):
#     print(f'***{i}***')
#     r = roulette(bet)
#     if r >= 0:
#         wins += 1
#     else:
#         losses += 1
#     # print(r)
#     running_total += r
#     print(running_total)
#     print(f'wins{wins} / losses{losses}')
