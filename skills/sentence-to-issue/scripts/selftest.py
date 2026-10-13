#!/usr/bin/env python3
"""selftest.py — regression guard for privacy_scan.py. Run it with no arguments.

Each case asserts the exit code privacy_scan.py must return. The last two cases
are there because both regressions shipped for real: a `privacy-allow` marker
that hid a level-2 secret from the scanner, and a marker sitting between two
words that got spliced into a "user" + "name: bob" hit — a string that exists
nowhere in the file. Keep them. (Spelled apart even here: this file must still
self-scan clean.)

Values are spelled apart below so this file still self-scans clean.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCAN = os.path.join(HERE, "privacy_scan.py")

MARK_OPEN = "<!-- privacy-allow -->"
MARK_CLOSE = "<!-- /privacy-allow -->"

PASS = "hunter" + "2xyz"                            # level-2 value
TOKEN = "gh" + "p_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + "0123456789"
EMAIL = "alice@" + "example.com"                    # level-1 value

# (name, text, extra scanner argv, expected exit code)
CASES = [
    ("clean text, no findings",
     "nothing sensitive in this sentence", (), 0),
    ("level-1 identity is warned once",
     EMAIL, (), 1),
    ("level-2 password demands confirmation",
     "password: " + PASS, (), 2),
    ("the marker must NOT hide a level-2 secret",
     f"{MARK_OPEN}\npassword: {PASS}\n{MARK_CLOSE}", (), 2),
    ("the marker must not splice boundary characters",
     "user" + MARK_OPEN + MARK_CLOSE + "name: " + PASS[:3] + "b", (), 0),
    ("a token cut apart by a comment is still level-2",
     "tok " + TOKEN[:12] + MARK_OPEN + MARK_CLOSE + TOKEN[12:], (), 2),
    ("a token wrapped across a line break is still level-2",
     TOKEN[:12] + "\n" + TOKEN[12:], (), 2),
    ("--allow silences exactly that authorised value",
     "password: " + PASS, ("--allow", "password: " + PASS), 0),
    ("authorisation is never inherited by omission",
     "password: " + PASS, (), 2),
    ("allowing one value does not spare a different secret",
     "password: " + PASS, ("--allow", "another value entirely"), 2),
]


def run(text, extra=()):
    proc = subprocess.run([sys.executable, SCAN, "-"] + list(extra), input=text,
                          capture_output=True, text=True)
    return proc.returncode


def main():
    if not os.path.isfile(SCAN):
        print(f"cannot find scanner next to this script: {SCAN}", file=sys.stderr)
        return 2

    failed = 0
    for name, text, extra, want in CASES:
        got = run(text, extra)
        ok = got == want
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: exit {got} (want {want})")
        if not ok:
            failed += 1

    if failed:
        print(f"\n{failed} case(s) FAILED — privacy_scan.py has regressed.")
        return 1
    print(f"\nAll {len(CASES)} cases pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
