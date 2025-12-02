import math
import random
import socket
import os
import sys
import time

# Global variables
global NUMBER_OF_PREFERRED_NEIGHBORS
global UNCHOKING_INTERVAL
global OPTIMISTIC_UNCHOKING_INTERVAL
global FILE_NAME
global FILE_SIZE
global PIECE_SIZE
global Bitfield
peer_info = {}


def init_Common():
    with open('Common.cfg', 'r') as file:
        print(__name__)
        for line in file:
            if line.startswith('NumberOfPreferredNeighbors'):
                NUMBER_OF_PREFERRED_NEIGHBORS = int(line.split(' ')[1].strip())
            elif line.startswith('UnchokingInterval'):
                UNCHOKING_INTERVAL = int(line.split(' ')[1].strip())
            elif line.startswith('OptimisticUnchokingInterval'):
                OPTIMISTIC_UNCHOKING_INTERVAL = int(line.split(' ')[1].strip())
            elif line.startswith('FileName'):  
                FILE_NAME = line.split(' ')[1].strip()
            elif line.startswith('FileSize'):
                FILE_SIZE = int(line.split(' ')[1].strip())
            elif line.startswith('PieceSize'):
                PIECE_SIZE = int(line.split(' ')[1].strip())
        
        NUM_PIECES = math.ceil(FILE_SIZE/PIECE_SIZE) # to update the number of pieces

def handshake(peer_id):
    # Create handshake message
    pstr = "P2PFILESHARINGPROJ" #handshake header
    pstrlen = len(pstr)
    zero_bits = bytes(10)  # 10 bytes of zero
    peer_id_bytes = peer_id.to_bytes(4, byteorder='big')
    handshake_msg = pstr.encode('utf-8') + zero_bits + peer_id_bytes #total of 32 bits
    return handshake_msg


def actual_mes(length, message_type): #work in progress
    if (message_type < 0 or message_type > 7):
        raise ValueError("Invalid message type")
    elif(message_type == 0, 1, 2, 3): # This is for choke, unchoke, interested, and not interested
        #how we will access time for the logs and such - time.ctime() for the log
        payload = 0
    elif(message_type == 4): #have
        payload = 4
    elif(message_type == 5): #This is the bitfield from the file, first thing after handshake
        payload = 16 # need to figure out the bitfield from the file
    elif(message_type == 6): #the request field, different than BitTorrent
        payload = 4 
    elif(message_type == 7): #the piece field
        payload = 4
        #actually the content of the piece
    
    # Create actual message
    return length.to_bytes(4, byteorder='big') + message_type.to_bytes(1,byteorder='big') + payload #may need to fix payload


def PeerInfo_init():

    with open('PeerInfo.cfg', 'r') as file: # peerinfo is like a tracker equivalent in BitTorrent
        #peer_info = {}
        for line in file:
            parts = line.split(' ')
            peer_id = int(parts[0].strip())
            #print(f"Peer ID: {peer_id}") used as a check
            host_name = parts[1].strip()
            port_number = int(parts[2].strip())
            has_file = parts[3].strip() == '1'
            peer_info[peer_id] = (host_name, port_number, has_file)
            #print(peer_info[1001]) used a check
            os.makedirs(f'peer_{peer_id}', exist_ok=True) #this makes the directory as long as it has nto been created yet

    #how to access: peer_info[1001][0]

#need a main or header file and src file but here is a couple functions

def peerProcess(peerID): #int the peer process id
    # Initialize peer process
    if peerID not in peer_info:
        print(f"Peer ID {peerID} not found in PeerInfo.cfg")
        sys.exit(1)

    host_name, port_number, has_file = peer_info[peerID]
    with open(f'log_peer_{peerID}.log', "w") as log_peer: # will create the log file for the specific peer process
        log_peer.write("started the peer process\n")
    print(f"Starting peer {peerID} at {host_name}:{port_number}, Has file: {has_file}")

    # Create a socket for the peer
    init_Common()

    # Further implementation would go here (handling connections, file pieces, etc.)


if __name__ == "__main__": # start us the process
    time.ctime() #gets the current time - needs to get parsed
    print(f'Program started at {time.ctime()}') # a check to make sure it is getting the time
    PeerInfo_init()
    peerProcess(1001)

