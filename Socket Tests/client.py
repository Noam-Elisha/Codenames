import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 12345))
message = None
while message != "done":
	data = s.recv(1024)
	s.send(b"idiot")
	if not data:
		continue
	print("received {} from server".format(data))

s.close()