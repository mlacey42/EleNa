from logging import debug
from flask import Flask, request, jsonify
from algorithm import GenerateMap

app = Flask(__name__)

@app.route("/create_path", methods=['POST'])
def create_path():
    data = request.json
    map_generator = GenerateMap()
    G = map_generator.create_graph(data["city_state"], "drive")
    orig_node = map_generator.neareast_node(G, map_generator.address_to_coords(data["start"]))
    dest_node = map_generator.neareast_node(G, map_generator.address_to_coords(data["end"]))
    path = []
    if data["mode"] == "max":
        path = map_generator.between_algorithm(G, orig_node, dest_node, data["percent"])
    else:
        path = map_generator.dijkstra_algorithm(G, orig_node, dest_node, False, data["percent"])
    response = {
        "path": map_generator.path_to_coords(G, path),
        "elevation": map_generator.path_elevation(G, path),
        "length": map_generator.path_length(G, path)
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)