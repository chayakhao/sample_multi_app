from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# เชื่อมต่อกับ mongo container ผ่านชื่อ container name
client = MongoClient("mongodb://mongo:27017/")
db = client["ipa2026_db"]
routers_col = db["routers"]


@app.route("/")
def main():
    routers = list(routers_col.find())
    return render_template("index.html", routers=routers)


@app.route("/add", methods=["POST"])
def add_router():
    ip = request.form.get("ip")
    username = request.form.get("username")
    password = request.form.get("password")

    if ip and username and password:
        routers_col.insert_one({"ip": ip, "username": username, "password": password})
    return redirect(url_for("main"))


@app.route("/delete", methods=["POST"])
def delete_router():
    try:
        router_id = request.form.get("id")
        if router_id:
            routers_col.delete_one({"_id": ObjectId(router_id)})
    except Exception:
        pass
    return redirect(url_for("main"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
