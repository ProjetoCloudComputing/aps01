import pyrebase
import Tarefas
import os
config = {
    "apiKey": "AIzaSyDeOtxp4HzORcB9GTZZSiWRyyHKu7CEg78",
    "authDomain": "cloudcomputing-41896.firebaseapp.com",
    "databaseURL": "https://cloudcomputing-41896.firebaseio.com",
    "projectId": "cloudcomputing-41896",
    "storageBucket": "cloudcomputing-41896.appspot.com",
    "messagingSenderId": "144270564026"
  }

firebase = pyrebase.initialize_app(config)


db = firebase.database()

#exemple of get
def init():
    db.child("/").remove()
    db.child("/").set({"Count":0})

def increseCount(actualValue):
    db.child("/Count").set(actualValue+1)

def get():
    tarefas = db.child("/Tarefas").get()
    print (tarefas.val())
    return tarefas.val()

def post(title, content):
    tarefaId = db.child("/Count").get().val()
    newTarefa = {"title": title, "content": content}
    db.child(f"/Tarefas/{tarefaId}").set(newTarefa)
    increseCount(tarefaId)

def getUnique(id):
    res = db.child("/Tarefas").child(id).get().val()
    if(res): 
        tarefa = {"title": res["title"], "content": res["content"]}
        print(tarefa)
    else:
        print("Tarefa doesnt exists")

def putUnique(id, content):
    old = db.child("/Tarefas").child(id).get().val()
    if(old):
        title = old["title"]
        db.child("/Tarefas").child(id).set({"title": title, "content": content})
        new = db.child("/Tarefas").child(id).get().val()
        return new 
    else:
        print("Cant update a Tarefa that doesnt exists")

def deleteUnique(id):
    exists = db.child("/Tarefas").child(id).get().val()
    if(exists):
        db.child("/Tarefas").child(id).remove()
    else:
        print("Cant delete a Tarefa that doesnt exists")
    

os.system(f"export ALO='{os.getcwd()}'")
os.system("source ~/.zshrc")
