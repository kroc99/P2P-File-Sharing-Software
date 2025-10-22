#!/usr/bin/env python3
"""
P2P File Sharing Implementation - Core Functions
This file extends the existing P2P_init.py with essential functionality
"""

import math
import random
import socket
import os
import sys
import threading
import time
import struct
from datetime import datetime
import P2P_init

from P2P_init import (
    init_Common, handshake, actual_mes, PeerInfo_init
)

# Message type constants
CHOKE = 0
UNCHOKE = 1
INTERESTED = 2
NOT_INTERESTED = 3
HAVE = 4
BITFIELD = 5
REQUEST = 6
PIECE = 7

# Global variables
peer_info = {}
NUM_PIECES = 0

# Configuration variables (will be set by init_Common)
NUMBER_OF_PREFERRED_NEIGHBORS = 0
UNCHOKING_INTERVAL = 0
OPTIMISTIC_UNCHOKING_INTERVAL = 0
FILE_NAME = ""
FILE_SIZE = 0
PIECE_SIZE = 0

# need to call the handshake initiatlizer in the P2P file
# plan on using the actual mes function from P2P as well 
def calculate_num_pieces():
    """Calculate number of pieces based on file size and piece size"""
    global NUM_PIECES, FILE_SIZE, PIECE_SIZE
    NUM_PIECES = math.ceil(FILE_SIZE / PIECE_SIZE)
    return NUM_PIECES

def create_message(message_type, payload=b''):
    """Create a message with length prefix"""
    length = len(payload)
    return struct.pack('>IB', length, message_type) + payload

def create_choke():
    return create_message(CHOKE)

def create_unchoke():
    return create_message(UNCHOKE)

def create_interested():
    return create_message(INTERESTED)

def create_not_interested():
    return create_message(NOT_INTERESTED)

def create_have(piece_index):
    payload = struct.pack('>I', piece_index)
    return create_message(HAVE, payload)

def create_bitfield(bitfield_bytes):
    return create_message(BITFIELD, bitfield_bytes)

def create_request(piece_index):
    payload = struct.pack('>I', piece_index)
    return create_message(REQUEST, payload)

def create_piece(piece_index, piece_data):
    payload = struct.pack('>I', piece_index) + piece_data
    return create_message(PIECE, payload)

def parse_message(data):
    """Parse message and return (message_type, payload)"""
    if len(data) < 5:
        return None, None
    
    length = struct.unpack('>I', data[:4])[0]
    message_type = data[4]
    payload = data[5:5+length] if length > 0 else b''
    
    return message_type, payload

def parse_handshake(data):
    """Parse handshake message and return peer_id"""
    if len(data) != 32:
        return None
    
    pstr = data[:18].decode('utf-8')
    if pstr != "P2PFILESHARINGPROJ":
        return None
    
    peer_id = int.from_bytes(data[28:32], byteorder='big')
    return peer_id

# TODO: Implement remaining message creation functions
# def create_not_interested():
# def create_have(piece_index):
# def create_bitfield(bitfield_bytes):
# def create_request(piece_index):
# def create_piece(piece_index, piece_data):

class Bitfield:
    def __init__(self, num_pieces, has_file=False):
        self.num_pieces = num_pieces
        self.num_bytes = math.ceil(num_pieces / 8)
        if has_file:
            self.bits = [True] * num_pieces
        else:
            self.bits = [False] * num_pieces
    
    def set_piece(self, piece_index):
        if 0 <= piece_index < self.num_pieces:
            self.bits[piece_index] = True
    
    def has_piece(self, piece_index):
        if 0 <= piece_index < self.num_pieces:
            return self.bits[piece_index]
        return False
    
    def to_bytes(self):
        byte_array = bytearray(self.num_bytes)
        for i in range(self.num_pieces):
            if self.bits[i]:
                byte_index = i // 8
                bit_index = 7 - (i % 8)
                byte_array[byte_index] |= (1 << bit_index)
        return bytes(byte_array)
    
    def from_bytes(self, data):
        for i in range(self.num_pieces):
            byte_index = i // 8
            bit_index = 7 - (i % 8)
            if byte_index < len(data):
                self.bits[i] = bool(data[byte_index] & (1 << bit_index))
    
    def is_complete(self):
        return all(self.bits) 

# TODO: Implement remaining Bitfield methods
# def has_interesting_pieces(self, other_bitfield):
# def get_missing_pieces(self, other_bitfield):

class Peer:
    def __init__(self, peer_id):
        self.peer_id = peer_id
        #print(peer_info[peer_id])
        self.host_name, self.port_number, self.has_file = P2P_init.peer_info[peer_id]
        self.bitfield = Bitfield(NUM_PIECES, self.has_file)
        self.connections = {}  # Active connections
        
        # Initialize log file 
        self.log_file = f"log_peer_{peer_id}.log"
        self.log("Peer process started")
        
        # Create peer directory
        os.makedirs(f'peer_{peer_id}', exist_ok=True)
    
    def log(self, message):
        """Write log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}]: {message}\n")
        print(f"[{timestamp}]: {message}") #makes the time stamp show in console as well
    
    def start_server(self):
        """Start listening for incoming connections"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host_name, self.port_number))
        server_socket.listen(10)
        
        self.log(f"Peer {self.peer_id} listening on {self.host_name}:{self.port_number}")
        return server_socket

# TODO: Implement remaining Peer methods
# def handle_incoming_connections(self, server_socket):
# def handle_peer_connection(self, client_socket):
# def handle_peer_messages(self, client_socket, peer_id):
# def process_message(self, message_type, payload, peer_id, client_socket):
# def send_request(self, peer_id, client_socket):
# def read_piece(self, piece_index):
# def save_piece(self, piece_index, piece_data):
# def connect_to_peers(self):
# def start_choking_algorithm(self):
# def update_preferred_neighbors(self):
# def update_optimistic_neighbor(self):

def peerProcess(peer_id):
    """Main peer process function"""
    global peer_info, NUMBER_OF_PREFERRED_NEIGHBORS, UNCHOKING_INTERVAL
    global OPTIMISTIC_UNCHOKING_INTERVAL, FILE_NAME, FILE_SIZE, PIECE_SIZE
    
    # Read configuration directly from Common.cfg
    # with open('Common.cfg', 'r') as file:
    #     for line in file:
    #         if line.startswith('NumberOfPreferredNeighbors'):
    #             NUMBER_OF_PREFERRED_NEIGHBORS = int(line.split(' ')[1].strip())
    #         elif line.startswith('UnchokingInterval'):
    #             UNCHOKING_INTERVAL = int(line.split(' ')[1].strip())
    #         elif line.startswith('OptimisticUnchokingInterval'):
    #             OPTIMISTIC_UNCHOKING_INTERVAL = int(line.split(' ')[1].strip())
    #         elif line.startswith('FileName'):  
    #             FILE_NAME = line.split(' ')[1].strip()
    #         elif line.startswith('FileSize'):
    #             FILE_SIZE = int(line.split(' ')[1].strip())
    #         elif line.startswith('PieceSize'):
    #             PIECE_SIZE = int(line.split(' ')[1].strip())
    init_Common()
    # Read peer info directly from PeerInfo.cfg
    peer_info.clear()  # Clear any old data


    PeerInfo_init() # use the function from the P2P file
    # Calculate number of pieces
    #calculate_num_pieces()
    
    # Create peer instance
    peer = Peer(peer_id)
    
    # Start server
    server_socket = peer.start_server()
    
    # TODO: Implement remaining functionality
    # peer.connect_to_peers()
    # peer.start_choking_algorithm()???
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        peer.log("Peer process terminated")
        server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 2: #making sure that the command includes exactly the information needed. 
        print("Usage: python peerProcess.py <peer_id>")
        sys.exit(1)
    
    peer_id = int(sys.argv[1])
    peerProcess(peer_id)
