import math
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

        Parameters:
            location(str): A valid location in the form of city, state, country
            network_type(str): The type of map (drive, walk, bike, etc.)

        Returns:
            G(MultiDiGraph): The graph of nodes
        """
        G = ox.graph_from_place(location, network_type)
        G = ox.add_node_elevations_google(G, api_key='AIzaSyCtgkUV4Om2PaU5AHX0q8CuMcIn8UREaZY')
        G = ox.add_edge_grades(G)
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

    def dijkstra_algorithm(self, G, start, end, mode, percent):
        """
        Uses dijkstra's algorithm to find a path where elevation gain is min/max

        Parameters:
            G(MultiDiGraph): The graph of nodes
            start(node): The node for the starting location
            end(node): The node for the ending location
            mode(str): Whether or not to "max" or "min" elevation.
            percent(float): x% of the shortest path

        Returns:
            path(list): A list of nodes comprising the path
        """
        shortest_path = nx.shortest_path(G, start, end)           # List containing nodes on shortest path
        min_length = self.path_length(G, shortest_path)           # Length of shortest path
        max_length = min_length * (1 + percent)                   # Maximum allowed length for the new path

        visited = []                                              # List of visited nodes
        node_to_parent = {}                                       # Dictionary mapping nodes to their parents (used to find path)
        unvisited = PriorityQueue()                               # PQ of tuples (elevation_gain, dist, node, parent node)
        unvisited.put((G.nodes[start]['elevation'], 0, start, 0)) # Initialize PQ with the start node
        mode_constant = -1 if mode == "max" else 1                # Constant used to max/min elevation

        while not unvisited.empty():
            # Get the highest priority node and marks it as visited
            curr = unvisited.get()
            visited.append(curr[2])
            # Visit neighbors of the current node 
            for neighbor in G.neighbors(curr[2]):
                if neighbor not in visited:
                    # Find the estimated final distance of the path w/ the neighbor
                    between_distance = G.edges[curr[2], neighbor, 0]['length']
                    euclidean_distance = self.euclidean(self.coords(G, neighbor), self.coords(G, end))
                    # If the estimate is shorter than the maximum_length, add the neighbor to the PQ
                    if curr[1] + between_distance + euclidean_distance < max_length:
                        elevation_gain = (G.nodes[neighbor]['elevation'] - G.nodes[curr[2]]['elevation']) + curr[0] if (
                            G.nodes[neighbor]['elevation'] - G.nodes[curr[2]]['elevation']) > 0 else curr[0]
                        distance = curr[1] + between_distance
                        unvisited.put((mode_constant * elevation_gain, distance, neighbor, curr[2]))
                        node_to_parent[neighbor] = curr[2]
                        
        return self.get_path(node_to_parent, start, end)

# def main():
    # map_generator = GenerateMap()
    # G = map_generator.create_graph("Amherst, MA", "drive")
    # orig = map_generator.address_to_coords("230 Sunset Ave") 
    # dest = map_generator.address_to_coords("495 West St")
    # orig_node = map_generator.neareast_node(G, orig)
    # dest_node = map_generator.neareast_node(G, dest)
    # path = map_generator.dijkstra_algorithm(G, orig_node, dest_node, "max", .86)
    # print(path)
    # print(map_generator.path_length(G, path))
    # print(map_generator.path_elevation(G, path))

# if __name__ == '__main__':
#     main()