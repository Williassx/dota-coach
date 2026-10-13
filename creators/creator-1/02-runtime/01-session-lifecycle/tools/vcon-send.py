"""Send a console command to a running hidden Dota client via vconsole.

Protocol observed in creator 2's vcon-query.cjs (CMND / PRNT chunks with
magic 0x00d40000); this is an independent Python implementation, not a copy.
Usage: python vcon-send.py <command> <out.jsonl> <timeout_ms> [port]
"""
import json
import socket
import sys
import time
from pathlib import Path

MAGIC = 0x00D40000


def send_marker_packet(sock: socket.socket, command: str) -> None:
    payload = command.encode("utf-8") + b"\x00"
    header = b"CMND" + MAGIC.to_bytes(4, "big") + (len(payload) + 12).to_bytes(2, "big")
    sock.sendall(header + payload)


def parse(recv: memoryview):
    chunks = []
    while len(recv) >= 12:
        length = int.from_bytes(recv[8:10], "big")
        if int.from_bytes(recv[4:8], "big") != MAGIC or length < 12 or len(recv) < length:
            break
        chunk_type = bytes(recv[0:4]).decode("ascii", "replace")
        if chunk_type == "PRNT" and length >= 40:
            text = bytes(recv[40:length]).decode("utf-8", "replace").rstrip("\x00")
            chunks.append(text)
        recv = recv[length:]
    return chunks, recv


def main() -> int:
    command, out_path, timeout_ms, port = (
        sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 29001)
    marker = "C1LC_" + command[:8]
    target = Path(out_path)
    if target.exists():
        print("Output exists; not overwriting:", target)
        return 2
    lines = []
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        sock.settimeout(0.4)
        send_marker_packet(sock, "echo " + marker)
        send_marker_packet(sock, command)
        deadline = time.monotonic() + timeout_ms / 1000
        buf = b""
        started = False
        while time.monotonic() < deadline:
            try:
                data = sock.recv(65536)
                if not data:
                    break
                buf = buf + data if buf else data
                chunks, buf_bytes = parse(memoryview(buf))
                buf = bytes(buf_bytes)
                for text in chunks:
                    if marker in text:
                        started = True
                    if started:
                        lines.append(text)
                        with target.open("a", encoding="utf-8") as handle:
                            handle.write(json.dumps({"utc": time.time(), "text": text}) + "\n")
            except socket.timeout:
                continue
            except (ConnectionResetError, OSError) as error:
                print("socket:", error)
                break
    print(json.dumps({"marker_received": started, "live_lines": len(lines)}))
    return 0 if started else 1


if __name__ == "__main__":
    raise SystemExit(main())
