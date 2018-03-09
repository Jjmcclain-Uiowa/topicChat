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
    topicDict = {}
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

                # accept connection, create socket, get client address, and add socket to clients list
                (client_socket, client_addr) = server_socket.accept()
                clients.append(client_socket)

                # get reg_json and extract topic
                reg_json = json.loads(client_socket.recv(256).decode('utf-8'))
                topic = reg_json['topic']
                print('Received registration JSON, registering client to topic')
                print('New Client registered to ' + topic)
                print('------')

                # add client_socket to topicMap or add topic
                if topic not in topicDict:
                    topicDict[topic] = [client_socket]
                else:
                    topicDict[topic].append(client_socket)

            # else there must be an incoming message
            else:
                # get the data and convert it to json, extract topic
                data = sock.recv(256).decode('utf-8')
                if data:
                    msg_json = json.loads(data)
                    print('Received message JSON: ' + msg_json['message']['text'])
                    print('------')
                    topic = msg_json['message']['topic']
                    # send message to all sockets in topic
                    for s in topicDict[topic]:
                        # except itself
                        if s != sock:
                            s.sendall(bytes(json.dumps(msg_json), 'utf-8'))
                    print(msg_json['message']['text'] + ' sent to all clients in ' + topic)

                # if no data, client has disconnected
                else:
                    print('Client has disconnected from ' + topic)

                    # close socket, remove from client list and topicDict
                    sock.close()
                    try:
                        clients.remove(sock)
                        for topic in topicDict:
                            topicDict[topic].remove(sock)
                    except:
                        continue









