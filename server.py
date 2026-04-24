import tornado.ioloop # Mantém o servidor rodando infinitamente
import tornado.web # Cria as rotas HTTP
import tornado.websocket # Comunicação em tempo real
import json # Json utilizado para troca de dados entre Js e Python
import os # Localiza os arquivos

# Conjunto para guardar os usuário conectados
clientes_conectados = set() # Utilizamos set pois não permite clientes repetidos

class PaginaCliente(tornado.web.RequestHandler): # Tornado lê o arquivo html e envia para navegador abrir o CLIENTE
    def get(self):
        self.render("cliente.html")  
        
class PaginaOficina(tornado.web.RequestHandler): # Tornado lê o arquivo html e envia para navegador abrir a OFICINA
    def get(self):
        self.render("oficina.html")
        
class AutoConnectWebSocket(tornado.websocket.WebSocketHandler): # ciclo de vida do websocket
    
    # 1. HANDSHAKE (Nova conexão) 
    def open(self): # Quando um novo usuário conecta, adiciona ele no conjunto
        clientes_conectados.add(self)
        print("Novo usuário conectado ao AutoConnect!")

    # 2. Recebendo mensagens
    def on_message(self, mensagem):
        print(f"Mensagem recebida: {mensagem}")
        
        # O servidor recebe a mensagem e repassa (BROADCAST) para todo mundo
        # O front-end decide para quem a mensagem deve ser enviada
        for conexao in clientes_conectados:
            conexao.write_message(mensagem)

    # 3. ENCERRAMENTO (Fechando conexão)
    def on_close(self): # Remove o usuário do conjunto quando ele é desconectado
        clientes_conectados.remove(self)
        print("Usuário desconectado.")

    # Permite acesso local
    def check_origin(self, origin): # Medida de segurança do Tornado - bloqueia conexões de origem diferente por padrão
        return True # Retornamos True para permitir conexões de qualquer origem para facilitar os testes

def configurar_servidor():
    # Obtém o caminho da pasta onde o server.py está localizado
    caminho_projeto = os.path.dirname(os.path.abspath(__file__))
    
    # Diz qual código será executado para cada URL que o usuário acessar
    return tornado.web.Application([
        (r"/", PaginaCliente),        
        (r"/cliente", PaginaCliente), 
        (r"/oficina", PaginaOficina),
        (r"/ws", AutoConnectWebSocket),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": caminho_projeto}), # serve para o servidor carregar as imagens
    ], template_path=caminho_projeto, debug=True)

if __name__ == "__main__": # Execução do servidor
    app = configurar_servidor()
    app.listen(8888)
    print("🚗 Servidor AutoConnect rodando na porta 8888...")
    print("👉 Cliente: http://localhost:8888/cliente")
    print("👉 Oficina: http://localhost:8888/oficina")
    tornado.ioloop.IOLoop.current().start() # Mantém o servidor rodando