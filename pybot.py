#!/usr/bin/env python3
"""Chat with PyBot in a terminal.

    python -m pybot                          interactive chat
    python -m pybot -p "your message"        one reply, then exit
    echo "your message" | python -m pybot    one reply per input line

PyBot itself is the `bot` package next to this file.
This file only adds the command line. It holds no chatbot logic of its own.
"""
import argparse
import os
import random
import sys
import time

__version__ = "0.1.0"

# The commit that `bot/` was copied from.
SOURCE_COMMIT = "24cbc0439e07fd015c0747ab3be6e782a42b5c5b"

# The first lines of the interactive chat: the name in FIGlet's "slant" lettering, then one line
# saying what PyBot is.
LOGO = r"""
    ____        ____        __
   / __ \__  __/ __ )____  / /_
  / /_/ / / / / __  / __ \/ __/
 / ____/ /_/ / /_/ / /_/ / /_
/_/    \__, /_____/\____/\__/
      /____/
""".strip("\n")
TAGLINE = "A chatbot written in plain Python. No weights, no training, just rules."

# What the interactive chat puts in front of each turn.  The bot's answers are
# language-aware modules, while these strings are only the terminal chrome.
USER_PREFIX = "user: "
BOT_PREFIX = "pybot: "

HINT = "Type a message and press Enter. /reset starts a new conversation, /exit quits."
HELP = """Commands:
  /reset   clear the screen and start again (PyBot forgets what was said)
  /help    show this help
  /exit    quit (Ctrl+D works too)"""

_UI = {
    "en": {
        "user_prefix": USER_PREFIX,
        "bot_prefix": BOT_PREFIX,
        "tagline": TAGLINE,
        "hint": HINT,
        "help": HELP,
        "loading": "Loading PyBot...",
        "reset": "New conversation.\n",
        "exit": ("/exit", "/quit", "/bye"),
        "help_commands": ("/help",),
        "reset_commands": ("/reset",),
    },
    "th": {
        "user_prefix": "ผู้ใช้: ",
        "bot_prefix": "บอต: ",
        "tagline": "แชตบอตที่เขียนด้วย Python และตอบด้วยกฎ",
        "hint": "พิมพ์ข้อความแล้วกด Enter /รีเซ็ต เริ่มการสนทนาใหม่ /ออก ออกจากโปรแกรม",
        "help": """คำสั่ง
  /รีเซ็ต   เริ่มการสนทนาใหม่ (บอตจะลืมสิ่งที่คุยกัน)
  /ช่วยเหลือ แสดงความช่วยเหลือนี้
  /ออก      ออกจากโปรแกรม""",
        "reset": "เริ่มการสนทนาใหม่\n",
        "exit": ("/ออก", "/ออกจากโปรแกรม", "/exit", "/quit", "/bye"),
        "help_commands": ("/ช่วยเหลือ", "/help"),
        "reset_commands": ("/รีเซ็ต", "/reset"),
        "loading": "กำลังโหลด PyBot...",
    },
}

# English remains the default so existing scripts and callers keep their
# output.  Thai is selected explicitly with ``--lang th``.
SUPPORTED_LANGUAGES = tuple(_UI)


def load_bot():
    """Import the bot's runtime. The first start compiles every module, so it takes longer."""
    try:
        from bot import runtime
    except ModuleNotFoundError as error:
        if error.name != "bot":
            raise
        # Run from another directory: the bot package sits next to this file.
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from bot import runtime
    return runtime


def _configure_utf8_stdio():
    """Make Thai input and replies work on Windows when no encoding was requested."""
    if os.name != "nt" or os.environ.get("PYTHONIOENCODING"):
        return
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None or stream.isatty():
            continue
        encoding = (getattr(stream, "encoding", "") or "").replace("-", "").replace("_", "").lower()
        if encoding == "utf8":
            continue
        try:
            reconfigure(encoding="utf-8", errors=stream.errors)
        except (OSError, ValueError):
            # Some embedders expose a stream whose encoding cannot be changed.
            continue


def answer(runtime, text, memory):
    """One turn: (reply, module, seconds).

    Mirrors bot/__main__.py: the reply is one non-empty line, and a turn never raises.
    """
    start = time.perf_counter()
    try:
        result = runtime.turn(text, memory)
        reply = " ".join(str(result["reply"]).split()) or "Hello!"
        module = result.get("module")
    except Exception:  # noqa: BLE001 - keep the bot's interface: always one reply
        reply, module = "Hello!", None
    return reply, module, time.perf_counter() - start


def details(module, seconds):
    return "[module: %s | %.0f ms]" % (module or "none", seconds * 1000)


def one_shot(runtime, args):
    """-p without -i: print the reply to one message and exit."""
    reply, module, seconds = answer(runtime, args.prompt, {})
    print(reply, flush=True)
    if args.verbose:
        print(details(module, seconds), file=sys.stderr)


def pipe(runtime, args):
    """Input that is not a terminal: one reply per line, like `python -m bot`."""
    memory = {}
    for line in sys.stdin:
        reply, module, seconds = answer(runtime, line.rstrip("\r\n"), memory)
        print(reply, flush=True)
        if args.verbose:
            print(details(module, seconds), file=sys.stderr, flush=True)


def _ui(args):
    """Return the terminal strings for the selected language."""
    return _UI.get(getattr(args, "lang", "en"), _UI["en"])


def opening(lang="en"):
    """What the chat shows when it starts, and again after /reset."""
    ui = _UI.get(lang, _UI["en"])
    print(LOGO + "\n")
    print(ui["tagline"])
    print(ui["hint"] + "\n")


def clear_screen():
    """Wipe the terminal, including what has scrolled off the top."""
    if os.name == "nt":
        os.system("cls")
    else:
        # Cursor to the top, erase the screen, erase the scrollback.
        sys.stdout.write("\033[H\033[2J\033[3J")
        sys.stdout.flush()


def chat(runtime, args):
    """An interactive conversation in the terminal.

    Every turn is labelled with who is speaking: `user: ` in front of what you type and
    `pybot: ` in front of the reply. /reset clears the conversation: PyBot forgets it, and in a
    terminal the screen is wiped back to the opening.
    """
    try:
        import readline  # noqa: F401 - line editing and history for input()
    except ImportError:
        pass
    ui = _ui(args)
    opening(getattr(args, "lang", "en"))
    memory = {}
    first = args.prompt
    while True:
        if first is not None:
            text, first = first, None
            print(ui["user_prefix"] + text)
        else:
            try:
                text = input(ui["user_prefix"])
            except (EOFError, KeyboardInterrupt):
                print()
                break
        command = text.strip().lower()
        if command in ui["exit"]:
            break
        if command in ui["reset_commands"]:
            memory = {}
            if args.seed is not None:
                random.seed(args.seed)
            if sys.stdout.isatty():
                clear_screen()
                opening(getattr(args, "lang", "en"))
            else:
                print(ui["reset"])
            continue
        if command in ui["help_commands"]:
            print(ui["help"] + "\n")
            continue
        if not command:
            continue
        reply, module, seconds = answer(runtime, text, memory)
        print(ui["bot_prefix"] + reply)
        if args.verbose:
            print(details(module, seconds))
        print()


def main(argv=None):
    _configure_utf8_stdio()
    parser = argparse.ArgumentParser(
        prog="pybot",
        description="Chat with PyBot, a chatbot written in plain Python: no model, no weights.",
        epilog="With no options, PyBot starts an interactive chat. "
               "When input is piped in, it prints one reply per input line.")
    parser.add_argument("-p", "--prompt", metavar="TEXT",
                        help="reply to this one message and exit")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="with -p: keep chatting after the first reply")
    parser.add_argument("-s", "--seed", type=int, metavar="N",
                        help="seed for PyBot's choice of wording, to get the same replies again")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="after each reply, show the module that produced it and the time it took")
    parser.add_argument("--lang", choices=SUPPORTED_LANGUAGES, default="en",
                        help="language for the interactive terminal UI (default: en)")
    parser.add_argument("--version", action="version",
                        version="pybot %s (bot at commit %s)" % (__version__, SOURCE_COMMIT[:12]))
    args = parser.parse_args(argv)
    ui = _UI[args.lang]

    if args.seed is not None:
        random.seed(args.seed)
    interactive = (args.prompt is None and sys.stdin.isatty()) or (args.prompt is not None and args.interactive)
    if interactive:
        print(ui["loading"], end="", file=sys.stderr, flush=True)
    runtime = load_bot()
    if interactive:
        print("\r" + " " * len(ui["loading"]) + "\r", end="", file=sys.stderr, flush=True)
        chat(runtime, args)
    elif args.prompt is not None:
        one_shot(runtime, args)
    else:
        pipe(runtime, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
