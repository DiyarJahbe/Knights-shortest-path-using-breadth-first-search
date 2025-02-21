from flask import Flask, request, jsonify, render_template
from collections import deque
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

KNIGHT_MOVES = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
DIRECTIONS = {
    (2, 1): "2 right, 1 up", (2, -1): "2 right, 1 down",
    (-2, 1): "2 left, 1 up", (-2, -1): "2 left, 1 down",
    (1, 2): "1 right, 2 up", (1, -2): "1 right, 2 down",
    (-1, 2): "1 left, 2 up", (-1, -2): "1 left, 2 down"
}

def is_valid(x, y, N):
    return 0 <= x < N and 0 <= y < N

def bfs(N, start, end):
    queue, visited = deque([(start, 0, [start])]), {start}
    while queue:
        (x, y), moves, path = queue.popleft()
        if (x, y) == end: return moves, path
        for dx, dy in KNIGHT_MOVES:
            new_pos = (x + dx, y + dy)
            if is_valid(*new_pos, N) and new_pos not in visited:
                visited.add(new_pos)
                queue.append((new_pos, moves + 1, path + [new_pos]))
    return -1, []

def find_knight_path(N, nodes):
    total_moves, full_path = 0, []
    for i in range(len(nodes) - 1):
        moves, path = bfs(N, (nodes[i]['x'], nodes[i]['y']), (nodes[i+1]['x'], nodes[i+1]['y']))
        if moves == -1: return -1, []
        total_moves += moves
        full_path.extend(path[1:] if full_path else path)

    move_sequence = [
        {'from': {'x': p1[0], 'y': p1[1]}, 'to': {'x': p2[0], 'y': p2[1]}, 'direction': DIRECTIONS.get((p2[0]-p1[0], p2[1]-p1[1]), "")}
        for p1, p2 in zip(full_path, full_path[1:])
    ]

    node_positions = {(n['x'], n['y']): i+1 for i, n in enumerate(nodes)}
    for move in move_sequence:
        move['nodeNumber'] = node_positions.get((move['from']['x'], move['from']['y'])) or node_positions.get((move['to']['x'], move['to']['y']))
    
    return total_moves, move_sequence

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST', 'OPTIONS'])
def calculate():
    if request.method == 'OPTIONS': return '', 204
    try:
        data = request.json
        N, nodes = int(data.get('N', 0)), data.get('nodes', [])
        if N <= 0 or len(nodes) < 2 or any(not is_valid(n['x'], n['y'], N) for n in nodes):
            return jsonify({'result': 'Invalid input'}), 400

        moves, path = find_knight_path(N, nodes)
        return jsonify({'success': moves != -1, 'result': f"{moves} moves needed." if moves != -1 else "No path found.", 'path': path, 'boardSize': N, 'nodes': nodes})
    
    except Exception as e:
        return jsonify({'success': False, 'result': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
