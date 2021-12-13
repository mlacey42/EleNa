import math
import os
import re
from networkx.algorithms.shortest_paths.generic import shortest_path
from numpy import short
from numpy.lib.function_base import append
import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
from queue import PriorityQueue

locator = Nominatim(user_agent="test")


class GenerateMap:
    def __init__(self):
        pass

    def address_to_coords(self, address):
        """
        Returns latitude and longitude given an address

        Parameters:
            address(str): A valid address

        Returns:
            tuple: (longitude, latitude)
        """
        geocoded_address = locator.geocode(address)
        return (geocoded_address.longitude, geocoded_address.latitude)

    def coords(self, G, node):
        """
        Returns latitude and longitude given a node

        Parameters:
            G(MultiDiGraph): The graph of nodes
            node(node): A node on the map

        Returns:
            tuple: (longitude, latitude)
        """
        return (G.nodes[node]['x'], G.nodes[node]['y'])

    def neareast_node(self, G, coords):
        """
        Returns the nearest node to the given coordinates

        Parameters:
            G(MultiDiGraph): The graph of nodes
            coords(tuple): Tuple containing coordinates in the form (longitude, latitude)

        Returns:
            node: The closest node to coords in G
        """
        return ox.distance.nearest_nodes(G, coords[0], coords[1])

    def create_graph(self, location, network_type):
        """
        Creates a directed graph of nodes and edges for a given location
        Loads the graph from map cache if it already exists

        Parameters:
            location(str): A valid location in the form of city, state, country
            network_type(str): The type of map (drive, walk, bike, etc.)

        Returns:
            G(MultiDiGraph): The graph of nodes
        """
        filename = re.sub('[^A-Za-z0-9]+', '', location) + ".graphml"
        for root, dir, files in os.walk("./mapcache"):
            if filename in files:
                G = ox.io.load_graphml("./mapcache/{file}".format(file=filename), node_dtypes=None, edge_dtypes=None, graph_dtypes=None)
                return G
        G = ox.graph_from_place(location, network_type)
        G = ox.add_node_elevations_google(G, api_key='AIzaSyCtgkUV4Om2PaU5AHX0q8CuMcIn8UREaZY')
        G = ox.add_edge_grades(G)
        ox.io.save_graphml(G, "./mapcache/{file}".format(file=filename), gephi=False, encoding="utf-8")
        return G

    def path_length(self, G, path):
        """
        Finds the length of a path of nodes

        Parameters:
            G(MultiDiGraph): The graph of nodes
            path(list): A list of nodes comprising the path

        Returns:
            length(float): The total length of the path
        """
        length = 0
        if(len(path) <= 1):
            return length
        for x in range(0, len(path) - 1):
            length += G.edges[path[x], path[x + 1], 0]["length"]
        return length

    def node_elevation(self, G, curr, neighbor):
        """
        Finds the elevation gain between two nodes

        Parameters:
            G(MultiDiGraph): The graph of nodes
            curr(node): The current node
            neighbor(node): The next node

        Returns:
            float: elevation gain
        """
        elevation = G.nodes[neighbor]['elevation'] - G.nodes[curr]['elevation']
        if elevation < 0:
            return 0
        else:
            return elevation

    def path_elevation(self, G, path):
        """
        Finds the elevation gain of a path of nodes

        Parameters:
            G(MultiDiGraph): The graph of nodes
            path(list): A list of nodes comprising the path

        Returns:
            elevation(float): The total elevation of the path
        """
        elevation = 0
        if(len(path) <= 1):
            return elevation
        for x in range(0, len(path) - 1):
            temp = (G.nodes[path[x+1]]["elevation"] -
                    G.nodes[path[x]]["elevation"])
            if temp > 0:
                elevation = temp + elevation
        return elevation

    def euclidean(self, curr_coord, end_coord):
        """
        Finds euclidean dist between coords in meters using the Haversine formula

        Parameters:
            curr_coord(tuple): (latitude, longitude) of current node
            end_coord(tuple): (latitude, longitude) of end node

        Returns:
            float: The euclidean distance between curr_coord and end_coord
        """
        earth_radius = 6378.137
        lon = end_coord[0] * math.pi / 180 - curr_coord[0] * math.pi / 180
        lat = end_coord[1] * math.pi / 180 - curr_coord[1] * math.pi / 180
        a = math.sin(lat / 2)**2 + math.cos(curr_coord[1] * math.pi / 180) * math.cos(
            end_coord[1] * math.pi / 180) * math.sin(lon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = earth_radius * c
        return d * 1000

    def get_path(self, n_to_p, start, end):
        """
        Trace the path starting from the end node to the start node
        
        Parameters:
            n_to_p(dict): A dictionary mapping node to parent
            start(node): The first node in the path
            end(node): The last node in the path

        Returns:
            path(list): The list of nodes comprising the path
        """
        path = []
        path.insert(0, end)
        curr = end
        while curr != start:
            path.insert(0, n_to_p[curr])
            curr = n_to_p[curr]
        return path

    def path_to_coords(self, G, path):
        """
        Convert a path of nodes to coordinates.

        Parameters:
            G(MultiDiGraph): The graph of nodes
            path(list): A list of nodes comprising the path

        Returns:
            coordinates(list): A list coordinates comprised of tuples
        """
        coordinates = []
        for node in path:
            coordinates.append(self.coords(G, node))
        return coordinates

    def between_algorithm(self, G, start, end, percent):
        """
        Finds the maximum elevation path between the nodes of the shortest path

        Parameters:
            G(MultiDiGraph): The graph of nodes
            start(node): The node for the starting location
            end(node): The node for the ending location
            max(bool): Whether or not to max or min elevation.
            percent(float): x% of the shortest path

        Returns:
            path(list): A list of nodes comprising the path    
        """
        path = []
        distance = 0
        shortest_path = nx.shortest_path(G, start, end)
        max_distance = self.path_length(G, nx.shortest_path(G, start, end)) * (1 + percent)
        for i in range(0, len(shortest_path) - 1):
            best_candidate = []
            max_elevation = self.node_elevation(G, shortest_path[i], shortest_path[i+1])
            candidates = nx.all_simple_paths(G, shortest_path[i], shortest_path[i+1], cutoff=10)
            for candidate in candidates:
                if any(x in candidate for x in shortest_path[i+2:]):
                    continue
                path_elevation = self.path_elevation(G, candidate)
                path_length = self.path_length(G, candidate)
                estimated_distance = distance + path_length + self.euclidean(self.coords(G, shortest_path[i+1]), self.coords(G, end))
                if path_elevation >= max_elevation and estimated_distance + 2000 < max_distance:
                    best_candidate = candidate
                    max_elevation = path_elevation
            if not best_candidate:
                best_candidate = [shortest_path[i], shortest_path[i+1]]
            path.extend(best_candidate[:-1])
            distance += self.path_length(G, best_candidate)
        path.append(end)
        return path

    def dijkstra_algorithm(self, G, start, end, max, percent):
            """
            Uses dijkstra's algorithm to find a path where elevation gain is min/max

            Parameters:
                G(MultiDiGraph): The graph of nodes
                start(node): The node for the starting location
                end(node): The node for the ending location
                max(bool): Whether or not to max or min elevation.
                percent(float): x% of the shortest path

            Returns:
                path(list): A list of nodes comprising the path
            """
            mode_constant = -1 if max else 1                                    # Constant used to max/min elevation        
            min_length = self.path_length(G, nx.shortest_path(G, start, end))   # Length of shortest path      
            max_length = min_length * (1 + percent)                             # Maximum allowed length for the new path
            visited = []                                                        # List of visited nodes
            node_to_parent = {}                                                 # Dictionary mapping nodes to their parents (used to find path)       
            unvisited = PriorityQueue()                                         # PQ of tuples (elevation, dist, node)        
            unvisited.put((G.nodes[start]['elevation'], 0, start))              # Initialize PQ with the start node                                     
            while not unvisited.empty():
                (current_elevation, current_distance, current_node) = unvisited.get()
                visited.append(current_node)
                for neighbor_node in G.neighbors(current_node):
                    if neighbor_node not in visited:
                        updated_distance = G.edges[current_node, neighbor_node, 0]['length'] + current_distance
                        estimated_distance = updated_distance + self.euclidean(self.coords(G, neighbor_node), self.coords(G, end))
                        if estimated_distance < max_length:
                            elevation_gain = self.node_elevation(G, current_node, neighbor_node) + current_elevation
                            unvisited.put((mode_constant * elevation_gain, updated_distance, neighbor_node))
                            node_to_parent[neighbor_node] = current_node
            try:
                return self.get_path(node_to_parent, start, end)
            except:
                return nx.shortest_path(G, start, end)

# Used for testing the algorithm
# def main():
#     map_generator = GenerateMap()
#     G = map_generator.create_graph("Amherst, MA", "drive")
#     orig = map_generator.address_to_coords("230 Sunset Ave")
#     dest = map_generator.address_to_coords("30 Eastman Ln")
#     orig_node = map_generator.neareast_node(G, orig)
#     dest_node = map_generator.neareast_node(G, dest)
#     path = map_generator.dijkstra_algorithm(G, orig_node, dest_node, False, .6)
#     print("Path Elevation: {elevation}".format(elevation = map_generator.path_elevation(G, path)))
#     print("Path Length: {length}".format(length = map_generator.path_length(G, path)))

# if __name__ == '__main__':
#     main()