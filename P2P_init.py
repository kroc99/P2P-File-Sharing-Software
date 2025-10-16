import math
import random
import socket
import os
import sys

# Global variables
with open('Common.cfg', 'r') as file:
    for line in file:
        if line.startswith('NumberOfPreferredNeighbors'):
            NUMBER_OF_PREFERRED_NEIGHBORS = int(line.split(' ')[1].strip())
            print(f"NumberOfPreferredNeighbors: {NUMBER_OF_PREFERRED_NEIGHBORS}")
        elif line.startswith('UnchokingInterval'):
            UNCHOKING_INTERVAL = int(line.split(' ')[1].strip())
            print(f"UnchokingInterval: {UNCHOKING_INTERVAL}")
        elif line.startswith('OptimisticUnchokingInterval'):
            OPTIMISTIC_UNCHOKING_INTERVAL = int(line.split(' ')[1].strip())
            print(f"OptimisticUnchokingInterval: {OPTIMISTIC_UNCHOKING_INTERVAL}") 
        elif line.startswith('FileName'):  
            FILE_NAME = line.split(' ')[1].strip()
            print(f"FileName: {FILE_NAME}")
        elif line.startswith('FileSize'):
            FILE_SIZE = int(line.split(' ')[1].strip())
            print(f"FileSize: {FILE_SIZE}")
        elif line.startswith('PieceSize'):
            PIECE_SIZE = int(line.split(' ')[1].strip())
            print(f"PieceSize: {PIECE_SIZE}")

with open('PeerInfo.cfg', 'r') as file: # peerinfo is like a tracker equivalent in BitTorrent
    peer_info = {}
    for line in file:
        parts = line.split(' ')
        peer_id = int(parts[0].strip())
        host_name = parts[1].strip()
        port_number = int(parts[2].strip())
        has_file = parts[3].strip() == '1'
        peer_info[peer_id] = (host_name, port_number, has_file)

    #how to access: peer_info[1001][0]

#need a main or header file and src file but here is a couple functions

def peerProess(int): #int the peer process id
    # Initialize peer process
    if peerID not in peer_info:
        print(f"Peer ID {peerID} not found in PeerInfo.cfg")
        sys.exit(1)

    host_name, port_number, has_file = peer_info[peerID]
    print(f"Starting peer {peerID} at {host_name}:{port_number}, Has file: {has_file}")

    # Create a socket for the peer
    try:
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.bind((host_name, port_number))
        peer_socket.listen(5)
        print(f"Peer {peerID} listening on {host_name}:{port_number}")
    except Exception as e:
        print(f"Error creating socket for peer {peerID}: {e}")
        sys.exit(1)

    # Further implementation would go here (e.g., handling connections, file pieces, etc.)
