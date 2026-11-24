"""Fixed interface: one reply per input line. Put bot logic in bot/modules/."""
import sys

from pybot import _configure_utf8_stdio
from .runtime import reply


def main():
    _configure_utf8_stdio()
    memory = {}
    for line in sys.stdin:
        try:
            answer = reply(line.rstrip("\r\n"), memory)
            answer = " ".join(str(answer).split()) or "Hello!"
        except Exception:  # noqa: BLE001 - preserve the bot interface
            answer = "Hello!"
        print(answer, flush=True)


if __name__ == "__main__":
    main()
