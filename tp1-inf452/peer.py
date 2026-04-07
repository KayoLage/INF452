# TP1 - INF452 (Sockets)
# NOME:      Kayo de Melo Lage
# MATRÍCULA: 116211

import socket
import threading
import time
import sys

IP = '200.235.131.66' # SERVER VITOR => 200.235.131.66 | LOCAL => 127.0.0.1
SERVER_PORT = 10000

HOST = ''
PORT = 0

peers_conhecidos = {}
sessao_atual = {'socket': None, 'nome_peer': None, 'sou_o_origem': False}

def keep_alive(server_conn):
    while True:
        try:
            time.sleep(5)
            server_conn.send("KEEP\r\n".encode())
        except: break

def ouvir_peer(conn_peer, nome_peer):
    while True:
        try:
            dados = conn_peer.recv(1024)
            if not dados: break
            
            mensagem = dados.decode().strip()
            print(f"{nome_peer} diz: {mensagem}")
        except: break
            
    print("<encerrar conexão peer>")
    
    if not sessao_atual['sou_o_origem']:
        print(f"Conexão com {nome_peer} finalizada")
    
    if sessao_atual['socket'] == conn_peer:
        sessao_atual['socket'] = None
        sessao_atual['nome_peer'] = None
    conn_peer.close()

def ouvir_servidor(server_conn):
    while True:
        try:
            dados = server_conn.recv(1024)
            if not dados: break
            respostas = dados.decode().split("\r\n")
            for msg in respostas:
                if not msg: continue
                if msg.startswith("LIST"):
                    lista = msg.replace("LIST ", "").strip().replace(':', ', ')
                    print(f"Ativos (além de você):\n{lista if lista else 'Nenhum'}")
                elif msg.startswith("ADDR"):
                    partes = msg.split(":")
                    if len(partes) >= 3:
                        nome = partes[0].replace("ADDR ", "")
                        peers_conhecidos[nome] = (partes[1], partes[2])
        except: break

def receber_conexoes_p2p(peer_socket):
    while True:
        try:
            conn_peer, _ = peer_socket.accept()
            print("<conexão TCP realizada>")
            
            id_msg = conn_peer.recv(1024).decode().strip()
            nome_amigo = id_msg[5:] if id_msg.startswith("USER") else "Desconhecido"
                
            print(f"Conectado a {nome_amigo}")
            sessao_atual['socket'] = conn_peer
            sessao_atual['nome_peer'] = nome_amigo
            sessao_atual['sou_o_origem'] = False
            
            threading.Thread(target=ouvir_peer, args=(conn_peer, nome_amigo), daemon=True).start()
        except: break

def main():
    nome_usuario = input("Nome de usuário: ")

    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.bind((HOST, PORT))
    peer_socket.listen(5)
    minha_porta = peer_socket.getsockname()[1]
    
    print("<inicia conexão TCP serv.>")
    server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_conn.connect((IP, SERVER_PORT))

    msg_reg = f"USER {nome_usuario}:{minha_porta}"
    print(msg_reg)
    server_conn.send(f"{msg_reg}\r\n".encode())
    
    print("<cadastro usuário ativo>")
    print("<aguardando conexão>")

    threading.Thread(target=receber_conexoes_p2p, args=(peer_socket,), daemon=True).start()
    threading.Thread(target=ouvir_servidor, args=(server_conn,), daemon=True).start()
    threading.Thread(target=keep_alive, args=(server_conn,), daemon=True).start()

    while True:
        linha = input("")
        
        if not linha: continue
        
        if linha == "/list":
            print("LIST")
            server_conn.send("LIST\r\n".encode())
            
        elif linha.startswith("/chat"):
            partes = linha.split(" ")
            if len(partes) >= 2:
                nome_alvo = partes[1]
                print(f"ADDR {nome_alvo}")
                server_conn.send(f"ADDR {nome_alvo}\r\n".encode())
                time.sleep(0.4) 
                
                if nome_alvo in peers_conhecidos:
                    ip, porta = peers_conhecidos[nome_alvo]
                    print("<inicia conexão TCP peer>")
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((ip, int(porta)))
                        print(f"USER {nome_usuario}")
                        sock.send(f"USER {nome_usuario}\r\n".encode())
                        
                        sessao_atual['socket'] = sock
                        sessao_atual['nome_peer'] = nome_alvo

                        # Quem chama o /chat é origem
                        sessao_atual['sou_o_origem'] = True
                        
                        threading.Thread(target=ouvir_peer, args=(sock, nome_alvo), daemon=True).start()
                    except: print("Erro ao conectar.")
            
        elif linha == "/bye":
            if sessao_atual['socket']:
                sessao_atual['sou_o_origem'] = True 
                try:
                    # Corta a conexão nos dois sentidos imediatamente (evita de ficar uma thread bloqueada no recv())
                    sessao_atual['socket'].shutdown(socket.SHUT_RDWR)
                except:
                    pass # Evita erro se o socket já tiver caído
                
                sessao_atual['socket'].close()
                sessao_atual['socket'] = None
            
        elif linha == "/exit":
            print("<encerrar conexão serv.>")
            break
            
        else:
            if sessao_atual['socket']:
                try:
                    sessao_atual['socket'].send(f"{linha}\r\n".encode())
                except: pass

    server_conn.close()
    peer_socket.close()

if __name__ == "__main__":
    main()