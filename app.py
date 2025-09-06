from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import database
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database and load hunt items
database.init_db()

# Load hunt items from CSV if it exists
if os.path.exists('hunt_items.csv'):
    database.load_hunt_items_from_csv('hunt_items.csv')

@app.route('/')
def index():
    games = database.get_all_games()
    return render_template('index.html', games=games)

@app.route('/game/<game_id>')
def game(game_id):
    # Get game info
    games = database.get_all_games()
    game_info = next((g for g in games if g[0] == game_id), None)
    
    if not game_info:
        return redirect(url_for('index'))
    
    return render_template('game.html', game_id=game_id, game_name=game_info[1])

@app.route('/create_game', methods=['POST'])
def create_game():
    data = request.get_json()
    game_id = data.get('game_id')
    game_name = data.get('game_name')
    
    try:
        database.create_game(game_id, game_name)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/game_data/<game_id>')
def game_data(game_id):
    try:
        items = database.get_game_progress(game_id)
        total_points = database.get_game_total_points(game_id)
        return jsonify({'items': items, 'total_points': total_points})
    except Exception as e:
        return jsonify({'error': str(e)})

@socketio.on('join_game')
def on_join(data):
    game_id = data['game_id']
    join_room(game_id)
    print(f"User joined game room: {game_id}")

@socketio.on('leave_game')
def on_leave(data):
    game_id = data['game_id']
    leave_room(game_id)
    print(f"User left game room: {game_id}")

@socketio.on('toggle_item')
def handle_toggle_item(data):
    game_id = data['game_id']
    item_id = data['item_id']
    
    try:
        completed = database.toggle_item(game_id, item_id)
        total_points = database.get_game_total_points(game_id)
        
        # Broadcast to all users in this game room
        socketio.emit('item_toggled', {
            'game_id': game_id,
            'item_id': item_id,
            'completed': completed,
            'total_points': total_points
        }, room=game_id)
        
    except Exception as e:
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    # For development
    socketio.run(app, debug=True, host='127.0.0.1', port=5001, allow_unsafe_werkzeug=True)
else:
    # For production (PythonAnywhere)
    application = app