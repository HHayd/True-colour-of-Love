#!/usr/bin/env python3
"""
cli.py — Terminal CLI for Red Cabbage 2PC Confession Game

This module provides a command-line interface that ties together the
crypto2pc and engine modules, allowing users to play multiple rounds,
optionally include short messages, view statistics, and inspect the audit log.

Responsibilities:
  • Display interactive menus and banners
  • Handle user input and menu navigation
  • Persist and display game statistics (rounds played, successful matches)
  • Provide options for simple bit-only rounds or enhanced rounds with messages
  • Allow viewing of the last N lines of the audit.log

Dependencies:
    from engine import GameEngine
    from crypto2pc import clear, view_audit_log
    import json, os, time

Usage:
    python3 cli.py
"""

import os
import json
import time
from typing import Dict
from engine import GameEngine
from crypto2pc import clear, view_audit_log, Color

STATS_FILE = 'stats.json'


def load_stats() -> Dict[str, int]:
    """Load statistics from disk or initialize defaults."""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, ValueError):
            pass
    return {'played': 0, 'success': 0}


def save_stats(stats: Dict[str, int]) -> None:
    """Persist statistics to a JSON file."""
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except IOError:
        print(f"{Color.WARNING.value} Warning: could not save stats.")


def print_banner() -> None:
    """Print the game banner with ASCII art."""
    print('=' * 50)
    print(' 💜 RED CABBAGE 2PC CONFESSION GAME 💜')
    print('=' * 50)


def print_menu() -> None:
    """Display the main menu options."""
    print('1) Play bit-only round')
    print('2) Play enhanced round with messages')
    print('3) View statistics')
    print('4) View audit log')
    print('0) Exit')


def show_stats(stats: Dict[str, int]) -> None:
    """Print current game statistics."""
    played = stats.get('played', 0)
    success = stats.get('success', 0)
    rate = f"{success}/{played}" if played else '0/0'
    print(f"Rounds played : {played}")
    print(f"Matches won   : {success}")
    print(f"Win rate      : {rate}")


def main() -> None:
    """Main loop to drive the CLI menu and game flow."""
    stats = load_stats()
    engine = GameEngine('Alice', 'Bob')

    while True:
        clear()
        print_banner()
        print_menu()
        choice = input('Select an option >>> ').strip()

        if choice == '1':
            clear()
            print('--- Bit-Only Round ---')
            result = engine.play_round(require_message=False)
            stats['played'] += 1
            if result.get('bit_result'):
                stats['success'] += 1
            save_stats(stats)
            input('Press Enter to return to menu...')

        elif choice == '2':
            clear()
            print('--- Enhanced Round (with messages) ---')
            result = engine.play_round(require_message=True)
            stats['played'] += 1
            if result.get('bit_result'):
                stats['success'] += 1
            if result.get('message1'):
                print(f"Alice said: {result['message1']}")
            if result.get('message2'):
                print(f"Bob said: {result['message2']}")
            save_stats(stats)
            input('Press Enter to return to menu...')

        elif choice == '3':
            clear()
            print('--- Game Statistics ---')
            show_stats(stats)
            input('Press Enter to return to menu...')

        elif choice == '4':
            clear()
            print('--- Audit Log (last 20 lines) ---')
            view_audit_log(20)
            input('Press Enter to return to menu...')

        elif choice == '0':
            print('Goodbye! Thanks for playing.')
            break

        else:
            print(f"{Color.WARNING.value} Invalid selection. Please choose from the menu.")
            time.sleep(1)


if __name__ == '__main__':
    main()
