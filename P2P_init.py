import math
import random
import socket
import os
import sys

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

#with open('PeerInfo.cfg', 'r') as file:
