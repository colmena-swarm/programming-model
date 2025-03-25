import threading

from flask import Flask, request, jsonify

app = Flask(__name__)

grouping_dictionary = {
        "a": "1",
        "b": "1",
        "red": "1",
        "gold": "1"
}

@app.route('/', methods=['GET'])
def handle_request():
    device_id = request.args.get('device_id')
    if not device_id:
        return jsonify({"error": "device_id parameter is required"}), 400

    grouping = grouping_dictionary[device_id]
    response_data = {"id": grouping}
    return jsonify(response_data)

def update_grouping():
    print("split group")
    global grouping_dictionary
    grouping_dictionary = {
        "a": "1",
        "b": "2",
        "red": "1",
        "gold": "2"
}

if __name__ == '__main__':
    timer = threading.Timer(30, update_grouping)
    timer.start()
    app.run(port=12442, debug=True)
