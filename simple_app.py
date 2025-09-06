from flask import Flask, render_template, request, jsonify, redirect, url_for
import database
import os

# Ensure we're in the right directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current working directory: {current_dir}")
print(f"Files in directory: {os.listdir(current_dir)}")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

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
    return {'status': 'ok', 'message': 'Simple app is running'}, 200

@app.route('/test')
def test():
    return "Hello from Railway - Simple Version!", 200

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

@app.route('/game/<game_id>')
def game(game_id):
    # Get game info
    games = database.get_all_games()
    game_info = next((g for g in games if g[0] == game_id), None)
    
    if not game_info:
        return redirect(url_for('index'))
    
    return render_template('game.html', game_id=game_id, game_name=game_info[1])

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)

# For production deployments
application = app