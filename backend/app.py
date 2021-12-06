from logging import debug
from flask import Flask, request, jsonify
from flask_cors import CORS
from algorithm import GenerateMap

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
})

@app.route("/create_path", methods=['POST'])
def create_path():
    data = request.json
    map_generator = GenerateMap()
    G = map_generator.create_graph(data["city_state"], "drive")
    orig_node = map_generator.neareast_node(G, (data["start"]["x"], data["start"]["y"]))
    dest_node = map_generator.neareast_node(G, (data["end"]["x"], data["end"]["y"]))
    path = []
    if data["mode"] == "max":
        path = map_generator.between_algorithm(G, orig_node, dest_node, float(data["extra_distance"]))
    else:
        path = map_generator.dijkstra_algorithm(G, orig_node, dest_node, False, float(data["extra_distance"]))
    response = {
        "path": map_generator.path_to_coords(G, path),
        "elevation": map_generator.path_elevation(G, path),
        "length": map_generator.path_length(G, path)
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)