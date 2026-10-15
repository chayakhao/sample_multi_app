import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

mongo_uri = os.environ.get("MONGO_URI", "mongodb://admin:mongo@mongo:27017/")
db_name = os.environ.get("DB_NAME", "ipa2026_db")

client = MongoClient(mongo_uri)
db = client[db_name]
routers_collection = db["routers"]
status_collection = db["interface_status"]


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ip = request.form.get("ip")
        username = request.form.get("username")
        password = request.form.get("password")
        if ip and username and password:
            routers_collection.insert_one(
                {"ip": ip, "username": username, "password": password}
            )
        return redirect(url_for("index"))

    routers = list(routers_collection.find())
    return render_template("index.html", routers=routers)


@app.route("/delete/<router_id>", methods=["POST"])
def delete_router(router_id):
    from bson.objectid import ObjectId

    routers_collection.delete_one({"_id": ObjectId(router_id)})
    return redirect(url_for("index"))


@app.route("/router/<router_ip>")
def router_detail(router_ip):
    # ดึงข้อมูล 3 ครั้งล่าสุดของ router ตัวนี้
    logs = list(
        status_collection.find({"router_ip": router_ip}).sort("timestamp", -1).limit(3)
    )
    return render_template("router_detail.html", router_ip=router_ip, logs=logs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
