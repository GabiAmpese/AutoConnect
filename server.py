import tornado.ioloop # Mantém o servidor rodando infinitamente
import tornado.web # Lida com as rotas 
import tornado.websocket # Tempo real
import os

# Conjunto para guardar as abas/janelas conectadas
conexoes_ativas = set()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # Renderiza a interface web que está na mesma pasta do script
        try:
            self.render("index.html")
        except Exception as e:
            self.set_status(404)
            self.write(f"Erro: Arquivo index.html não encontrado na pasta do servidor. {e}")

class AutoConnectHandler(tornado.websocket.WebSocketHandler): # classe que herda os poderes do tornado
    
    # 1. HANDSHAKE (Nova conexão) ====================
    def open(self):
        conexoes_ativas.add(self)
        print("Novo usuário conectado ao AutoConnect!")

    # 2. PERSISTÊNCIA (Recebendo mensagens)  ====================
    def on_message(self, message):
        print(f"Mensagem bruta recebida: {message}")
        
        # O servidor recebe a mensagem e simplesmente repassa (broadcast) 
        # para todo mundo. O 'index.html' é quem vai decidir o que fazer com ela.
        for conexao in conexoes_ativas:
            conexao.write_message(message)

    # 3. ENCERRAMENTO (Fechando conexão)  ====================
    def on_close(self):
        conexoes_ativas.remove(self)
        print("Usuário desconectado.")

    # Permite acesso local
    def check_origin(self, origin):
        return True

def make_app():
    # Obtém o caminho absoluto da pasta onde o server.py está localizado
    caminho_projeto = os.path.dirname(os.path.abspath(__file__))
    
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws", AutoConnectHandler),
        # Fallback para arquivos estáticos (permite acessar localhost:8888/index.html se necessário)
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": caminho_projeto}),
    ], template_path=caminho_projeto, debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("🚗 Servidor AutoConnect rodando na porta 8888...")
    tornado.ioloop.IOLoop.current().start()