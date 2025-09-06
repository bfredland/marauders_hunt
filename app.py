from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import database
import os

# Ensure we're in the right directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current working directory: {current_dir}")
print(f"Files in directory: {os.listdir(current_dir)}")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database and load hunt items
try:
    print("Initializing database...")
    database.init_db()
    print("Database initialized successfully")
    
    # Load hunt items from CSV if it exists
    if os.path.exists('hunt_items.csv'):
        print("Loading hunt items from CSV...")
        database.load_hunt_items_from_csv('hunt_items.csv')
        print("Hunt items loaded successfully")
    else:
        print("hunt_items.csv not found, using empty hunt items")
except Exception as e:
    print(f"Error during initialization: {e}")
    import traceback
    traceback.print_exc()

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'App is running'}, 200

@app.route('/test')
def test():
    return "Hello from Railway!", 200

@app.route('/')
def index():
    try:
        print("Index route called")
        games = database.get_all_games()
        print(f"Found {len(games)} games")
        return render_template('index.html', games=games)
    except Exception as e:
        print(f"Error in index route: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {e}", 500

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

@app.route('/toggle_item', methods=['POST'])
def toggle_item():
    data = request.get_json()
    game_id = data.get('game_id')
    item_id = data.get('item_id')
    
    try:
        completed = database.toggle_item(game_id, item_id)
        total_points = database.get_game_total_points(game_id)
        
        return jsonify({
            'success': True,
            'completed': completed,
            'total_points': total_points
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

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
    # Local development only
    print("Running in development mode")
    socketio.run(app, debug=True, host='127.0.0.1', port=5001, allow_unsafe_werkzeug=True)

# For production deployments
application = app