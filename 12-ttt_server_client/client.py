import json
import sys
import asyncio
import aiohttp
import os


async def fetch(session, url):
    async with session.get(url) as response:
        assert response.status == 200
        return json.loads(await response.text())


def has_empty_board(board):
    zeros = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                zeros += 1

    return zeros == 9


async def game_lobby(session, games):
    listed_games = []
    if games and len(games):
        for game in games:
            game_status = await fetch(session, GAME_SERVER_ADDRESS + "/status?game=" + str(game["id"]))
            if "board" not in game_status:
                continue
            board = game_status["board"]
            if has_empty_board(board):
                if game["name"]:
                    listed_games.append(str(game["id"]) + " " + game["name"])
                else:
                    listed_games.append(str(game["id"]))

    if len(listed_games) > 0:
        print("Available games:")
        for available_game in listed_games:
            print(available_game)
        print("Enter game id or \'new <game_name>\' for new game.")
        lobby_input = input()
        return lobby_input
    else:
        print("No available games. Type \'new\' <game_name> for new game.")
        lobby_input = input()
        return lobby_input


async def start_new_game(session, name):
    response = await fetch(session, GAME_SERVER_ADDRESS + "/start?name=" + name)
    game_id = response["id"]
    print("New game with id: " + str(game_id) + " started.")
    return game_id


async def status(session, game_id, player):
    game_status = await fetch(session, GAME_SERVER_ADDRESS + "/status?game=" + str(game_id))
    return game_status


async def play(session, game_id, player, x, y):
    response = await fetch(session, GAME_SERVER_ADDRESS + '/play?' + 'game=' + str(game_id) +
                                '&player=' + str(player) + '&x=' + str(x) + '&y=' + str(y))
    return response


async def main():
    host = sys.argv[1]
    port = int(sys.argv[2])
    clear = lambda: os.system('clear')
    global GAME_SERVER_ADDRESS
    GAME_SERVER_ADDRESS = 'http://' + host + ":" + str(port)
    async with aiohttp.ClientSession() as session:
        # game lobby for game creation/selection
        while True:
            games = await fetch(session, GAME_SERVER_ADDRESS + "/list")

            lobby_input = await game_lobby(session, games)

            if lobby_input.startswith("new"):
                s = lobby_input.split (" ")
                if len(s) == 2:
                    name = s[1]
                else:
                    name = ""
                game_id = await start_new_game(session, name)
                player = 1
                break
            elif lobby_input.isdigit():
                game_id = lobby_input
                player = 2
                break
            else:
                print("Invalid command. Try again")

        # game play
        printed = 0
        while True:
            dic = {0: "_", 1: "o", 2: 'x'}
            game_status = await status(session, game_id, player)
            if game_status.get("next") and player != game_status["next"] and not printed:
                print("waiting for the other player")
                printed = 1

            if "winner" in game_status:
                if game_status["winner"] == player:
                    print("you win")
                else:
                    print("you lose")
                break
            else:
                for row in game_status["board"]:
                    for element in row:
                        print(dic.get(element), end="")
                    print()
                print()

            if player == game_status["next"]:
                while True:
                    print("your turn(%s):" % dic.get(player))
                    game_input = input()
                    game_input = game_input.split(" ")
                    if len(game_input) != 2 or not game_input[0].isdigit() or not game_input[1].isdigit():
                        print("invalid input")
                    else:
                        play_response = await play(session, game_id, player, game_input[0], game_input[1])
                        if play_response['status'] == 'bad':
                            print("invalid input")
                        else:
                            printed = 0
                            break
            await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())