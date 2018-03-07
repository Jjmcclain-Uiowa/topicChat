import sys
import socket
import json
import select

if __name__ == '__main__':

    # check number of command line arguments
    if len(sys.argv) != 2:
        print('invalid arguments')
        sys.exit(0)

    print('Waiting for connection')

    # create a socket, bind it to the port num given, listen for connections
    addr = ('localhost', int(sys.argv[1]))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(addr)
    server_socket.listen(5)

    # create some variables to be used later
    topicMap = {}
    clients = []
    to_write = []

    while True:
        to_read = clients[:]
        to_read.append(server_socket)

        # select statement
        socks_to_read, socks_to_write, _ = select.select(to_read, to_write, [])

        # check all the sockets in socks_to_read
        for sock in socks_to_read:

            # check to see if it is a connection request
            if sock == server_socket:

                # accept connection, create socket, get client address, and add socket to clients list
                (client_socket, client_addr) = server_socket.accept()
                clients.append(client_socket)

                # get reg_json and extract topic
                data = client_socket.recv(256)
                reg_json = json.loads(data)
                topic = reg_json['topic']
                print('received: ', reg_json)
                print('New Client registered to topic ', topic)

                # add client_socket to topicMap or add topic
                if topic not in topicMap:
                    topicMap[topic] = [client_socket]
                else:
                    topicMap[topic].append(client_socket)


            # else there must be an incoming message
            else:
                # get the data and convert it to json, extract topic
                msg_json = json.loads(sock.recv(256))
                print('received ', msg_json['message']['text'])
                topic = msg_json['message']['topic']

                # send message to all sockets in topic
                for s in topicMap[topic]:
                    if s != sock:
                        sock.sendall(bytes(json.dumps(msg_json), 'utf-8'))
                        print('message sent')









