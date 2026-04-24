import tornado.ioloop # Mantém o servidor rodando infinitamente
import tornado.web # Cria as rotas HTTP
import tornado.websocket # Comunicação em tempo real
import os # Localiza os arquivos

# Conjunto para guardar os usuário conectadas
conexoes_ativas = set() # Utilizamos set pois não permite clientes repetidos

class MainHandler(tornado.web.RequestHandler): # Abre a página web
    def get(self): # Executa quando a porta 8888 é acessada
        # Abre a interface web 
        try:
            self.render("index.html")
        except Exception as e:
            self.set_status(404)
            self.write(f"Erro: Arquivo index.html não encontrado na pasta do servidor. {e}")

class AutoConnectHandler(tornado.websocket.WebSocketHandler): # classe que herda os poderes do tornado - implementa o ciclo do websocket
    
    # 1. HANDSHAKE (Nova conexão)
    def open(self): # Quando um novo usuário conecta, a função adiciona ele na lista
        conexoes_ativas.add(self)
        print("Novo usuário conectado ao AutoConnect!")

    # 2. PERSISTÊNCIA (Recebendo mensagens)  
    def on_message(self, message):
        print(f"Mensagem bruta recebida: {message}")
        
        # O servidor recebe a mensagem e repassa (BROADCAST) para todo mundo
        # O html decide oq fazer com a mensagem
        for conexao in conexoes_ativas:
            conexao.write_message(message)

    # 3. ENCERRAMENTO (Fechando conexão)
    def on_close(self): # Remove o usuário da lista quando ele é desconectado
        conexoes_ativas.remove(self)
        print("Usuário desconectado.")

    # Permite acesso local
    # O Tornado bloqueia conexões de origem diferente por padrão
    # Retornamos True para permitir conexões de qualquer origem para facilitar os testes
    def check_origin(self, origin):
        return True

def make_app():
    # Obtém o caminho da pasta onde o server.py está localizado
    caminho_projeto = os.path.dirname(os.path.abspath(__file__))
    
    # Diz qual código será executado para cada URL que o usuário acessar
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws", AutoConnectHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": caminho_projeto}),
    ], template_path=caminho_projeto, debug=True)

if __name__ == "__main__": # Execução do servidor
    app = make_app()
    app.listen(8888)
    print("🚗 Servidor AutoConnect rodando na porta 8888...")
    tornado.ioloop.IOLoop.current().start() # Mantém o servidor rodando