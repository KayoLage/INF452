# TP1 - INF452 (Sockets)
# NOME:      Kayo de Melo Lage
# MATRÍCULA: 116211

import socket
import threading
import time
import sys

# Definição de cores ANSI
VERDE = '\033[32m'
VERMELHO = '\033[31m'
AZUL = '\033[34m'
RESET = '\033[0m'

DUMMY_IP = '127.0.0.1' 
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
            # Garante que a mensagem recebida saia em preto (RESET), mesmo se o terminal estava em AZUL
            sys.stdout.write(RESET + '\r\033[K') 
            print(f"{nome_peer} diz: {mensagem}")
            sys.stdout.flush()
        except: break
            
    sys.stdout.write(RESET + '\r\033[K')
    print(f"{VERDE}<encerrar conexão peer>{RESET}")
    
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
                # Respostas do protocolo em Vermelho conforme PDF
                if msg.startswith("LIST"):
                    lista = msg.replace("LIST ", "").strip().replace(':', ', ')
                    sys.stdout.write(RESET + '\r\033[K')
                    print(f"Ativos (além de você):\n{lista if lista else 'Nenhum'}")
                elif msg.startswith("ADDR"):
                    partes = msg.split(": ")
                    if len(partes) >= 3:
                        nome = partes[0].replace("ADDR ", "")
                        peers_conhecidos[nome] = (partes[1], partes[2])
        except: break

def receber_conexoes_p2p(peer_socket):
    while True:
        try:
            conn_peer, _ = peer_socket.accept()
            sys.stdout.write(RESET + '\r\033[K')
            print(f"{VERDE}<conexão TCP realizada>{RESET}")
            
            id_msg = conn_peer.recv(1024).decode().strip()
            nome_amigo = id_msg[5:] if id_msg.startswith("USER") else "Desconhecido"
                
            print(f"Conectado a {nome_amigo}")
            sessao_atual['socket'] = conn_peer
            sessao_atual['nome_peer'] = nome_amigo
            sessao_atual['sou_o_origem'] = False
            
            threading.Thread(target=ouvir_peer, args=(conn_peer, nome_amigo), daemon=True).start()
        except: break

def main():
    # Para o nome de usuário aparecer em azul, usamos write(AZUL) antes do input
    sys.stdout.write("Nome de usuário: " + AZUL)
    sys.stdout.flush()
    nome_usuario = input("")
    sys.stdout.write(RESET) # Reseta imediatamente após o input

    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.bind((HOST, PORT))
    peer_socket.listen(5)
    minha_porta = peer_socket.getsockname()[1]
    
    print(f"{VERDE}<inicia conexão TCP serv.>{RESET}")
    server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_conn.connect((DUMMY_IP, SERVER_PORT))

    # Protocolo USER em Vermelho
    msg_reg = f"USER {nome_usuario}:{minha_porta}"
    print(f"{VERMELHO}{msg_reg}{RESET}")
    server_conn.send(f"{msg_reg}\r\n".encode())
    
    print(f"{VERDE}<cadastro usuário ativo>{RESET}")
    print(f"{VERDE}<aguardando conexão>{RESET}")

    threading.Thread(target=receber_conexoes_p2p, args=(peer_socket,), daemon=True).start()
    threading.Thread(target=ouvir_servidor, args=(server_conn,), daemon=True).start()
    threading.Thread(target=keep_alive, args=(server_conn,), daemon=True).start()

    while True:
        # Tudo que o usuário digita aparece em azul no terminal
        sys.stdout.write(AZUL)
        sys.stdout.flush()
        linha = input("")
        sys.stdout.write(RESET) # Reseta para que prints do sistema não saiam em azul
        
        if not linha: continue
        
        if linha == "/list":
            print(f"{VERMELHO}LIST{RESET}")
            server_conn.send("LIST\r\n".encode())
            
        elif linha.startswith("/chat"):
            partes = linha.split(" ")
            if len(partes) >= 2:
                nome_alvo = partes[1]
                print(f"{VERMELHO}ADDR {nome_alvo}{RESET}")
                server_conn.send(f"ADDR {nome_alvo}\r\n".encode())
                time.sleep(0.4) 
                
                if nome_alvo in peers_conhecidos:
                    ip, porta = peers_conhecidos[nome_alvo]
                    print(f"{VERDE}<inicia conexão TCP peer>{RESET}")
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((ip, int(porta)))
                        # Identificação inicial USER em vermelho
                        print(f"{VERMELHO}USER {nome_usuario}{RESET}")
                        sock.send(f"USER {nome_usuario}\r\n".encode())
                        
                        sessao_atual['socket'] = sock
                        sessao_atual['nome_peer'] = nome_alvo
                        sessao_atual['sou_o_origem'] = False
                        
                        threading.Thread(target=ouvir_peer, args=(sock, nome_alvo), daemon=True).start()
                    except: print("Erro ao conectar.")
            
        elif linha == "/bye":
            if sessao_atual['socket']:
                sessao_atual['sou_o_origem'] = True 
                sessao_atual['socket'].close()
                sessao_atual['socket'] = None
            
        elif linha == "/exit":
            print(f"{VERDE}<encerrar conexão serv.>{RESET}")
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