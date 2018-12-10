import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import urllib


def dict_to_json(dict):
    json_string = str(json.dumps(dict))
    return bytes(json_string, 'utf-8')


def format_bad_response(message):
        return dict_to_json({
            "status": "bad",
            "message": message
        })


class RequestHandler(BaseHTTPRequestHandler):
    games = {}

    def validate_turn(self, game_id, player, x, y):
        game = self.games[game_id]
        if game["winner"] != -1:
            raise Exception("Game is already over.")
        if player != 1 and player != 2:
            raise Exception("Invalid player.")
        elif x < 0 or x > 2 or y < 0 or y > 2:
            raise Exception("Invalid coordinates. Matrix size only 3x3. x:%s y:%s" % (x, y))
        elif game["next"] != player:
            raise Exception("It is not your turn. Next turn is on player: %s" % (game["next"]))
        elif game["board"][x][y] != 0:
            raise Exception("Position already taken on x:%s y:%s" % (x, y))



    def send_200_resp(self, json_string):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json_string)

    def send_400_resp(self, json_string):
        self.send_response(400)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json_string)


    def new_game(self, name):
            newId = len(self.games) + 1
            self.games[newId] = {}
            self.games[newId]['name'] = name
            self.games[newId]['next'] = 1
            self.games[newId]['winner'] = -1
            self.games[newId]['board'] = [
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0]
            ]
            return newId

    def start_game(self, params, request_path):
        try:
            name = params["name"][0]
            game_id = self.new_game(name)

            response_data = {}
            response_data["id"] = game_id
            self.send_200_resp(dict_to_json(response_data))

        except Exception as e:
            response_data = {}
            response_data["bad"] = "Invalid params. Exc:" + str(e)
            self.send_200_resp(dict_to_json(response_data))

    def status_game(self, params, request_path):
        try:
            game_id = int(params["game"][0])
            game = self.games[game_id]

            response_data = {}
            if game["winner"] != -1:
                response_data["winner"] = game["winner"]
            else:
                response_data["board"] = game["board"]
                response_data["next"] = game["next"]
            self.send_200_resp(dict_to_json(response_data))

        except Exception as e:
            response_data = {}
            response_data["bad"] = "Invalid params. Exc:" + str(e)
            self.send_200_resp(dict_to_json(response_data))


    def get_winner(self, game_id):
        board = self.games[game_id]["board"]

        zeros = 0
        for i in range(3):
            for j in range(3):
                if board[i][j] == 0:
                    zeros += 1
        # no space left - this is tie
        if zeros == 0:
            return 0

        players = [1, 2]

        for p in players:
            for i in range(3):
                if board[i][0] == p and board[i][1] == p and board[i][2] == p:
                    return p
                if board[0][i] == p and board[1][i] == p and board[2][i] == p:
                    return p

            if board[0][0] == p and board[1][1] == p and board[2][2] == p:
                return p
            if board[2][0] == p and board[1][1] == p and board[0][2] == p:
                return p
        return -1


    def play_game(self, params, request_path):
        response_data = {}
        try:
            try:
                game_id = int(params["game"][0])
                player = int(params["player"][0])
                x = int(params["x"][0])
                y = int(params["y"][0])
            except ValueError as ve:
                raise Exception("Invalid parameter format.")

            game = self.games[game_id]
            self.validate_turn(game_id, player, x, y)

            if game["winner"] == -1:
                # no winner, make turn
                game["board"][x][y] = player
                if player == 1:
                    game["next"] = 2
                else:
                    game["next"] = 1
            else:
                # we already got winner
                response_data["status"] = "bad"
                response_data["message"] = "Game is already over."
                self.send_200_resp(dict_to_json(response_data))


            response_data["status"] = "ok"

            # winner after update
            winner = self.get_winner(game_id)
            if winner != -1:
                game["winner"] = winner
                if player == winner:
                    response_data["message"] = "Congrats! You won!"
                elif winner == 0:
                    response_data["message"] = "Tie."

            self.send_200_resp(dict_to_json(response_data))

        except Exception as e:
            print(str(e))
            response_data["status"] = "bad"
            if isinstance(e, KeyError):
                response_data["message"] = "Missing parameter " + str(e)
            else:
                response_data["message"] = str(e)
            self.send_200_resp(dict_to_json(response_data))


    def check_id_exists(self, params):
        # check game_id exists
        try:
            game_id = int(params["game"][0])
            self.games[game_id]
        except:
            self.send_error(404)

    def do_GET(self):

        params = str(self.path).split("?", 1)[-1]

        if params:
            params = urllib.parse.parse_qs(params)
        request_path = urllib.parse.urlparse(self.path).path

        if "/start" in request_path:
            self.start_game(params, request_path)
        elif "/status" in request_path:
            self.check_id_exists(params)
            self.status_game(params, request_path)
        elif "/play" in request_path:
            self.check_id_exists(params)
            self.play_game(params, request_path)




port = int(sys.argv[1])
server = HTTPServer(('', port), RequestHandler)
server.serve_forever()
print('Listening on localhost:%s' % port)

