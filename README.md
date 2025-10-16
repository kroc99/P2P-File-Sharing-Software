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
