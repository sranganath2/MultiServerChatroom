import socket
import argparse
import threading
import sys
import hashlib
import time
import logging
import os

logging.basicConfig(filename="logs.log", format="%(message)s", filemode="a")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
global_chunk_list = []
global_chunks_requested = [] #TODO the jank


# TODO: Implement P2PClient that connects to P2PTracker
tracker_HOST = "localhost"
tracker_PORT = 5100
#hostname = socket.gethostname()
tracker = socket.socket()
tracker.connect((tracker_HOST, tracker_PORT))


def read_local_chunks(folder_path):
    '''
    read chunks from local_chucks, hash file chuck, send to tracker
    :return:
    '''
    local_chunk_txt = folder_path + "/local_chunks.txt"
    f = open(local_chunk_txt, "r")
    global global_chunk_list
    global_chunk_list = f.read().strip().split("\n")

    last_chunk = global_chunk_list [-1].split(",")[0]
    global_chunk_list = global_chunk_list[:-1]
    f.close()

    # message = ""

    for chunk in global_chunk_list :
        chunk_path = folder_path + "/" + chunk.split(",")[1]
        file_chunk = open(chunk_path, "rb")
        f = file_chunk.read()
        hash_chunk = hashlib.sha1(f)
        file_chunk.close()

        chunk_num = chunk.split(",")[0]
        message = "LOCAL_CHUNKS," + str(chunk_num) + "," + hash_chunk.hexdigest() + "," + "localhost" + "," + str(
            host_port) + "\n"

        log_message = "LOCAL_CHUNKS," + str(chunk_num) + "," + hash_chunk.hexdigest() + "," + "localhost" + "," + str(
            host_port)  # + "\n"
        print("SENDING TRACKER: " + message)
        tracker.send(message.encode('utf-8'))
        logger.info("%s,%s", NAME, log_message)
        time.sleep(1)

    send_request_chunks(int(last_chunk))
    main_loop(int(last_chunk))


def checkAinB(A, B):
    #function for below
    return set(A).issubset(set(B))

def send_request_chunks(num_chunks):
    # what chunks do we need?
    chunk_num = [int(chunk.split(",")[0]) for chunk in global_chunk_list]
    needed_chunks = [i for i in range(1, num_chunks + 1) if i not in chunk_num]
    needed_chunks.sort()
    global global_chunks_requested
    global_chunks_requested.sort()
    #TODO send one at a time, not all of them
    for chunk in needed_chunks:
        if chunk not in global_chunks_requested:
            message = "WHERE_CHUNK," + str(chunk)  # + "\n"
            print("SENDING TO TRAKCER:" + message)
            logger.info("%s,%s", NAME, message)
            tracker.send(message.encode('utf-8'))

            # need some way to send the next chunk in line instead of repeating
            global_chunks_requested.append(chunk)
            time.sleep(1)
            break
        elif needed_chunks == global_chunks_requested: #handle case that we have looped through all needed chunks and request the first chunk again
            global_chunks_requested = []
            chunk = needed_chunks[0]
            message = "WHERE_CHUNK," + str(chunk)  # + "\n"
            print("SENDING TO TRAKCER:" + message)
            tracker.send(message.encode('utf-8'))
            logger.info("%s,%s", NAME, message)
            # need some way to send the next chunk in line instead of repeating
            global_chunks_requested.append(chunk)
            #resend the first chunk in needed_chunks
            time.sleep(1)

        else:
            continue


def listenToPeer(peer_socket, address):  # send the peer the chunk it needs
    size = 1024
    # x = peer_socket.recv(size)
    chunk_request = str(peer_socket.recv(size).decode("utf-8")).split(",")[1]

    filename = folder + "/" + "chunk_" + chunk_request
    #print("SENDING chunk_" + str(chunk_request))
    with open(filename, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(size)
            if not bytes_read:
                # file transmitting is done
                break
            peer_socket.sendall(bytes_read)
    # close the socket
    peer_socket.close()


def request_chunk_from_peer(chunk_index, ip, peer_port):
    # send REQUEST_CHUNK,<chunk_index> to the peer that has t he chunk
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, int(peer_port)))
        message = "REQUEST_CHUNK," + chunk_index
        s.sendall(message.encode("utf-8"))
        #("REQUESTING CHUNK " + str(chunk_index))
        log_msg = message + "," + "localhost" + "," + peer_port
        logger.info("%s,%s", NAME, log_msg)
        # download the chunk

        download_path = os.path.join(os.getcwd(), folder)

        filename = "chunk_" + chunk_index
        file_to_write = open(os.path.join(download_path, filename), 'wb')
        while True:
            data = s.recv(1024)
            if not data:
                break
            file_to_write.write(data)
        file_to_write.close()
        file_to_write = open(os.path.join(download_path, filename), 'rb')
        # tell tracker we have recived the chunk
        f = file_to_write.read()
        hash_chunk = hashlib.sha1(f)
        file_to_write.close()

        local_chunks_message = "LOCAL_CHUNKS," + str(chunk_index) + "," + hash_chunk.hexdigest() + "," + "localhost" + "," + str(
            host_port) + "\n"

        log_message = "LOCAL_CHUNKS," + str(chunk_index) + "," + hash_chunk.hexdigest() + "," + "localhost" + "," + str(
            host_port)  # + "\n"
        tracker.send(local_chunks_message.encode('utf-8'))
        logger.info("%s,%s", NAME, log_message)
        print("SENDING TRACKER: " + local_chunks_message)
        time.sleep(1)
        print("CHUNK downloaded. Closing client socket")
        s.close()


        # update the chunk list. This function will use this to recompute needed_chunks
        entry = str(chunk_index) + "," + "chunk_" + str(chunk_index)
        global_chunk_list.append(entry) #TODO better pray this doesn't cause race issues...
        print("updated_CHUNKS")
        print(global_chunk_list)

        #update local_chunks.txt
        #remove local_chunks.txt
        #add in the file?


def main_loop(num_chunks):
    # create socket here
    while True:
        data = str(tracker.recv(1024).decode('utf8'))
        for GET_CHUNK_MSG in data.split("\n"):
            command = GET_CHUNK_MSG.split(',')[0]
            if command == "GET_CHUNK_FROM":
                ip = GET_CHUNK_MSG.split(',')[3]
                peer_port = GET_CHUNK_MSG.split(',')[4]
                chunk_index = GET_CHUNK_MSG.split(',')[1]
                #print("GETTING CHUNK " + data.split(',')[1] + " FROM " + ip)
                request_chunk_from_peer(chunk_index, ip, peer_port)
            else:
                send_request_chunks(num_chunks)


def listen_incoming_peer(host, listening_port):

    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #listen_socket.bind((host, listening_port))
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((host, listening_port))
    listen_socket.listen()
    while True:
        peer_socket, address = listen_socket.accept()
        threading.Thread(target=listenToPeer, args=(peer_socket, address)).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-folder', required=True)
    parser.add_argument('-transfer_port', required=True)
    parser.add_argument('-name', required=True)
    args = parser.parse_args()
    global NAME
    NAME = str(args.name)
    global folder
    folder = args.folder
    global host_port
    host_port = int(args.transfer_port)
    global ip_address
    #ip_address = socket.gethostbyname(hostname)
    ip_address = "localhost"
    threading.Thread(target=listen_incoming_peer, args=(ip_address, host_port)).start()

    read_local_chunks(folder)  # read the chunks already present, send them
# connect to another client for the chunk
