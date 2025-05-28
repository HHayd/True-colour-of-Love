#!/usr/bin/env python3
"""
crypto2pc.py — Core Cryptographic Utilities and Tools Module

This module implements the commit-reveal primitive using SHA-256 and a random salt,
as well as terminal utilities and audit logging for secure two-party computation (2PC).
It also provides support for committing arbitrary text messages to increase flexibility.

Responsibilities:
  • commit_bit(bit): produce a hex-encoded SHA-256 commitment of a single bit (0 or 1) concatenated with a random salt.
  • verify_bit(commitment, bit, salt_hex): verify a revealed bit and salt against the original commitment.
  • commit_message(message): produce a SHA-256 commitment of an arbitrary UTF-8 string with random salt.
  • verify_message(commitment, message, salt_hex): verify a revealed message and salt against its commitment.
  • clear(): clear the terminal screen cross-platform to hide sensitive input.
  • Color: ANSI-colored block constants for green, purple, and warnings.
  • Audit logging: record each commit and verify event in "audit.log" for security auditing.
  • view_audit_log(lines): display the last N entries from the audit log.

Dependencies: hashlib, secrets, os, platform, logging, enum

Usage example:
    from crypto2pc import (
        commit_bit, verify_bit,
        commit_message, verify_message,
        clear, Color, IntegrityError, view_audit_log
    )

    # Commit a choice bit
    digest, salt = commit_bit(1)

    # Reveal and verify the choice bit
    try:
        verify_bit(digest, 1, salt)
    except IntegrityError:
        print("Integrity check failed for bit commitment.")

    # Commit a message
    msg_digest, msg_salt = commit_message("I love you")

    # Reveal and verify the message
    try:
        verify_message(msg_digest, "I love you", msg_salt)
    except IntegrityError:
        print("Integrity check failed for message.")

    # Clear the screen and display color blocks
    clear()
    print(Color.GREEN.value)

    # View last 20 audit log entries
    view_audit_log(20)
"""

import hashlib
import secrets
import os
import platform
import logging
from enum import Enum

# ---------- Configuration ----------
#: Number of random bytes to use as salt in commitments
SALT_LENGTH = 16

# ---------- Audit Logging Setup ----------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('audit.log', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# ---------- Custom Exception ----------
class IntegrityError(Exception):
    """Raised when a reveal does not match its original commitment."""
    pass

# ---------- Commit-Reveal for a Single Bit ----------

def commit_bit(bit: int) -> tuple[str, str]:
    """
    Commit a single bit (0 or 1) with a random salt.

    Returns:
        commitment: hex-encoded SHA-256 digest of (bit || salt)
        salt_hex:   hex-encoded random salt
    """
    if bit not in (0, 1):
        raise ValueError('commit_bit: bit must be 0 or 1')
    salt = secrets.token_bytes(SALT_LENGTH)
    digest = hashlib.sha256(bytes([bit]) + salt).hexdigest()
    logger.info(f'commit_bit: bit={bit}, digest={digest}')
    return digest, salt.hex()


def verify_bit(commitment: str, bit: int, salt_hex: str) -> None:
    """
    Verify a revealed bit and salt against the original commitment.

    Raises:
        IntegrityError: if recomputed digest does not match commitment.
    """
    try:
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        logger.warning(f'verify_bit: invalid salt hex: {salt_hex}')
        raise IntegrityError('Invalid salt hex')
    digest = hashlib.sha256(bytes([bit]) + salt).hexdigest()
    if digest != commitment:
        logger.warning(f'verify_bit mismatch: computed={digest}, expected={commitment}, bit={bit}')
        raise IntegrityError('Bit commitment mismatch')
    logger.info(f'verify_bit: bit={bit}, commitment OK')

# ---------- Commit-Reveal for an Arbitrary Message ----------

def commit_message(message: str) -> tuple[str, str]:
    """
    Commit an arbitrary UTF-8 string with a random salt.

    Returns:
        commitment: hex-encoded SHA-256 digest of (message_bytes || salt)
        salt_hex:   hex-encoded random salt
    """
    data = message.encode('utf-8')
    salt = secrets.token_bytes(SALT_LENGTH)
    digest = hashlib.sha256(data + salt).hexdigest()
    logger.info(f'commit_message: message="{message[:10]}...", digest={digest}')
    return digest, salt.hex()


def verify_message(commitment: str, message: str, salt_hex: str) -> None:
    """
    Verify a revealed message and salt against the original commitment.

    Raises:
        IntegrityError: if recomputed digest does not match commitment.
    """
    data = message.encode('utf-8')
    try:
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        logger.warning(f'verify_message: invalid salt hex: {salt_hex}')
        raise IntegrityError('Invalid salt hex')
    digest = hashlib.sha256(data + salt).hexdigest()
    if digest != commitment:
        logger.warning(f'verify_message mismatch: computed={digest}, expected={commitment}, message="{message[:10]}..."')
        raise IntegrityError('Message commitment mismatch')
    logger.info(f'verify_message: message verified, commitment OK')

# ---------- Terminal Utility ----------

def clear() -> None:
    """Clear the terminal screen, cross-platform."""
    cmd = 'cls' if platform.system() == 'Windows' else 'clear'
    os.system(cmd)

# ---------- ANSI Color Blocks ----------
class Color(Enum):
    """ANSI-colored blocks for visual output."""
    GREEN   = '\033[92m██\033[0m'  # green block
    PURPLE  = '\033[95m██\033[0m'  # purple block
    WARNING = '\033[93m!!\033[0m'  # yellow warning

# ---------- Audit Log Viewer ----------

def view_audit_log(lines: int = 20) -> None:
    """
    Print the last `lines` entries from the audit log.
    """
    try:
        with open('audit.log', 'r', encoding='utf-8') as f:
            entries = f.readlines()
    except FileNotFoundError:
        print('No audit log found.')
        return
    for entry in entries[-lines:]:
        print(entry.rstrip())

# ---------- Module Exports ----------
__all__ = [
    'commit_bit', 'verify_bit',
    'commit_message', 'verify_message',
    'clear', 'IntegrityError', 'Color', 'view_audit_log'
]
