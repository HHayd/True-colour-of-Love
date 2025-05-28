#!/usr/bin/env python3
"""
engine.py — Protocol Engine for Secure Two-Party Commit-Reveal

This module builds on crypto2pc.py to implement an interactive engine
that orchestrates multi-phase commit-reveal rounds for both a single-bit
choice and an optional short text message. It provides:
  • Player: encapsulates per-player state (name, commits, salts).
  • RoundContext: handles commit and reveal phases with timing
    safeguards and optional message commitments.
  • GameEngine: high-level API to play rounds, enforce timeouts,
    and display results with ANSI colors.

Dependencies:
    from crypto2pc import (
        commit_bit, verify_bit,
        commit_message, verify_message,
        clear, Color, IntegrityError, view_audit_log
    )
    import time, threading

Usage example:
    engine = GameEngine('Alice', 'Bob')
    result = engine.play_round(require_message=True)
    # result is a dict: {'bit_result': bool, 'message': str or None}
"""

import time
import threading
from typing import Optional, Dict, Tuple
from crypto2pc import (
    commit_bit, verify_bit,
    commit_message, verify_message,
    clear, Color, IntegrityError
)

# ---------- Player Class ----------
class Player:
    """
    Represents one participant in the 2PC protocol.
    Attributes:
      name         (str)
      bit_commit   (str) and bit_salt (str)
      msg_commit   (str) and msg_salt (str)
      selected_bit (int)
      selected_msg (Optional[str])
    """
    def __init__(self, name: str):
        self.name = name
        self.selected_bit: Optional[int] = None
        self.bit_commit: Optional[str] = None
        self.bit_salt: Optional[str] = None
        self.selected_msg: Optional[str] = None
        self.msg_commit: Optional[str] = None
        self.msg_salt: Optional[str] = None

    def commit_choice(self, bit: int) -> None:
        """Commit a single-bit choice."""
        digest, salt = commit_bit(bit)
        self.selected_bit = bit
        self.bit_commit = digest
        self.bit_salt = salt
        print(f"[{self.name}] bit committed: {digest[:8]}...")

    def commit_message(self, message: str) -> None:
        """Optionally commit a text message."""
        digest, salt = commit_message(message)
        self.selected_msg = message
        self.msg_commit = digest
        self.msg_salt = salt
        print(f"[{self.name}] message committed.")

    def reveal_choice(self) -> Tuple[int, str]:
        """Return the bit and its salt for verification."""
        return self.selected_bit, self.bit_salt

    def reveal_message(self) -> Tuple[str, str]:
        """Return the message and its salt for verification."""
        return self.selected_msg, self.msg_salt

# ---------- RoundContext Class ----------
class RoundContext:
    """
    Manages the commit and reveal phases for two players.
    Supports timeouts on commit and reveal phases to prevent stalling.
    """
    TIMEOUT = 30  # seconds per phase

    def __init__(self, player1: Player, player2: Player):
        self.p1 = player1
        self.p2 = player2
        self._timer: Optional[threading.Timer] = None

    def _start_timeout(self, phase: str):
        def on_timeout():
            print(f"Timeout during {phase} phase. Aborting round.")
            raise TimeoutError(phase)
        self._timer = threading.Timer(self.TIMEOUT, on_timeout)
        self._timer.start()

    def _cancel_timeout(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def commit_phase(self) -> None:
        """Ask each player to commit their bit under a timeout."""
        for player in (self.p1, self.p2):
            self._start_timeout('commit')
            while True:
                raw = input(f"[{player.name}] Enter choice (yes/no): ").strip().lower()
                if raw in ('yes','y','1'):
                    bit = 1
                elif raw in ('no','n','0'):
                    bit = 0
                else:
                    print("Invalid input. Please enter yes or no.")
                    continue
                try:
                    player.commit_choice(bit)
                finally:
                    self._cancel_timeout()
                break

    def reveal_phase(self, require_message: bool=False) -> None:
        """Reveal and verify commitments under a timeout."""
        for player in (self.p1, self.p2):
            self._start_timeout('reveal')
            # Verify bit
            bit, salt = player.reveal_choice()
            try:
                verify_bit(player.bit_commit, bit, salt)
                print(f"[{player.name}] bit verify OK.")
            except IntegrityError as e:
                self._cancel_timeout()
                raise
            # Optionally verify message
            if require_message and player.msg_commit:
                msg, msalt = player.reveal_message()
                try:
                    verify_message(player.msg_commit, msg, msalt)
                    print(f"[{player.name}] message verify OK.")
                except IntegrityError:
                    self._cancel_timeout()
                    raise
            self._cancel_timeout()

    def compute_and(self) -> bool:
        """Compute the logical AND of both players' bits."""
        return bool(self.p1.selected_bit & self.p2.selected_bit)

# ---------- GameEngine Class ----------
class GameEngine:
    """
    High-level interface to play a commit-reveal round.
    """
    def __init__(self, name1: str, name2: str):
        self.player1 = Player(name1)
        self.player2 = Player(name2)

    def play_round(self, require_message: bool=False) -> Dict[str, Optional[str]]:
        """
        Execute a full commit-reveal round:
          1) commit_phase()
          2) optional message commitment
          3) reveal_phase()
          4) compute_and() and display result

        Returns a dict with keys:
          'bit_result': bool
          'message1': str or None
          'message2': str or None
        """
        clear()
        print("=== New 2PC Round ===")
        # Commit bits
        self.p1 = Player(self.player1.name)
        self.p2 = Player(self.player2.name)
        context = RoundContext(self.p1, self.p2)
        context.commit_phase()

        # Optional message
        if require_message:
            for player in (context.p1, context.p2):
                msg = input(f"[{player.name}] Enter a short message (or blank to skip): ")
                if msg:
                    player.commit_message(msg)

        # Reveal and verify
        try:
            context.reveal_phase(require_message)
        except IntegrityError:
            print(Color.WARNING.value, "Integrity error! Round aborted.")
            return {'bit_result': False, 'message1': None, 'message2': None}

        # Compute AND
        result = context.compute_and()
        block = Color.GREEN.value if result else Color.PURPLE.value
        print(f"Result block: {block}")
        print("Both chose yes!" if result else "At least one said no.")

        return {
            'bit_result': result,
            'message1': context.p1.selected_msg,
            'message2': context.p2.selected_msg
        }

# ---------- Module Exports ----------
__all__ = [
    'Player', 'RoundContext', 'GameEngine'
]
