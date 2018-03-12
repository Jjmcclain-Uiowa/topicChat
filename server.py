import sys
import socket
import json
import select

if __name__ == '__main__':

    # check number of command line arguments
    if len(sys.argv) != 2:
        print('invalid arguments')
        sys.exit(0)

    print('------')
    print('>>>Waiting for connection<<<')
    print('------')

    # create a socket, bind it to the port num given, listen for connections
    addr = ('localhost', int(sys.argv[1]))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(addr)
    server_socket.listen(5)

    # create some variables to be used later
    room_dict = {}
    clients = []
    to_write = []

    while True:
        to_read = clients[:]
        to_read.append(server_socket)

        # select statement
        socks_to_read, _, _ = select.select(to_read, [], [])

        # check all the sockets in socks_to_read
        for sock in socks_to_read:

            # check to see if it is a connection request
            if sock == server_socket:

                # accept connection, create socket, get client address,
                # and add socket to clients list
                (client_socket, client_addr) = server_socket.accept()
                clients.append(client_socket)

                # get reg_json and extract room
                reg_json = json.loads(client_socket.recv(256).decode('utf-8'))
                room = reg_json['room']
                username = reg_json['source']['username']
                print('Received registration JSON,'
                      'registering user to chat room')
                print(username + ' has joined ' + room)
                print('------')

                # add client_socket to room_dict or add room
                if room not in room_dict:
                    room_dict[room] = [client_socket]
                else:
                    room_dict[room].append(client_socket)

            # else there must be an incoming message
            else:
                # get the data and convert it to json, extract room
                data = sock.recv(256).decode('utf-8')
                if data:
                    msg_json = json.loads(data)
                    print('Received message: ' + msg_json['message']['text'])
                    print('------')
                    room = msg_json['message']['room']
                    # send message to all sockets in room
                    for s in room_dict[room]:
                        # except itself
                        if s != sock:
                            s.sendall(bytes(json.dumps(msg_json), 'utf-8'))
                    print(msg_json['message']['text'] +
                          ' sent to all users in ' + room)

                # if no data, client has disconnected
                else:
                    print('Client has disconnected from ' + room)

                    # close socket, remove from client list and room_dict
                    sock.close()
                    try:
                        clients.remove(sock)
                        for room in room_dict:
                            room_dict[room].remove(sock)
                    except:
                        continue
