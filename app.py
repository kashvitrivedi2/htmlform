from flask import Flask, render_template,request
import os, json

app=Flask(__name__)

@app.route("/")
def home():
    return(render_template("index.html"))

@app.post("/submit")
def submit():
    username=request.form.get("username")
    password=request.form.get("password")
    _textarea=request.form.get("textarea")

    data=f"[{username},{password},{_textarea}]\n"
    with open("data.txt","a+") as _file:
        _file.write(data)
    _file.close()

    return("Thank You")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))