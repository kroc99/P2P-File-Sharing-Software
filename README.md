# P2P-File-Sharing-Software
Similar to BitTorrent

For this project we worked collaboratively on creating a peer to peer file sharing system dedicated to sharing a file within certain peers and preferred neighbors. This is done with simmilar functions and types as BitTorrent like choke, unchoke, interested, not interested, have, and request. We have all of the messages saved within a log file for all the peers that gets created upon the opening of the socket and have printed out a few checks in our terminal to verify variable updates and bitfield translations.

We tested in the video on a personal hotspot as we ran into issue testing on uf servers. Where one computer was on IP address 172.20.10.4 and the other on 172.20.10.2. This ended up showing full peer to peer TCP connection and the process terminating after. 

You will notice that we printed out the common.cfg and PeerInfo.cfg variables inthe beginning alomg with the bitfield message in the terminal but it cannot be found in the log as these are things that normally not printed in the peer log. We do have messages in place that run after those functions have executed but not an explicit message.

We ran python peerProcess.py 1002 or other everytime and that is what started our connection. 

Github link: (we worked off the main branch as that should be the most up to date)

Group Members:

Savannah Ogletree, Kristian O'Connor, and Giovanni Sanchez

Contributions:

Savannah: Worked on the initial set up and worked on the planning of meetings and deadlines needed to be met. Worked on the README file and worked on the P2P_init.py file. After file implementation, she worked on debugging and meeting rubric criteria with logging statements. She also created the video and submitted the project ensuring full submission occured. 

Kristian: Worked on the initial class structures for Peer and Bitfield. He also fixed logging and test result bugs and helped in the creation of the test case code.

Giovanni: Worked on main functionality of a lot of the functions in Peer and remaining functions in Bitfield. He also worked on the creation of the test cases that we could run. In addition to that, he helped with logic understanding and functionality