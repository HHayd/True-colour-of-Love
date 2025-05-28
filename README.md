# True-colour-of-Love
# PROJECT_OVERVIEW

## Overview:

This code transforms the red cabbage juice color-change experiment into a secure, two-party commit-reveal game, enabling participants to "confess" their true feelings in the terminal without any embarrassment. By exchanging cryptographic commitments and only unveiling the shared result, the system guarantees that each person’s private choice remains hidden unless both agree—making every confession bold and worry-free.

## Details:

The implementation relies on Python’s built-in libraries:

• **hashlib**: SHA-256 hashing for commitment construction and verification.
• **secrets**: Cryptographically secure random salt generation.
• **os**, **platform**: Cross-platform terminal clearing to hide sensitive prompts.
• **logging**: Audit logging of commit and verify events in `audit.log`.
• **json**: Persistent storage of game statistics (`stats.json`).
• **threading**: Timeout enforcement during commit/reveal phases to prevent stalling.
• **enum**: ANSI color code definitions for green, purple, and warning markers.

The codebase is organized into three modules:

1. **crypto2pc.py**

   * Implements commit/verify for both single bits and optional messages.
   * Provides `clear()`, ANSI color constants, audit logging, and a log viewer.

2. **engine.py**

   * Defines `Player`, `RoundContext`, and `GameEngine` classes.
   * Manages commit and reveal phases with optional text messages and timeouts.
   * Computes the logical AND of both players’ choices and displays results.

3. **cli.py**

   * Offers a user-friendly terminal menu to start a bit-only or message-enhanced round.
   * Displays and updates game statistics, and allows audit log inspection.

## Usage:

Place all three scripts in the same directory and run:

```
python3 cli.py
```

Follow the on-screen prompts to play, view stats, or inspect the audit log. Enjoy a secure, embarrassment-free 2PC confession!
