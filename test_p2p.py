#!/usr/bin/env python3
"""
Test script for P2P File Sharing System
This script helps test the peer-to-peer file sharing implementation
"""

import subprocess
import time
import os
import sys

def create_test_file():
    """Create a test file for sharing"""
    test_content = """This is a test file for the P2P file sharing system.
It contains multiple lines of text to test the file sharing functionality.
Each peer will download pieces of this file from other peers.
This tests the choking/unchoking mechanism, piece exchange, and overall P2P functionality.
The file should be distributed among peers using the BitTorrent-like protocol.
Each peer will download pieces of this file from other peers until they have the complete file.
This is line 8 of the test file.
This is line 9 of the test file.
This is line 10 of the test file.
This is line 11 of the test file.
This is line 12 of the test file.
This is line 13 of the test file.
This is line 14 of the test file.
This is line 15 of the test file.
This is line 16 of the test file.
This is line 17 of the test file.
This is line 18 of the test file.
This is line 19 of the test file.
This is line 20 of the test file.
This is line 21 of the test file.
This is line 22 of the test file.
This is line 23 of the test file.
This is line 24 of the test file.
This is line 25 of the test file.
This is line 26 of the test file.
This is line 27 of the test file.
This is line 28 of the test file.
This is line 29 of the test file.
This is line 30 of the test file.
This is line 31 of the test file.
This is line 32 of the test file.
This is line 33 of the test file.
This is line 34 of the test file.
This is line 35 of the test file.
This is line 36 of the test file.
This is line 37 of the test file.
This is line 38 of the test file.
This is line 39 of the test file.
This is line 40 of the test file.
This is line 41 of the test file.
This is line 42 of the test file.
This is line 43 of the test file.
This is line 44 of the test file.
This is line 45 of the test file.
This is line 46 of the test file.
This is line 47 of the test file.
This is line 48 of the test file.
This is line 49 of the test file.
This is line 50 of the test file.
This is line 51 of the test file.
This is line 52 of the test file.
This is line 53 of the test file.
This is line 54 of the test file.
This is line 55 of the test file.
This is line 56 of the test file.
This is line 57 of the test file.
This is line 58 of the test file.
This is line 59 of the test file.
This is line 60 of the test file.
This is line 61 of the test file.
This is line 62 of the test file.
This is line 63 of the test file.
This is line 64 of the test file.
This is line 65 of the test file.
This is line 66 of the test file.
This is line 67 of the test file.
This is line 68 of the test file.
This is line 69 of the test file.
This is line 70 of the test file.
This is line 71 of the test file.
This is line 72 of the test file.
This is line 73 of the test file.
This is line 74 of the test file.
This is line 75 of the test file.
This is line 76 of the test file.
This is line 77 of the test file.
This is line 78 of the test file.
This is line 79 of the test file.
This is line 80 of the test file.
This is line 81 of the test file.
This is line 82 of the test file.
This is line 83 of the test file.
This is line 84 of the test file.
This is line 85 of the test file.
This is line 86 of the test file.
This is line 87 of the test file.
This is line 88 of the test file.
This is line 89 of the test file.
This is line 90 of the test file.
This is line 91 of the test file.
This is line 92 of the test file.
This is line 93 of the test file.
This is line 94 of the test file.
This is line 95 of the test file.
This is line 96 of the test file.
This is line 97 of the test file.
This is line 98 of the test file.
This is line 99 of the test file.
This is line 100 of the test file.
"""
    
    with open('thefile', 'w') as f:
        f.write(test_content)
    
    print(f"Created test file 'thefile' with {len(test_content)} bytes")

def start_peer(peer_id):
    """Start a peer process"""
    try:
        process = subprocess.Popen([sys.executable, 'peerProcess.py', str(peer_id)])
        print(f"Started peer {peer_id} with PID {process.pid}")
        return process
    except Exception as e:
        print(f"Failed to start peer {peer_id}: {e}")
        return None

def main():
    """Main test function"""
    print("P2P File Sharing Test Script")
    print("=" * 40)
    
    # Create test file
    create_test_file()
    
    # Start peers
    print("\nStarting peers...")
    processes = []
    
    # Start peers in order (as specified in PeerInfo.cfg)
    peer_ids = [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009]
    
    for peer_id in peer_ids:
        process = start_peer(peer_id)
        if process:
            processes.append((peer_id, process))
        time.sleep(2)  # Wait between starting peers
    
    print(f"\nStarted {len(processes)} peer processes")
    print("Peers are now running. Check the log files for activity.")
    print("Press Ctrl+C to stop all peers.")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all peers...")
        for peer_id, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"Stopped peer {peer_id}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"Force killed peer {peer_id}")
            except Exception as e:
                print(f"Error stopping peer {peer_id}: {e}")
        
        print("All peers stopped.")

if __name__ == "__main__":
    main()
