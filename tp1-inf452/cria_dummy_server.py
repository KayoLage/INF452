# Cria servidor dummy para testes iniciais

# Servidor dummy atendendo as especificoes do PDF do trabalho (assets/trab_sockets.pdf)

import socket
import threading

IP = '127.0.0.1'
PORTA = 10000
usuarios_online = {} # nome: (ip, porta)

def lidar_com_peer(conexao, endereco):
    ip_cliente = endereco[0]
    nome_cliente = ""
    
    while True:
        try:
            dados = conexao.recv(1024)
            if not dados: break
            
            comando = dados.decode().strip()
            
            if comando.startswith("USER"):
                # USER Fulano: 20000 
                dados_user = comando.replace("USER ", "")
                nome_cliente, porta = dados_user.split(": ")
                usuarios_online[nome_cliente] = (ip_cliente, porta)
                print(f"Cadastro: {nome_cliente} em {ip_cliente}:{porta}")
                
            elif comando == "LIST":
                # Resposta: LIST nome1:nome2: 
                lista = ":".join([n for n in usuarios_online if n != nome_cliente])
                conexao.send(f"LIST {lista}\r\n".encode())
                
            elif comando.startswith("ADDR"):
                # ADDR Fulano 
                alvo = comando.replace("ADDR ", "")
                if alvo in usuarios_online:
                    ip, porta = usuarios_online[alvo]
                    # Resposta: ADDR nome: ip: porta 
                    resposta = f"ADDR {alvo}: {ip}: {porta}\r\n"
                    conexao.send(resposta.encode())
                    
            elif comando == "KEEP":
                pass # PDF diz que KEEP não tem resposta 
                
        except:
            break
            
    if nome_cliente in usuarios_online:
        del usuarios_online[nome_cliente]
    conexao.close()

def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((IP, PORTA))
    servidor.listen(10)
    print("🤖 Servidor Dummy Central Online (Porta 10000)")

    while True:
        conn, addr = servidor.accept()
        threading.Thread(target=lidar_com_peer, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()