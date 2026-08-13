#!/usr/bin/env python3
"""Emit QEMU-monitor sendkey commands that type a literal string into a guest.

The ClearPass setup wizard renders on the VGA console only (its kernel command
line ends with `console=tty0`, which wins for userspace), so a serial port shows
the boot but never the questions. The only way to answer them programmatically
is synthesised key events through the QEMU monitor.

Usage:
    console-type.py "some text"      # keystrokes for the text
    console-type.py --key ret esc    # named keys, in order

Pipe the output into the monitor, then screenshot to confirm what landed:

    console-type.py "192.168.1.5/24" | qm monitor <vmid>
    echo 'sendkey ret'               | qm monitor <vmid>
    echo 'screendump /tmp/x.ppm'     | qm monitor <vmid>

Always screenshot after each answer. The 6.14 wizard's question set differs from
the installation guide's, so a pre-baked answer list desyncs and every later
answer lands in the wrong field.

Suppress this script's output when typing a password — the sendkey lines spell
it out one character per line.
"""
import sys

# Characters reachable only with shift, mapped to the unshifted key name.
SHIFTED = {
    '!': '1', '@': '2', '#': '3', '$': '4', '%': '5',
    '^': '6', '&': '7', '*': '8', '(': '9', ')': '0',
    '_': 'minus', '+': 'equal', '{': 'bracket_left', '}': 'bracket_right',
    ':': 'semicolon', '"': 'apostrophe', '~': 'grave_accent',
    '|': 'backslash', '<': 'comma', '>': 'dot', '?': 'slash',
}
PLAIN = {
    '-': 'minus', '=': 'equal', '[': 'bracket_left', ']': 'bracket_right',
    ';': 'semicolon', "'": 'apostrophe', '`': 'grave_accent',
    '\\': 'backslash', ',': 'comma', '.': 'dot', '/': 'slash', ' ': 'spc',
}


def keys_for(char):
    """Return the QEMU sendkey argument that produces `char`."""
    if char.islower() or char.isdigit():
        return char
    if char.isupper():
        return 'shift-' + char.lower()
    if char in SHIFTED:
        return 'shift-' + SHIFTED[char]
    if char in PLAIN:
        return PLAIN[char]
    raise SystemExit('unmappable character: %r' % char)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == '--key':
        for name in sys.argv[2:]:
            print('sendkey %s' % name)
        return
    for char in sys.argv[1]:
        print('sendkey %s' % keys_for(char))


if __name__ == '__main__':
    main()
