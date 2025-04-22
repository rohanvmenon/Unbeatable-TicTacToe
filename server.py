from flask import Flask, request, jsonify, send_from_directory
from tictactoe import Board
from mcts import MCTS

app = Flask(__name__)

# Initialize the board and MCTS
board = Board()
mcts = MCTS()

@app.route('/')
def index():
    # Serve the index.html file
    return send_from_directory('.', 'index.html')

@app.route('/reset', methods=['POST'])
def reset_game():
    global board
    board = Board()  # Reset the board
    return jsonify({"message": "Game reset", "board": board_to_json(board)})

@app.route('/player-move', methods=['POST'])
def player_move():
    global board
    data = request.json
    move = data.get('move')  # Move is a number between 0-8
    row, col = divmod(move, 3)

    # Check if the move is valid
    if board.position[row, col] != board.empty_square:
        return jsonify({"error": "Invalid move"}), 400

    # Make the player's move
    board = board.make_move(row, col)

    # Check if the player has won or if the game is a draw
    if board.is_win():
        return jsonify({"status": "win", "winner": "player", "board": board_to_json(board)})
    elif board.is_draw():
        return jsonify({"status": "draw", "board": board_to_json(board)})

    # Let the AI make its move
    best_move = mcts.search(board)
    board = best_move.board

    # Check if the AI has won or if the game is a draw
    if board.is_win():
        return jsonify({"status": "win", "winner": "ai", "board": board_to_json(board)})
    elif board.is_draw():
        return jsonify({"status": "draw", "board": board_to_json(board)})

    # Continue the game
    return jsonify({"status": "continue", "board": board_to_json(board)})

def board_to_json(board):
    """Convert the board state to a JSON-friendly format."""
    return {
        "position": [
            [board.position[row, col] for col in range(3)]
            for row in range(3)
        ],
        "player_1": board.player_1,
        "player_2": board.player_2,
    }

if __name__ == '__main__':
    app.run(debug=True)