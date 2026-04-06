import socket
import threading

VERDE = '\033[32m'
VERMELHO = '\033[31m'
RESET = '\033[0m'

IP = '127.0.0.1'
PORTA = 10000
usuarios_online = {}

def lidar_com_peer(conexao, endereco):
    print(f"{VERDE}<conexão TCP realizada>{RESET}")
    ip_cliente = endereco[0]
    nome_cliente = ""
    
    while True:
        try:
            dados = conexao.recv(1024)
            if not dados: break
            
            msg_bruta = dados.decode()
            comandos = msg_bruta.split("\r\n")
            
            for cmd in comandos:
                if not cmd: continue
                
                # O servidor NÃO imprime mais o que recebe em vermelho aqui
                
                if cmd.startswith("USER"):
                    nome_cliente, porta = cmd[5:].split(":")
                    usuarios_online[nome_cliente] = (ip_cliente, porta)
                    print(f"{VERDE}<cadastro usuário ativo>{RESET}")
                    
                elif cmd == "LIST":
                    lista = ":".join([n for n in usuarios_online if n != nome_cliente])
                    msg_resp = f"LIST {lista}"
                    print(f"{VERMELHO}{msg_resp}{RESET}") # Imprime apenas a resposta que ele envia
                    conexao.send(f"{msg_resp}\r\n".encode())
                    
                elif cmd.startswith("ADDR"):
                    alvo = cmd[5:].strip()
                    if alvo in usuarios_online:
                        ip, porta = usuarios_online[alvo]
                        msg_resp = f"ADDR {alvo}:{ip}:{porta}"
                        print(f"{VERMELHO}{msg_resp}{RESET}") # Imprime apenas a resposta que ele envia
                        conexao.send(f"{msg_resp}\r\n".encode())
                    
                elif cmd == "KEEP":
                    pass 
        except:
            break
            
    if nome_cliente in usuarios_online:
        del usuarios_online[nome_cliente]
    print(f"{VERDE}<encerrar conexão>{RESET}")
    conexao.close()

def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((IP, PORTA))
    servidor.listen(10)
    
    print(f"{VERDE}<aguardando conexão>{RESET}")
        
    while True:
        conn, addr = servidor.accept()
        threading.Thread(target=lidar_com_peer, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()