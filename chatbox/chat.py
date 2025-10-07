import socket
import threading

PORT = 5005

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to external IP to get local IP without sending data
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

LOCAL_IP = get_local_ip()

def receive():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))
    while True:
        data, addr = sock.recvfrom(1024)
        sender_ip = addr[0]
        if sender_ip != LOCAL_IP:
            print(f"\nFriend ({sender_ip}): {data.decode()}\n> ", end='')

def send(friend_ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        msg = input("> ")
        if msg.strip() == "":
            continue
        sock.sendto(msg.encode(), (friend_ip, PORT))
        print(f"Sent to {friend_ip}: {msg}")

if __name__ == "__main__":
    print(f"Your local IP is: {LOCAL_IP}")
    friend_ip = input("Enter your friend’s IP address: ").strip()
    print(f"Chatting with {friend_ip} on port {PORT}...\n")

    threading.Thread(target=receive, daemon=True).start()
    send(friend_ip)
