# aps01
# Repositorio do projeto, arquivos importantes:
1. run.py: este arquivo cria o loadbalancer em uma instancia na aws (Nao se esqueça de preencher o credentials antes de utilizar este arquivo)
2. credentials.py: o credentials ja esta parcialmente preenchido, basta preencher o 
ACCESS_KEY com sua access_key da aws e o mesmo com a SECRET_KEY
3. webaps4.py: Este arquivo é o próprio Load Balancer que será executado na máquina
4. firebaseWebServer.py: corresponde ao servidor que cada maquina do load balancer estara rodando, utilizando o firebase como database
5. criaVar.sh: este arquivo cria a variavel SERVER_ADRESS no ambiente, que torna possivel utilizar o arquivo tarefa, lembre-se de rodar este aquivo como
<code>source ./criaVar.sh http://iploadbalancer:5000</code>
5. tarefa: o tarefa é uma forma mais simples de testar o ambiente, basta rodar <code>export PATH="caminhoateapasta:$PATH"</code>, lembrando de dar source no .bashrc após isto, assim, basta seguir as instruções do arquivo. Digite tarefa help para verificar quais os comandos possíveis.
