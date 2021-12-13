import unittest
import networkx as nx
from algorithm import GenerateMap

class TestAlgorithm(unittest.TestCase):
    def setUp(self):
        self.mapGenerator = GenerateMap()
        self.map = GenerateMap().create_graph("Amherst, MA", "drive")
        self.source = 66672877
        self.dest = 66649487

    def tearDown(self):
        pass

    # Test for empty paths when finding elevation
    def test_empty_path_elevation(self):
        path = []
        self.assertEqual(self.mapGenerator.path_elevation(self.map, path), 0)

    # Test for correctness for path elevation
    def test_path_elevation(self):
        path = nx.shortest_path(self.map, self.source, self.dest)
        self.assertEqual(self.mapGenerator.path_elevation(self.map, path), 64.948)

    # Test for empty path length
    def test_empty_path_length(self):
        path = []
        self.assertEqual(self.mapGenerator.path_length(self.map, path), 0)

    # Test for correctness for path length
    def test_path_length(self):
        path = nx.shortest_path(self.map, self.source, self.dest)
        self.assertEqual(self.mapGenerator.path_length(self.map, path), 8244.960999999998)

    # Test for key error when given an invalid path
    def test_invalid_path(self):
        path = nx.shortest_path(self.map, self.source, self.dest)
        path.pop(1)
        self.assertRaises(KeyError, lambda: self.mapGenerator.path_length(self.map, path))

    # Test the algorithm for maximizing elevation
    def test_between_algorithm(self):
        default_path = nx.shortest_path(self.map, self.source, self.dest)
        def_elevation = self.mapGenerator.path_elevation(self.map, default_path)
        max_path = self.mapGenerator.between_algorithm(self.map, self.source, self.dest, .9)
        max_elevation = self.mapGenerator.path_elevation(self.map, max_path)
        self.assertGreater(max_elevation, def_elevation)

    # Test the algorithm for minimizing elevation
    def test_dijkstra_algorithm(self):
        default_path = nx.shortest_path(self.map, self.source, 66708760)
        def_elevation = self.mapGenerator.path_elevation(self.map, default_path)
        min_path = self.mapGenerator.dijkstra_algorithm(self.map, self.source, 66708760, False, .3)
        min_elevation = self.mapGenerator.path_elevation(self.map, min_path)
        self.assertLess(min_elevation, def_elevation)

    # Test that the maximizing algorithm falls below the max distance
    def test_valid_length_between(self):
        percent = .9
        max_dist = self.mapGenerator.path_length(self.map, nx.shortest_path(self.map, self.source, self.dest)) * (1 + percent)
        path = self.mapGenerator.between_algorithm(self.map, self.source, self.dest, percent)
        path_dist = self.mapGenerator.path_length(self.map, path)
        self.assertLess(path_dist, max_dist)

    # Test that the minimizing algorithm falls below the max distance
    def test_valid_length_dijkstra(self):
        percent = .9
        max_dist = self.mapGenerator.path_length(self.map, nx.shortest_path(self.map, self.source, self.dest)) * (1 + percent)
        path = self.mapGenerator.dijkstra_algorithm(self.map, self.source, self.dest, False, percent)
        path_dist = self.mapGenerator.path_length(self.map, path)
        self.assertLess(path_dist, max_dist)

if __name__ == '__main__':
    unittest.main()