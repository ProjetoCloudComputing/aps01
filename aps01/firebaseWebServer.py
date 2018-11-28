from flask import Flask, redirect, url_for, request
import json
import pyrebase 

with open('credentials.json') as f:
        data = json.load(f)
config = {
    "apiKey": data["firebase"]["apiKey"],
    "authDomain": data["firebase"]["authDomain"],
    "databaseURL": data["firebase"]["databaseURL"],
    "projectId": data["firebase"]["projectId"],
    "storageBucket": data["firebase"]["storageBucket"],
    "messagingSenderId": data["firebase"]["messagingSenderId"]
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/Tarefa", methods=['GET', 'POST'])
def tarefa():
    if request.method == 'GET':
        tarefas = db.child("Tarefas").get().val()
        print("GET REQUEST: ", tarefas)
        return json.dumps(tarefas, default=lambda x: x.__dict__)

    else:
        print("POST REQUEST")
        body = json.loads(request.data)
        
        tarefaId = db.child("/Count").get().val()
        newTarefa = {"title": body["titulo"], "content": body["content"]}
        db.child(f"/Tarefas/{tarefaId}").set(newTarefa)
        db.child("/Count").set(tarefaId+1)
        return "200"

@app.route("/Tarefa/<int:id>", methods=['GET', 'PUT', 'DELETE'])
def tarefa_id(id):
    if request.method == 'GET':
        res = db.child("/Tarefas").child(id).get().val()
        if(res): 
            tarefa = {"title": res["title"], "content": res["content"]}
            return json.dumps(tarefa, default=lambda x: x.__dict__)
        else:
            return "Tarefa doesnt exist"

    elif request.method == 'PUT':
        body = json.loads(request.data)
        old = db.child("/Tarefas").child(id).get().val()
        if(old):
            title = old["title"]
            db.child("/Tarefas").child(id).set({"title": title, "content": body["content"]})
            new = db.child("/Tarefas").child(id).get().val()
            return json.dumps(new, default=lambda x: x.__dict__)
        else:
            return "Tarefa doesnt exist"

    else:
        exists = db.child("/Tarefas").child(id).get().val()
        if(exists):
            db.child("/Tarefas").child(id).remove()
            return "200"
        else:
            return "Tarefa doesnt exist"
            

@app.route("/healthcheck")
def healthcheck():
    return "200"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)