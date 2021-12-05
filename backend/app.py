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
    path = map_generator.between_algorithm(G, orig_node, dest_node, data["mode"], data["percent"])
    response = {
        "path": path,
        "elevation": map_generator.path_elevation(G, path),
        "length": map_generator.path_length(G, path)
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)