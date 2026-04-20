import tornado.ioloop # Mantém o servidor rodando infinitamente
import tornado.web # Lida com as rotas 
import tornado.websocket # Tempo real
import json # Importante: Precisamos do JSON para ler as ações!

# Conjunto para guardar as abas/janelas conectadas
conexoes_ativas = set()

class AutoConnectHandler(tornado.websocket.WebSocketHandler): # classe que herda os poderes do tornado
    
    # 1. HANDSHAKE (Nova conexão)
    def open(self):
        conexoes_ativas.add(self)
        print("Novo usuário conectado ao AutoConnect!")

    # 2. PERSISTÊNCIA (Recebendo mensagens)
    def on_message(self, message):
        print(f"Mensagem bruta recebida: {message}")
        
        # O servidor recebe a mensagem e simplesmente repassa (broadcast) 
        # para todo mundo. O 'index.html' é quem vai decidir o que fazer com ela.
        for conexao in conexoes_ativas:
            conexao.write_message(message)

    # 3. ENCERRAMENTO (Fechando conexão)
    def on_close(self):
        conexoes_ativas.remove(self)
        print("Usuário desconectado.")

    # Permite acesso local
    def check_origin(self, origin):
        return True

def make_app():
    return tornado.web.Application([
        (r"/ws", AutoConnectHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("🚗 Servidor AutoConnect rodando na porta 8888...")
    tornado.ioloop.IOLoop.current().start()