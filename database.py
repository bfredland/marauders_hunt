import sqlite3
import csv
import os
from datetime import datetime

def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'marauders_hunt.db')
    return sqlite3.connect(db_path)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hunt_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            points INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_points INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT,
            item_id INTEGER,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (item_id) REFERENCES hunt_items(id),
            UNIQUE(game_id, item_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def load_hunt_items_from_csv(csv_file):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear existing items
    cursor.execute('DELETE FROM hunt_items')
    
    # Load from CSV
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            item_name = row['item']  # assuming column name is 'item'
            points = int(row['points'])  # assuming column name is 'points'
            cursor.execute('INSERT INTO hunt_items (item_name, points) VALUES (?, ?)', 
                         (item_name, points))
    
    conn.commit()
    conn.close()

def get_hunt_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM hunt_items ORDER BY points DESC')
    items = cursor.fetchall()
    conn.close()
    return items

def create_game(game_id, game_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO games (id, name) VALUES (?, ?)', (game_id, game_name))
    conn.commit()
    conn.close()

def get_all_games():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT g.id, g.name, g.created_at, 
               COALESCE(SUM(hi.points), 0) as total_points
        FROM games g
        LEFT JOIN completions c ON g.id = c.game_id
        LEFT JOIN hunt_items hi ON c.item_id = hi.id
        GROUP BY g.id, g.name, g.created_at
        ORDER BY g.created_at DESC
    ''')
    games = cursor.fetchall()
    conn.close()
    return games

def get_game_progress(game_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT hi.id, hi.item_name, hi.points, 
               CASE WHEN c.item_id IS NOT NULL THEN 1 ELSE 0 END as completed
        FROM hunt_items hi
        LEFT JOIN completions c ON hi.id = c.item_id AND c.game_id = ?
        ORDER BY hi.points DESC
    ''', (game_id,))
    progress = cursor.fetchall()
    conn.close()
    return progress

def toggle_item(game_id, item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if already completed
    cursor.execute('SELECT * FROM completions WHERE game_id = ? AND item_id = ?', 
                  (game_id, item_id))
    existing = cursor.fetchone()
    
    if existing:
        # Remove completion
        cursor.execute('DELETE FROM completions WHERE game_id = ? AND item_id = ?', 
                      (game_id, item_id))
        completed = False
    else:
        # Add completion
        cursor.execute('INSERT INTO completions (game_id, item_id) VALUES (?, ?)', 
                      (game_id, item_id))
        completed = True
    
    conn.commit()
    conn.close()
    return completed

def get_game_total_points(game_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COALESCE(SUM(hi.points), 0) as total_points
        FROM completions c
        JOIN hunt_items hi ON c.item_id = hi.id
        WHERE c.game_id = ?
    ''', (game_id,))
    total = cursor.fetchone()[0]
    conn.close()
    return total