class Tarefas:  
    def __init__(self, idTarefa, titulo, content):
        self.idTarefa = idTarefa
        self.content = content
        self.titulo = titulo

    def setContent(self, content):
        self.content = content

    def getContent(self):
        return self.content

    def setTitulo(self, titulo):
        self.titulo = titulo

    def getTitulo(self):
        return self.titulo

    def setIdTarefa(self, idTarefa):
        self.idTarefa = idTarefa

    def getIdTarefa(self):
        return self.idTarefa


dicTarefas = {}
countTarefas = 0