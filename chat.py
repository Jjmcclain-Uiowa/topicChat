import socket
import sys
import json
import select

if __name__ == '__main__':

    # check if direct mode
    if sys.argv[1] == '-direct':

        # check if client or server
        if int(sys.argv[2]) == 0:
            # create client
            # extract ip and port from command line
            addr_list = sys.argv[3].split(':')
            addr = (addr_list[0], int(addr_list[1]))

            # create client socket and connect to server

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(addr)
            print('Connected! ')

            while True:
                # select statement
                to_read, _, _ = select.select([client_socket, sys.stdin], [], [])

                # if there is a message to send
                if sys.stdin in to_read:
                    # get msg, convert it to 'json'
                    msg = str(input())
                    msg_json = json.dumps({
                        'source': {
                            'ip': 'localhost',
                            'port': addr_list[1]
                        },
                        'destination': {
                            'ip': addr_list[0],
                            'port': addr_list[1]
                        },
                        'message': {
                            'topic': '---',
                            'text': msg
                        }
                    })

                    # send msg_json to socket
                    client_socket.send(bytes(msg_json, 'utf-8'))
                    print('-----------')

                # if there is data to read from the server
                if client_socket in to_read:
                    # get the data, convert to json, print text
                    msg_json = json.loads(client_socket.recv(256).decode('utf-8'))
                    print('Server: ' + msg_json['message']['text'])

        # else create server
        else:
            # create socket, bind it to port, listen for connections
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('localhost', int(sys.argv[2])))
            server_socket.listen(5)
            print('>>>Waiting for connection<<<')

            # create a list of all connected clients
            clients = []

            while True:
                # select statement
                to_read = clients[:]
                to_read.append(server_socket)
                socks_to_read, _, _ = select.select(to_read, [], [])

                # iterate through all sockets that have something waiting to be read
                for sock in socks_to_read:

                    # check if it is a new connection
                    if sock == server_socket:

                        # accept connection, create a new socket, get client_addr, add socket to clients list
                        (client_socket, client_addr) = server_socket.accept()
                        clients.append(client_socket)
                        print('Client connected!')

                    # else there is a message
                    else:

                        # send the data back to each client
                        data = sock.recv(256)
                        if data:
                            print('----------------')
                            print('>>>Data has been received. Sending it to all clients<<<')
                            for s in clients:
                                s.send(data)
                            print('Data sent!')
                            print('----------------')

                        # if no data, client has disconnected
                        else:
                            print('Client has disconnected')

                            # close socket and it remove from clients
                            sock.close()
                            try:
                                clients.remove(sock)
                            except:
                                continue

    #  check if topic mode
    if sys.argv[1] == '-topic':

        # extract ip, port#, and topic from command line arguments
        addr_list = sys.argv[2].split(':')
        addr = (addr_list[0], int(addr_list[1]))
        topic = sys.argv[3]

        # Create a socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect the client_socket to the server
        client_socket.connect(addr)
        print('connected to server!')
        print('------')

        # create registration 'json'
        reg_json = json.dumps({
            'source': {
                'ip': 'localhost',
                'port': addr_list[1]
            },
            'topic': topic},
        )

        # send reg_json to the socket
        client_socket.sendall(bytes(reg_json, 'utf-8'))
        print('Sent Registration JSON, Type your message!')
        print('------')

        while True:

            to_read, _, _ = select.select([client_socket, sys.stdin], [], [])

            #
            if sys.stdin in to_read:
                # get msg, convert it to 'json'
                msg = input()
                msg_json = json.dumps({
                    'source': {
                        'ip': 'localhost',
                        'port': addr_list[1]
                    },
                    'destination': {
                        'ip': addr_list[0],
                        'port': addr_list[1]
                    },
                    'message': {
                        'topic': topic,
                        'text': msg
                    }
                })

                # send msg_json to socket
                client_socket.send(bytes(msg_json, 'utf-8'))

            # if there is data from the server
            if client_socket in to_read:
                # get data, convert it to json, extract text
                msg_json = json.loads(client_socket.recv(256).decode('utf-8'))
                text = msg_json['message']['text']

                # print text
                print(topic + ': ' + text)



















