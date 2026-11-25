#!/usr/bin/env python3
"""One-line office joke entry for make.fun.

Writes a single original joke about office life to /output/entry.txt.
The gate: UTF-8 text of 1 to 200 characters, not only whitespace.
No network, no randomness, stdlib only, deterministic.
"""
import os
import sys

ENTRY = (
    "HR said my job title was self-explanatory, which is awkward, "
    "because nobody in this office can explain what I actually do."
)

DEFAULT_OUTPUT = "/output/entry.txt"
MIN_CHARS = 1
MAX_CHARS = 200


def validate(text):
    """Return an error string if text fails the gate, else None."""
    if not isinstance(text, str):
        return "entry is not text"
    if len(text) < MIN_CHARS:
        return "entry is empty"
    if len(text) > MAX_CHARS:
        return "entry exceeds %d characters (%d)" % (MAX_CHARS, len(text))
    if not text.strip():
        return "entry is only whitespace"
    if "\n" in text or "\r" in text:
        return "entry must be a single line"
    for ch in text:
        if ord(ch) < 0x20 and ch not in ("\t",):
            return "entry contains a control character"
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return "entry is not UTF-8 text"
    return None


def write_entry(path):
    error = validate(ENTRY)
    if error is not None:
        raise SystemExit("gate failed: " + error)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(ENTRY)
    # Read-back check: the file on disk must be exactly the entry.
    with open(path, "r", encoding="utf-8", newline="") as fh:
        written = fh.read()
    if written != ENTRY:
        raise SystemExit("read-back mismatch: file differs from entry")
    return path


def self_test():
    """Validate the gate, including rejection cases. Exit 0 on pass."""
    failures = []

    def check(name, text, should_pass):
        error = validate(text)
        if should_pass and error is not None:
            failures.append("%s: should pass but failed: %s" % (name, error))
        if not should_pass and error is None:
            failures.append("%s: should fail but passed" % name)

    check("chosen entry", ENTRY, True)
    check("empty", "", False)
    check("whitespace only", "   \n\t  ", False)
    check("multi-line", "setup\npunchline", False)
    check("over limit", "x" * 201, False)
    check("at limit", "x" * 200, True)
    check("single char", "!", True)
    check("control char", "joke\x01here", False)

    # Round-trip: write to a temp file and read back byte-exact.
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "entry.txt")
        write_entry(path)
        with open(path, "rb") as fh:
            raw = fh.read()
        if raw != ENTRY.encode("utf-8"):
            failures.append("round-trip bytes differ from entry")
        if raw.endswith(b"\n"):
            failures.append("entry must not end with a trailing newline")

    if failures:
        for failure in failures:
            print("FAIL: " + failure, file=sys.stderr)
        return 1
    print("self-test passed: entry is %d chars, %d bytes"
          % (len(ENTRY), len(ENTRY.encode("utf-8"))))
    return 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    output = os.environ.get("ENTRY_OUTPUT") or DEFAULT_OUTPUT
    args = [a for a in argv[1:] if not a.startswith("-")]
    if args:
        output = args[0]
    write_entry(output)
    print("wrote %d chars to %s" % (len(ENTRY), output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
