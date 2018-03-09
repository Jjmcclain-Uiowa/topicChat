import sys
import socket
import json
import select

if __name__ == '__main__':

    # extract ip, port#, and topic from command line arguments
    addr_list = sys.argv[1].split(':')
    addr = (addr_list[0], int(addr_list[1]))
    topic = sys.argv[2]

    # Create a socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # try to connect the client_socket to the server
    connected = False
    while not connected:
        try:
            client_socket.connect(addr)
            connected = True
            print('connected to server!')
            print('------')
        except socket.error:
            print('Failed to Connect. :( retry? y/n')
            msg = input()
            if msg == 'n':
                print('Closing')
                sys.exit(0)
            elif msg == 'y':
                print('Attempting to reconnect')
            else:
                print('Input not recognized, reconnecting anyways')

    # Get Username
    print('------')
    username = input('Choose a Username: ')
    if username == "":
        username = 'Anonymous'

    # create message 'json'
    reg_json = json.dumps({
                    'source': {
                            'ip': 'localhost',
                            'port': addr_list[1],
                            'username': username
                    },
                    'topic': topic},
                )

    # send reg_json to the socket
    client_socket.sendall(bytes(reg_json, 'utf-8'))
    print('You have been registered with the server!')
    print('(type -q to exit)')
    print('Start Chatting!')
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
                                'text': msg,
                                'username': username
                            }
            })

            # if -q, exit
            if msg == '-q':
                sys.exit(0)

            # send msg_json to socket
            client_socket.send(bytes(msg_json, 'utf-8'))

        # if there is data from the server
        if client_socket in to_read:

            # get data, convert it to json, extract text
            msg_json = json.loads(client_socket.recv(256).decode('utf-8'))
            text = msg_json['message']['text']
            sending_user = msg_json['message']['username']

            # print text
            print(sending_user + '(' + topic + '): ' + text)
