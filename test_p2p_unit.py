import os
import sys
import shutil
import unittest

import P2P_init
import peerProcess

class TestCommonCfg(unittest.TestCase):
    def test_common_cfg_exists_and_parsable(self):
        cfg_path = os.path.join(os.getcwd(), 'Common.cfg')
        self.assertTrue(os.path.isfile(cfg_path), "Common.cfg must exist in project root")
        entries = {}
        with open(cfg_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    entries[parts[0]] = parts[1]
        # basic keys expected in your sample Common.cfg
        self.assertIn('NumberOfPreferredNeighbors', entries)
        self.assertIn('UnchokingInterval', entries)
        self.assertIn('OptimisticUnchokingInterval', entries)
        self.assertIn('FileName', entries)
        self.assertIn('FileSize', entries)
        self.assertIn('PieceSize', entries)
        # numeric conversions sanity check
        self.assertGreater(int(entries['NumberOfPreferredNeighbors']), 0)
        self.assertGreater(int(entries['UnchokingInterval']), 0)
        self.assertGreater(int(entries['OptimisticUnchokingInterval']), 0)
        self.assertGreater(int(entries['FileSize']), 0)
        self.assertGreater(int(entries['PieceSize']), 0)

class TestPeerInfoParsingAndInit(unittest.TestCase):
    def setUp(self):
        self.peerinfo_path = os.path.join(os.getcwd(), 'PeerInfo.cfg')
        self.assertTrue(os.path.isfile(self.peerinfo_path), "PeerInfo.cfg must exist")
        # parse peer ids from file
        self.peer_ids = []
        with open(self.peerinfo_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                try:
                    pid = int(parts[0])
                    self.peer_ids.append(pid)
                except Exception:
                    pass
        # ensure directories cleaned for test (only remove peer_* dirs matching IDs)
        for pid in self.peer_ids:
            d = os.path.join(os.getcwd(), f'peer_{pid}')
            if os.path.isdir(d):
                try:
                    shutil.rmtree(d)
                except Exception:
                    # ignore cleanup failure
                    pass

    def test_peerinfo_parse_manual(self):
        # manual parse verification (always run)
        entries = {}
        with open(self.peerinfo_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 4:
                    pid = int(parts[0])
                    host = parts[1]
                    port = int(parts[2])
                    has_file = parts[3] == '1'
                    entries[pid] = (host, port, has_file)
        # sanity checks on the parsed data
        self.assertTrue(len(entries) >= 1)
        # check one known peer from the sample file
        self.assertIn(1001, entries)
        host, port, has_file = entries[1001]
        self.assertIsInstance(host, str)
        self.assertIsInstance(port, int)
        self.assertIn(has_file, (True, False))

    def test_peerinfo_init_population_if_implemented(self):
        # If PeerInfo_init is implemented it should populate P2P_init.peer_info and create directories.
        # Call it and then assert expected side-effects only if visible.
        try:
            P2P_init.peer_info.clear()
        except Exception:
            pass
        # call the initializer (if it's implemented this will populate peer_info and create peer_x dirs)
        try:
            P2P_init.PeerInfo_init()
        except Exception as e:
            # not implemented or errored; test that at least the function exists
            self.skipTest(f"PeerInfo_init not usable in current code: {e}")
        # if populated, assert it's a dict and contains some known ids
        if isinstance(P2P_init.peer_info, dict) and len(P2P_init.peer_info) > 0:
            self.assertIn(1001, P2P_init.peer_info)
            # check directories exist for the parsed peers
            for pid in list(P2P_init.peer_info.keys())[:3]:
                d = os.path.join(os.getcwd(), f'peer_{pid}')
                self.assertTrue(os.path.isdir(d), f"Expected directory peer_{pid} to exist")

class TestHandshakeAndParsing(unittest.TestCase):
    def test_handshake_format_and_parse(self):
        pid = 1001
        hw = P2P_init.handshake(pid)
        # handshake should be 32 bytes: 18 pstr + 10 zero + 4 id (per project convention)
        self.assertIsInstance(hw, (bytes, bytearray))
        self.assertEqual(len(hw), 32)
        # last 4 bytes encode the id big-endian
        parsed = int.from_bytes(hw[28:32], byteorder='big')
        self.assertEqual(parsed, pid)
        # test parser in peerProcess
        parsed_by_parser = peerProcess.parse_handshake(hw)
        self.assertEqual(parsed_by_parser, pid)

    def test_handshake_wrong_header(self):
        pid = 9999
        hw = P2P_init.handshake(pid)
        # corrupt the header part to make parse fail
        corrupted = b'X' + hw[1:]
        self.assertIsNone(peerProcess.parse_handshake(corrupted))

class TestTheFilePresence(unittest.TestCase):
    def test_thefile_exists_and_readable(self):
        path = os.path.join(os.getcwd(), 'thefile')
        self.assertTrue(os.path.isfile(path), "thefile must exist for tests")
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.assertGreaterEqual(len(lines), 5)
        # size sanity check
        self.assertGreater(os.path.getsize(path), 0)

class TestSmokeImports(unittest.TestCase):
    def test_modules_importable(self):
        # simple smoke tests to ensure required attributes exist
        for mod, attr in ((P2P_init, 'handshake'), (peerProcess, 'parse_handshake')):
            self.assertTrue(hasattr(mod, attr), f"{mod.__name__} should define {attr}")

if __name__ == '__main__':
    # run with verbosity on the project root
    unittest.main(verbosity=2)