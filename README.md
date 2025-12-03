# P2P-File-Sharing-Software
Similar to BitTorrent

First we need to implement a file reading code to read and store Common.cfg and PeerInfo.cfg

Then create a directory set up where if a peer starts up then it would 
- create its own subdirectory
- bitfield init
- and a splitter or loaded for the file

Then we need to log the system that would record events (not essential but could help)

Then creation of:
- Server socket - Similar to the Sample server.java - listens
- clilent socket - similar to the sample client.java - connects to all peers before it
- handhake protocol with the 3 parts
- 

To run the test_p2p file:
- type "python test_p2p.py" into the terminal inside the root folder
- use Ctrl+C to terminate process
- the testing file starts a log file for each peer to show the P2P relationship working

To run the test_p2p_unit file:
- type "python -m unittest test_p2p_unit.py -v" into the terminal inside the root folder

- test_common_cfg_exists_and_parsable
    * checks that Common.cfg exists
    * check that the right keys are parsed

- test_handshake_format_and_parse
    * builds handshake with P2P_init.handshake(pid) to encode peer id
    * passes the handshake to peerProcess.parse_handshake and expects the same id

- test_handshake_wrong_header
    * checks that parsing rejects a bad header

- test_peerinfo_init_population_if_implemented
    * calls P2P_init.PeerInfo_init() if available
    * then checks P2P_init.peer_info is populated

- test_peerinfo_parse_manual
    * parses PeerInfo.cfg to check if the proper extries exist in the right order
    * asserts at least one entry exists and that a known peer (1001) is present

- test_modules_importable
    * simple check to see if symbols exist: "P2P_init.handshake" and "peerProcess.parse_handshake"
    * fails if missing

- test_thefile_exists_and_readable
    * confirms "thefile" exists and is readable
    * checks that it contains at least 5 lines and file is not empty


!!!!!!!
Before final submission, you will need:

1️⃣ A stop condition

Peers currently run forever.
Add this inside save_piece():

if self.bitfield.is_complete():
    # Check all peers also complete before termination (per project spec).


But this can be added later.

2️⃣ A log that exactly matches project format

Your logs are extremely close — and acceptable.