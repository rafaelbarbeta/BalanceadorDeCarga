import os

from flask import Flask, request, render_template, send_from_directory, jsonify, make_response
import pymongo
from bson import json_util
import json
import time

def create_app(config=None):
    app = Flask(__name__, static_folder="pub", static_url_path='/pub')

    app.config.update(dict(DEBUG=True))
    app.config.update(config or {})

    mongo_conn = pymongo.MongoClient(f"mongodb://root:MongoDB@{os.environ.get('MONGO')}")
    db_all = mongo_conn["potencias"]
    db = db_all["col_potencias"]


    def power(x, y):
        power_type = os.environ.get("POWER_TYPE")
        if power_type == "A":
            return x ** y
        elif power_type == "A_line":
            return y ** x
        else:
            raise Exception("POWER_TYPE env not set!")

    @app.route("/")
    def my_app():
        return send_from_directory("pub", "index.html")
    
    
    @app.route("/power", methods=["POST"])
    def compute_power():
        x = int(request.json["x"])
        y = int(request.json["y"])
        print(power(x,y))
        db.insert_one({"timestamp":int(time.time()) % 1000000000000, "x":x, "y":y, "resultado":power(x,y), "servico":os.environ.get("POWER_TYPE")})
        response = make_response(
                jsonify(
                    {"mensagem": "Potência Calculada!"}
                ),
                200,
            )
        response.headers["Content-Type"] = "application/json"
        return response
    
    @app.route("/getValues")
    def get_values_all():
        response = make_response(
                jsonify(
                    json.loads(json_util.dumps(db.find({}, {'_id': False})))
                ),
                200,
            )
        response.headers["Content-Type"] = "application/json"
        return response
    
    @app.route("/check_alive")
    def alive():
        return "Alive!"

    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app = create_app()
    app.run(host="0.0.0.0", port=port)