#!/usr/bin/env python3
"""Stream-inflate a single-member zip from stdin straight onto a block device.

Written for the ClearPass KVM image, whose zip member inflates to ~45 GiB. The
point is to never materialise that file: pipe the ~5 GB compressed stream to the
hypervisor over ssh, inflate here, and write directly to the guest's logical
volume. Integrity is checked against the size and CRC32 recorded in the zip's
own local file header, so a truncated transfer cannot pass silently.

Usage:
    stream-inflate-zip.py <device> <expected_crc32_hex> <expected_size_bytes>

Typical invocation from the workstation holding the zip:

    ssh root@<host> 'cd /root/cppm && python3 stream-inflate-zip.py \\
        /dev/<vg>/vm-<vmid>-disk-0 2572e1fe 48318382080' < CPPM-...-KVM.raw.zip

Read the expected values off the archive first:

    python3 -c "import zipfile; i=zipfile.ZipFile('<zip>').infolist()[0]; \\
        print(i.file_size, hex(i.CRC))"

Do NOT stage this script in /tmp on a Proxmox host: Python places the script's
own directory first on sys.path, and a stray /tmp/struct.py will shadow the
stdlib module and kill the run at import.

Exit status is 0 only on an exact size and CRC32 match.
"""
import os
import struct
import sys
import zlib

CHUNK = 4 << 20


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    device, expect_crc_hex, expect_size = sys.argv[1], sys.argv[2], int(sys.argv[3])
    expect_crc = int(expect_crc_hex, 16)

    inp = sys.stdin.buffer
    header = inp.read(30)
    if header[:4] != b'PK\x03\x04':
        sys.exit('not a zip local file header: %r' % header[:4])
    namelen, extralen = struct.unpack('<HH', header[26:30])
    inp.read(namelen + extralen)

    decomp = zlib.decompressobj(-15)  # raw deflate, no zlib wrapper
    crc = 0
    total = 0
    with open(device, 'wb') as out:
        while True:
            chunk = inp.read(CHUNK)
            if not chunk:
                break
            data = decomp.decompress(chunk)
            if data:
                out.write(data)
                crc = zlib.crc32(data, crc)
                total += len(data)
            if decomp.eof:
                break
        tail = decomp.flush()
        if tail:
            out.write(tail)
            crc = zlib.crc32(tail, crc)
            total += len(tail)
        out.flush()
        os.fsync(out.fileno())

    crc &= 0xffffffff
    print('written=%d expected=%d' % (total, expect_size))
    print('crc=0x%08x expected=0x%08x' % (crc, expect_crc))
    if total == expect_size and crc == expect_crc:
        print('MATCH')
        return 0
    print('MISMATCH')
    return 1


if __name__ == '__main__':
    sys.exit(main())
