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
    init_Common, handshake, PeerInfo_init, peer_info
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

# Global variables (local helpers only)
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

    # DONE def has_interesting_pieces(self, other_bitfield):
    def has_interesting_pieces(self, other_bitfield):
        """True if neighbor has pieces we don't have."""
        for i in range(self.num_pieces):
            if other_bitfield.bits[i] and not self.bits[i]:
                return True
        return False

    # DONE def get_missing_pieces(self, other_bitfield):
    def get_missing_pieces(self, other_bitfield):
        """Return a list of indices that neighbor has and we don't."""
        missing = []
        for i in range(self.num_pieces):
            if other_bitfield.bits[i] and not self.bits[i]:
                missing.append(i)
        return missing

class Peer:

    def __init__(self, peer_id):
        self.peer_id = peer_id

        if peer_id not in peer_info:
            print(f"Peer ID {peer_id} not found in PeerInfo.cfg")
            sys.exit(1)

        # Load peer info
        self.host_name, self.port_number, self.has_file = peer_info[peer_id]

        # Bitfield
        self.bitfield = Bitfield(P2P_init.NUM_PIECES, self.has_file)

        # Dictionary of peerID -> neighbor_state
        # neighbor_state = {
        #   'socket': socket,
        #   'bitfield': Bitfield(...),
        #   'am_choking': bool,
        #   'peer_choking_me': bool,
        #   'interested_in_me': bool,
        #   'im_interested_in_them': bool,
        #   'downloaded_bytes_interval': int
        # }
        # Neighbors
        self.connections = {}
        self.preferred_neighbors = set()
        self.optimistic_neighbor = None

        # LOG FILE MUST BE INITIALIZED BEFORE ANYTHING CALLS self.log()
        self.log_file = f"log_peer_{peer_id}.log"
        open(self.log_file, "w").close()   # clear file NOW

        self.log("Peer process started")
        self.log(f"Host={self.host_name} Port={self.port_number} HasFile={self.has_file}")

        # File path
        self.file_path = os.path.join(f"peer_{peer_id}", P2P_init.FILE_NAME)

        # THIS MUST COME AFTER log_file SETUP
        self._init_file_storage()

    def _init_file_storage(self):
        """
        Ensure the peer's file exists in its directory.
        If has_file == True, we assume the complete file already exists.
        If has_file == False, create an empty file of the correct size.
        """
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        if self.has_file:
            # We assume the full file is already there
            if not os.path.exists(self.file_path):
                self.log(f"WARNING: expected full file at {self.file_path} but not found.")
        else:
            # Create an empty file of FILE_SIZE bytes if not exists
            if not os.path.exists(self.file_path):
                with open(self.file_path, "wb") as f:
                    if P2P_init.FILE_SIZE > 0:
                        f.seek(P2P_init.FILE_SIZE - 1)
                        f.write(b'\0')

    def log(self, message):
        """Write log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")  # fixed getting only the time
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}]: {message}\n")
        print(f"[{timestamp}]: {message}")  # makes the time stamp show in console as well

    def recv_exact(self, sock, num_bytes):
        """Receive exactly num_bytes from the socket."""
        data = b''
        while len(data) < num_bytes:
            chunk = sock.recv(num_bytes - len(data))
            if not chunk:
                raise ConnectionError("Socket closed unexpectedly")
            data += chunk
        return data

    # -------------------------
    # Server side
    # -------------------------
    def start_server(self):
        """Start listening for incoming connections"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host_name, self.port_number))
        server_socket.listen()

        self.log(f"Peer {self.peer_id} listening on {self.host_name}:{self.port_number}")
        return server_socket

    def handle_incoming_connections(self, server_socket):
        """
        Accept incoming connections in a loop, perform handshake,
        create neighbor state, then spawn message handler threads.
        """
        while True:
            client_socket, addr = server_socket.accept()


            # Receive handshake first
            hs = self.recv_exact(client_socket, 32)
            remote_id = parse_handshake(hs)
            if remote_id is None:
                self.log(f"Received invalid handshake from {addr}, closing.")
                client_socket.close()
                continue

            # Log "is connected from"
            self.log(f"Peer {self.peer_id} is connected from Peer {remote_id}.")

            # Send our handshake back
            client_socket.sendall(handshake(self.peer_id))

            # Create neighbor state
            neighbor_state = {
                'socket': client_socket,
                'bitfield': Bitfield(P2P_init.NUM_PIECES, False),
                'am_choking': True,
                'peer_choking_me': True,
                'interested_in_me': False,
                'im_interested_in_them': False,
                'downloaded_bytes_interval': 0
            }
            self.connections[remote_id] = neighbor_state

            # After handshake, send our bitfield
            bf_msg = create_bitfield(self.bitfield.to_bytes())
            client_socket.sendall(bf_msg)

            # Start a thread to handle messages from this neighbor
            t = threading.Thread(
                target=self.handle_peer_connection,
                args=(client_socket, remote_id),
                daemon=True
            )
            t.start()

    # -------------------------
    # Peer connection + message handling
    # -------------------------
    def handle_peer_connection(self, client_socket, peer_id):
        """
        Handle messages from a single peer in a loop.
        """
        try:
            self.handle_peer_messages(client_socket, peer_id)
        except ConnectionError:
            self.log(f"Connection to Peer {peer_id} closed.")
        except Exception as e:
            self.log(f"Error in connection with Peer {peer_id}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass

    def handle_peer_messages(self, client_socket, peer_id):
        """
        Continuously read messages: length (4 bytes) + type (1 byte) + payload.
        """
        while True:
            # Read length (payload length, not including type)
            header = self.recv_exact(client_socket, 4)
            length = struct.unpack('>I', header)[0]

            # Read type
            type_byte = self.recv_exact(client_socket, 1)
            message_type = type_byte[0]

            # Read payload
            payload = b''
            if length > 0:
                payload = self.recv_exact(client_socket, length)

            self.process_message(message_type, payload, peer_id, client_socket)

    def process_message(self, message_type, payload, peer_id, client_socket):
        """
        Process incoming messages from a neighbor.
        Handles: bitfield, have, interested, not interested, choke, unchoke, request, piece.
        """
        neighbor = self.connections.get(peer_id)
        if neighbor is None:
            # Should not happen
            return

        if message_type == BITFIELD:
            # Neighbor's initial bitfield
            neighbor['bitfield'].from_bytes(payload)
            # Decide if we are interested
            if self.bitfield.has_interesting_pieces(neighbor['bitfield']):
                client_socket.sendall(create_interested())
                neighbor['im_interested_in_them'] = True
            else:
                client_socket.sendall(create_not_interested())
                neighbor['im_interested_in_them'] = False

        elif message_type == HAVE:
            # Neighbor just got one new piece
            piece_index = struct.unpack('>I', payload)[0]
            neighbor['bitfield'].set_piece(piece_index)
            self.log(f"Peer {self.peer_id} received the 'have' message from {peer_id} for the piece {piece_index}.")
            # Decide if this makes us interested now
            if self.bitfield.has_interesting_pieces(neighbor['bitfield']) and not neighbor['im_interested_in_them']:
                client_socket.sendall(create_interested())
                neighbor['im_interested_in_them'] = True

        elif message_type == INTERESTED:
            neighbor['interested_in_me'] = True
            self.log(f"Peer {self.peer_id} received the 'interested' message from {peer_id}.")

        elif message_type == NOT_INTERESTED:
            neighbor['interested_in_me'] = False
            self.log(f"Peer {self.peer_id} received the 'not interested' message from {peer_id}.")

        elif message_type == CHOKE:
            neighbor['peer_choking_me'] = True
            self.log(f"Peer {self.peer_id} is choked by {peer_id}.")

        elif message_type == UNCHOKE:
            neighbor['peer_choking_me'] = False
            self.log(f"Peer {self.peer_id} is unchoked by {peer_id}.")
            # Once unchoked, send a request
            self.send_request(peer_id, client_socket)

        elif message_type == REQUEST:
            # Neighbor requests a piece from us
            piece_index = struct.unpack('>I', payload)[0]
            piece_data = self.read_piece(piece_index)
            if piece_data is not None:
                msg = create_piece(piece_index, piece_data)
                client_socket.sendall(msg)
            # If we don't have it, ignore (should not happen if bitfields are correct)

        elif message_type == PIECE:
            # We got a piece from neighbor
            piece_index = struct.unpack('>I', payload[:4])[0]
            piece_data = payload[4:]
            self.save_piece(piece_index, piece_data, peer_id)

            # Track download rate
            neighbor['downloaded_bytes_interval'] += len(piece_data)

            # If neighbor still has interesting pieces and we are not choked, request another
            if not neighbor['peer_choking_me'] and self.bitfield.has_interesting_pieces(neighbor['bitfield']):
                self.send_request(peer_id, client_socket)
            else:
                # Might send not interested if nothing left
                if not self.bitfield.has_interesting_pieces(neighbor['bitfield']):
                    client_socket.sendall(create_not_interested())
                    neighbor['im_interested_in_them'] = False

        else:
            # Unknown/unused message type
            pass

    def send_request(self, peer_id, client_socket):
        """
        Send a 'request' message for a piece that:
        - we don't have
        - the neighbor (peer_id) does have
        """
        neighbor = self.connections.get(peer_id)
        if neighbor is None:
            return

        # Find missing pieces that neighbor has
        missing = self.bitfield.get_missing_pieces(neighbor['bitfield'])
        if not missing:
            # Nothing to request, send not interested
            client_socket.sendall(create_not_interested())
            neighbor['im_interested_in_them'] = False
            return

        piece_index = random.choice(missing)
        msg = create_request(piece_index)
        client_socket.sendall(msg)
        self.log(f"Peer {self.peer_id} sent 'request' message to {peer_id} for piece {piece_index}.")

    def read_piece(self, piece_index):
        """
        Read a piece from our local file.
        Returns bytes or None on error.
        """
        try:
            with open(self.file_path, "rb") as f:
                offset = piece_index * P2P_init.PIECE_SIZE
                f.seek(offset)
                # Last piece may be shorter
                max_len = min(P2P_init.PIECE_SIZE, P2P_init.FILE_SIZE - offset)
                if max_len <= 0:
                    return None
                data = f.read(max_len)
                return data
        except Exception as e:
            self.log(f"Error reading piece {piece_index}: {e}")
            return None

    def save_piece(self, piece_index, piece_data, from_peer_id):
        """
        Save a downloaded piece to our local file, update bitfield,
        log download, and send 'have' to neighbors.
        """
        try:
            with open(self.file_path, "r+b") as f:
                offset = piece_index * P2P_init.PIECE_SIZE
                f.seek(offset)
                f.write(piece_data)

            # Update bitfield
            if not self.bitfield.has_piece(piece_index):
                self.bitfield.set_piece(piece_index)

            # Count how many pieces we now have
            pieces_have = sum(1 for b in self.bitfield.bits if b)

            # Log download
            self.log(f"Peer {self.peer_id} has downloaded the piece {piece_index} from {from_peer_id}. "
                     f"Now the number of pieces it has is {pieces_have}.")

            # Send 'have' to all neighbors
            have_msg = create_have(piece_index)
            for nb_id, nb_state in self.connections.items():
                try:
                    nb_state['socket'].sendall(have_msg)
                except:
                    pass

            # If file complete, log completion (and later: terminate)
            if self.bitfield.is_complete():
                self.log(f"Peer {self.peer_id} has downloaded the complete file.")

        except Exception as e:
            self.log(f"Error saving piece {piece_index}: {e}")

    def connect_to_peers(self):
        """
        Initial connections at startup:
        Each peer connects to all peers listed before it in PeerInfo.cfg.
        """
        peer_ids_sorted = sorted(P2P_init.peer_info.keys())
        my_index = peer_ids_sorted.index(self.peer_id)
        older_peers = peer_ids_sorted[:my_index]

        for other_id in older_peers:
            host, port, _ = P2P_init.peer_info[other_id]
            print(port)
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, port))
                # Send handshake
                
                sock.sendall(handshake(self.peer_id))

                # Receive handshake back
                hs = self.recv_exact(sock, 32)
                returned_id = parse_handshake(hs)

                # Log "makes a connection"
                self.log(f"Peer {self.peer_id} makes a connection to Peer {returned_id}.")

                # Neighbor state
                neighbor_state = {
                    'socket': sock,
                    'bitfield': Bitfield(P2P_init.NUM_PIECES, False),
                    'am_choking': True,
                    'peer_choking_me': True,
                    'interested_in_me': False,
                    'im_interested_in_them': False,
                    'downloaded_bytes_interval': 0
                }
                self.connections[returned_id] = neighbor_state

                # Send our bitfield
                bf_msg = create_bitfield(self.bitfield.to_bytes())
                sock.sendall(bf_msg)

                # Start message handling thread
                t = threading.Thread(
                    target=self.handle_peer_connection,
                    args=(sock, returned_id),
                    daemon=True
                )
                t.start()

            except Exception as e:
                self.log(f"Error connecting to Peer {other_id}: {e}")

    def start_choking_algorithm(self):
        """
        Start background threads for:
        - updating preferred neighbors every UnchokingInterval seconds
        - updating optimistic unchoked neighbor every OptimisticUnchokingInterval seconds
        """
        t1 = threading.Thread(
            target=self._preferred_neighbors_loop,
            daemon=True
        )
        t2 = threading.Thread(
            target=self._optimistic_unchoke_loop,
            daemon=True
        )
        t1.start()
        t2.start()

    def _preferred_neighbors_loop(self):
        while True:
            time.sleep(P2P_init.UNCHOKING_INTERVAL)
            self.update_preferred_neighbors()

    def _optimistic_unchoke_loop(self):
        while True:
            time.sleep(P2P_init.OPTIMISTIC_UNCHOKING_INTERVAL)
            self.update_optimistic_neighbor()

    def update_preferred_neighbors(self):
        """
        Every p seconds, select k preferred neighbors.
        If we have complete file: pick randomly among interested neighbors.
        Otherwise: pick top k by download rate.
        """
        # Collect interested neighbors
        interested_neighbors = [
            (pid, state) for pid, state in self.connections.items()
            if state['interested_in_me']
        ]

        if not interested_neighbors:
            return

        if self.bitfield.is_complete():
            # Choose k randomly among interested
            random.shuffle(interested_neighbors)
            selected = [pid for pid, _ in interested_neighbors[:P2P_init.NUMBER_OF_PREFERRED_NEIGHBORS]]
        else:
            # Sort by downloaded_bytes_interval descending
            interested_neighbors.sort(
                key=lambda item: item[1]['downloaded_bytes_interval'],
                reverse=True
            )
            selected = [pid for pid, _ in interested_neighbors[:P2P_init.NUMBER_OF_PREFERRED_NEIGHBORS]]

        self.preferred_neighbors = set(selected)

        # Log preferred neighbors list
        if self.preferred_neighbors:
            neighbors_str = ",".join(str(pid) for pid in sorted(self.preferred_neighbors))
        else:
            neighbors_str = ""
        self.log(f"Peer {self.peer_id} has the preferred neighbors {neighbors_str}.")

        # Unchoke new preferred neighbors
        for pid in self.preferred_neighbors:
            if pid in self.connections:
                state = self.connections[pid]
                if state['am_choking'] and pid != self.optimistic_neighbor:
                    try:
                        state['socket'].sendall(create_unchoke())
                        state['am_choking'] = False
                    except:
                        pass

        # Choke neighbors that are no longer preferred and not optimistic neighbor
        for pid, state in self.connections.items():
            if pid not in self.preferred_neighbors and pid != self.optimistic_neighbor:
                if not state['am_choking']:
                    try:
                        state['socket'].sendall(create_choke())
                        state['am_choking'] = True
                    except:
                        pass

        # Reset download interval counters
        for _, state in self.connections.items():
            state['downloaded_bytes_interval'] = 0

    def update_optimistic_neighbor(self):
        """
        Every m seconds, randomly select one interested but choked neighbor as the optimistic
        unchoked neighbor.
        """
        # candidates: interested in me, currently choked by me, not already preferred
        candidates = [
            pid for pid, state in self.connections.items()
            if state['interested_in_me'] and state['am_choking'] and pid not in self.preferred_neighbors
        ]

        if not candidates:
            return

        new_opt = random.choice(candidates)
        self.optimistic_neighbor = new_opt

        # Unchoke this neighbor
        state = self.connections[new_opt]
        try:
            state['socket'].sendall(create_unchoke())
            state['am_choking'] = False
        except:
            pass

        # Log optimistic neighbor
        self.log(f"Peer {self.peer_id} has the optimistically unchoked neighbor {new_opt}.")


def peerProcess(peer_id):
    """Main peer process function"""

    # Read configuration directly from Common.cfg
    init_Common()
    

    # Read peer info directly from PeerInfo.cfg
    PeerInfo_init()  # use the function from the P2P file

    # Create peer instance
    peer = Peer(peer_id)

    # Start server
    server_socket = peer.start_server()

    # Start thread to handle incoming connections
    t_accept = threading.Thread(
        target=peer.handle_incoming_connections,
        args=(server_socket,),
        daemon=True
    )
    t_accept.start()

    # Connect to older peers
    peer.connect_to_peers()

    # Start choking/unchoking algorithms
    peer.start_choking_algorithm()

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        peer.log("Peer process terminated")
        server_socket.close()
        for _, state in peer.connections.items():
            try:
                state['socket'].close()
            except:
                pass


if __name__ == "__main__":
    if len(sys.argv) != 2:  # making sure that the command includes exactly the information needed.
        print("Usage: python peerProcess.py <peer_id>")
        sys.exit(1)

    peer_id = int(sys.argv[1])  # reads in the peer id
    peerProcess(peer_id)
    # handshake(peer_id) dont think we need this here - implemented in peer_process
