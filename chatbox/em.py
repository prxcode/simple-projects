#!/usr/bin/env python3
import socket, sys, time, select, argparse

def main():
    ap = argparse.ArgumentParser(description="Serverless LAN chat over UDP broadcast")
    ap.add_argument("-p", "--port", type=int, default=56789, help="UDP port to use (default 56789)")
    ap.add_argument("-n", "--name", default=None, help="Nickname (default: hostname + pid)")
    ap.add_argument("--iface", default="0.0.0.0", help="Bind interface IP (default 0.0.0.0)")
    args = ap.parse_args()

    nick = args.name or f"{socket.gethostname()}:{os.getpid() if hasattr(sys, 'argv') else int(time.time())}"

    # Create UDP socket for recv
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except Exception:
        pass
    recv_sock.bind((args.iface, args.port))

    # Create UDP socket for send (broadcast)
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    broadcast_addr = ("255.255.255.255", args.port)
    print(f"[ready] {nick} on port {args.port}. Type messages and press Enter. Ctrl+C to quit.", flush=True)

    # Nonblocking loop
    recv_sock.setblocking(False)
    stdin_fd = sys.stdin.fileno()
    while True:
        try:
            rlist, _, _ = select.select([recv_sock, stdin_fd], [], [], 0.5)
            if recv_sock in rlist:
                data, addr = recv_sock.recvfrom(65535)
                try:
                    text = data.decode("utf-8", errors="replace")
                except Exception:
                    text = repr(data)
                ts = time.strftime("%H:%M:%S")
                print(f"[{ts}] {addr[0]}: {text}", flush=True)
            if stdin_fd in rlist:
                line = sys.stdin.readline()
                if not line:
                    break
                msg = line.rstrip("\n")
                if not msg:
                    continue
                payload = f"{nick}: {msg}".encode("utf-8")
                send_sock.sendto(payload, broadcast_addr)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    import os
    main()
