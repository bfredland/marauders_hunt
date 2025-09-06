#!/usr/bin/env python3
"""
Database Cleanup Utility for Marauders Hunt App

This script allows you to clear test games and reset the database
without affecting the hunt items configuration.

Usage:
    python clear_games.py

Options:
    - Clear all games and completions
    - Reset just completions (keep games but clear progress)
    - Interactive mode with confirmation prompts
"""

import database
import sys

def clear_all_games():
    """Clear all games and completions from the database"""
    print("🗑️  Clearing all games and completions...")
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # Get counts before deletion
    cursor.execute('SELECT COUNT(*) FROM completions')
    completion_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM games')
    game_count = cursor.fetchone()[0]
    
    print(f"Found {game_count} games with {completion_count} total completions")
    
    if game_count == 0:
        print("✅ Database is already empty!")
        conn.close()
        return
    
    # Delete all completions first (foreign key constraint)
    cursor.execute('DELETE FROM completions')
    print(f"✅ Deleted {completion_count} completions")
    
    # Delete all games
    cursor.execute('DELETE FROM games')
    print(f"✅ Deleted {game_count} games")
    
    conn.commit()
    conn.close()
    print("🎉 Database cleared successfully!")

def clear_completions_only():
    """Clear all completions but keep games"""
    print("🗑️  Clearing all completions (keeping games)...")
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM completions')
    completion_count = cursor.fetchone()[0]
    
    if completion_count == 0:
        print("✅ No completions to clear!")
        conn.close()
        return
    
    cursor.execute('DELETE FROM completions')
    print(f"✅ Deleted {completion_count} completions")
    
    conn.commit()
    conn.close()
    print("🎉 All game progress reset!")

def show_stats():
    """Show current database statistics"""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM games')
    game_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM completions')
    completion_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM hunt_items')
    item_count = cursor.fetchone()[0]
    
    conn.close()
    
    print("📊 Current Database Stats:")
    print(f"   Games: {game_count}")
    print(f"   Hunt Items: {item_count}")
    print(f"   Completions: {completion_count}")

def interactive_mode():
    """Interactive mode with user prompts"""
    print("🍻 Marauders Hunt Database Cleanup Utility")
    print("=" * 45)
    
    show_stats()
    print()
    
    print("Choose an option:")
    print("1. Clear all games and progress")
    print("2. Reset game progress only (keep games)")
    print("3. Show stats only")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            confirm = input("⚠️  This will delete ALL games and progress. Continue? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                clear_all_games()
            else:
                print("❌ Operation cancelled")
            break
            
        elif choice == "2":
            confirm = input("⚠️  This will reset ALL game progress. Continue? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                clear_completions_only()
            else:
                print("❌ Operation cancelled")
            break
            
        elif choice == "3":
            show_stats()
            break
            
        elif choice == "4":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--all':
            clear_all_games()
        elif sys.argv[1] == '--completions':
            clear_completions_only()
        elif sys.argv[1] == '--stats':
            show_stats()
        else:
            print("Usage: python clear_games.py [--all|--completions|--stats]")
    else:
        interactive_mode()