import sys
import socket
import json
import select

if __name__ == '__main__':

    # check number of line arguments
    if len(sys.argv) != 3:
        print('wrong num args')
        sys.exit(0)

    # extract ip, port#, and topic from command line arguments
    addr_list = sys.argv[1].split(':')
    addr = (addr_list[0], int(addr_list[1]))
    topic = sys.argv[2]

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
            print(topic, ': ', text)



