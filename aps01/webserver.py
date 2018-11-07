from flask import Flask, redirect, url_for, request
import Tarefas
import json

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/Tarefa", methods=['GET', 'POST'])
def tarefa():
    if request.method == 'GET':
        print("GET REQUEST: ", Tarefas.dicTarefas)
        return json.dumps(Tarefas.dicTarefas, default=lambda x: x.__dict__)

    else:
        body = json.loads(request.data)
        Tarefas.countTarefas += 1
        newId = Tarefas.countTarefas
        tarefa = Tarefas.Tarefas(newId ,body["titulo"], body["content"])
        Tarefas.dicTarefas[newId] = tarefa
        print(Tarefas.dicTarefas)
        return "200"

@app.route("/Tarefa/<int:id>", methods=['GET', 'PUT', 'DELETE'])
def tarefa_id(id):
    if request.method == 'GET':
        try:
            tarefa_search = Tarefas.dicTarefas[id]
            return json.dumps(tarefa_search, default=lambda x: x.__dict__)
        except:
            return "Tarefa doesnt exist"

    elif request.method == 'PUT':
        body = json.loads(request.data)
        try:
            Tarefas.dicTarefas[id].setContent(body["content"])
            return json.dumps(Tarefas.dicTarefas[id], default=lambda x: x.__dict__)
        except:
            return "Tarefa doesnt exist"

    else:
        try:
            del Tarefas.dicTarefas[id]
            return "200"
        except:
            return "Tarefa doesnt exist"

@app.route("/healthcheck")
def healthcheck():
    return "200"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)