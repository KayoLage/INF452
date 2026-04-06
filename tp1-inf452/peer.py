import socket
import threading
import time

# Constantes de IP
DUMMY_IP = '127.0.0.1' 
OFFICIAL_IP = '200.235.131.66' # IP server original
SERVER_PORT = 10000

HOST = ''   # Escuta em todas as interfaces
PORT = 0    # Porta P2P aleatória

# Dicionário para armazenar endereços de peers resolvidos via ADDR [cite: 31]
peers_conhecidos = {}

def keep_alive(server_conn):
    """
    Envia KEEP a cada 'tempo' segundos para o servidor não encerrar a conexão. 
    """
    while True:
        try:
            tempo = 5 # 5s de keep alive 
            time.sleep(tempo)
            server_conn.send("KEEP\r\n".encode()) # Terminação \r\n obrigatória 
        except:
            print("\n[ERRO] Conexão com o servidor caiu. Thread KeepAlive encerrada.")
            break

def conectar_servidor(ip_destino, porta_destino, nome, minha_porta):
    """
    Estabelece a conexão TCP, registra o usuário e dispara o KeepAlive.
    Retorna o socket conectado ou None se falhar.
    """
    try:
        server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_conn.connect((ip_destino, porta_destino))
        print(f"[SISTEMA] Conectado ao servidor central ({ip_destino}).")

        # Manda a mensagem de registro: USER <nome>: <porta> 
        # Formato exige espaço após o ":" conforme PDF 
        msg_registro = f"USER {nome}: {minha_porta}\r\n"
        server_conn.send(msg_registro.encode())
        print(f"[SISTEMA] Enviado: {msg_registro.strip()}")
        
        # Dispara a thread do KEEP ALIVE em background
        threading.Thread(target=keep_alive, args=(server_conn,), daemon=True).start()

        return server_conn # Retorna o socket para podermos enviar comandos (como LIST) depois

    except ConnectionRefusedError:
        print(f"[ERRO] Servidor ({ip_destino}) offline. Crie o servidor dummy primeiro!")
        return None
    except Exception as e:
        print(f"[ERRO] Falha na conexão: {e}")
        return None

def enviar_mensagem(ip_destino, porta_destino, meu_nome, mensagem):
    """
    Atua como cliente P2P => Conecta na porta de um amigo, entrega a mensagem e vai embora. [cite: 17, 19]
    """
    try:
        # Cria um socket temporário de saída
        socket_envio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Conecta no seu amigo
        socket_envio.connect((ip_destino, int(porta_destino)))
        
        # Primeiro identifica-se ao peer servidor: USER <nome>\r\n 
        socket_envio.send(f"USER {meu_nome}\r\n".encode())
        
        # Envia a mensagem de texto [cite: 22]
        # Garante \r\n para o receptor conseguir processar individualmente [cite: 61, 62]
        socket_envio.send(f"{mensagem}\r\n".encode())
        
        # Usa shutdown para desbloquear recv() no destino antes de fechar [cite: 46, 47]
        socket_envio.shutdown(socket.SHUT_RDWR)
        socket_envio.close()
        print(f"[SISTEMA] Mensagem enviada para {ip_destino}:{porta_destino}")
        
    except ConnectionRefusedError:
        print(f"[ERRO] O usuário em {ip_destino}:{porta_destino} não está online.")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar mensagem: {e}")

def ouvir_servidor(server_conn):
    """
    Fica escutando as respostas do servidor central (ex: quando você pede o LIST) 
    """
    while True:
        try:
            tam_buffer_comando = 1024 # recebe 1024 bytes (1 KB) de dados
            dados = server_conn.recv(tam_buffer_comando)
            if not dados:
                break
            
            # Divide mensagens baseando-se no delimitador \r\n [cite: 62]
            respostas = dados.decode().split("\r\n")
            
            for msg in respostas:
                if msg.startswith("LIST"):
                    # Formato: LIST <nome1>:<nome2> 
                    print(f"\n[SERVIDOR CENTRAL] Usuários ativos: {msg[5:]}")
                elif msg.startswith("ADDR"):
                    # Formato: ADDR <nome>: <ip>: <porta> 
                    partes = msg.split(": ")
                    if len(partes) == 4:
                        nome_alvo = partes[1]
                        ip_alvo = partes[2]
                        porta_alvo = partes[3]
                        peers_conhecidos[nome_alvo] = (ip_alvo, porta_alvo)
                        print(f"\n[SISTEMA] Endereço de '{nome_alvo}' obtido: {ip_alvo}:{porta_alvo}")
        except:
            break
            
# === RECEBIMENTO DE MENSAGENS === #

def lidar_com_amigo(conn_peer, endereco_peer):
    """
    Fica em loop infinito lendo as mensagens de um amigo específico. [cite: 17]
    """
    try:
        # O peer servidor primeiro espera a identificação: USER <nome> 
        primeira_msg = conn_peer.recv(1024).decode().strip()
        if primeira_msg.startswith("USER"):
            nome_amigo = primeira_msg[5:]
            print(f"\n[P2P] Conectado com {nome_amigo} ({endereco_peer})")
            
            while True:
                dados = conn_peer.recv(1024)
                if not dados:
                    break 
                
                mensagem = dados.decode().strip()
                print(f"\n[{nome_amigo}]: {mensagem}")
    except:
        pass
    finally:
        conn_peer.close()

def receber_conexoes_p2p(peer_socket):
    """
    Fica no accept() esperando alguém tentar abrir um chat. [cite: 14]
    """
    while True:
        try:
            # O código trava aqui até alguém conectar na sua porta [cite: 17]
            conn_peer, endereco_peer = peer_socket.accept()
            
            # Quando alguém conecta, cria uma Thread só para esse amigo! [cite: 44, 49]
            threading.Thread(target=lidar_com_amigo, args=(conn_peer, endereco_peer), daemon=True).start()
        except:
            break
        
# ============================== #
    
def main():
    
    nome = input("Digite seu nome de usuário: ")

    # ==== LADO LOCAL ==== #
    # Cria o socket P2P (lado Mini-Servidor)
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_socket.bind((HOST, PORT)) # Porta 0 para SO escolher automática [cite: 42]
    
    # Define o tamanho da fila de espera para a escuta das mensagens
    backlog_size = 5
    peer_socket.listen(backlog_size)
    
    minha_porta = peer_socket.getsockname()[1] # [cite: 43]
    print(f"[{nome}] Escutando conexões P2P na porta {minha_porta}")

    # ===================== #
    
    # === LADO SERVIDOR === #
    
    # Conecta ao Servidor
    ip_alvo = DUMMY_IP 
    server_conn = conectar_servidor(ip_alvo, SERVER_PORT, nome, minha_porta)
    
    # ===================== #
    
    # Thread do recepcionista P2P como daemon para encerrar com o programa [cite: 57, 58]
    threading.Thread(target=receber_conexoes_p2p, args=(peer_socket,), daemon=True).start()
    
    # Ouve o servidor para ler as respostas do LIST e ADDR
    threading.Thread(target=ouvir_servidor, args=(server_conn,), daemon=True).start()

    # O Loop Principal (A "Boca" do programa) [cite: 26, 27]
    print("\n" + "="*30)
    print("        CHAT P2P INICIADO")
    print("="*30)
    print("Comandos disponíveis:")
    print("  /list             -> Lista usuários online")
    print("  /chat <nome>      -> Inicia conversa com alguém")
    print("  /msg <nome> <msg> -> Envia mensagem para alguém já consultado")
    print("  /sair             -> Fecha o programa")
    print("="*30 + "\n")

    try:
        while True:
            linha = input("")
            if not linha: continue
            
            partes = linha.split(" ", 2)
            comando = partes[0].lower()

            if comando == "/list":
                server_conn.send("LIST\r\n".encode())
                
            elif comando == "/chat":
                # Primeiro passo: pedir o endereço ao servidor central
                if len(partes) >= 2:
                    nome_alvo = partes[1]
                    server_conn.send(f"ADDR {nome_alvo}\r\n".encode())
                else:
                    print("[ERRO] Uso: /chat <nome>")

            elif comando == "/msg":
                # Segundo passo: enviar a mensagem usando dados de ADDR salvos
                if len(partes) >= 3:
                    nome_alvo = partes[1]
                    texto = partes[2]
                    if nome_alvo in peers_conhecidos:
                        ip, porta = peers_conhecidos[nome_alvo]
                        enviar_mensagem(ip, porta, nome, texto)
                    else:
                        print(f"[ERRO] Primeiro use /chat {nome_alvo} para localizar o usuário.")
                else:
                    print("[ERRO] Uso: /msg <nome> <mensagem>")

            elif comando == "/sair":
                print("[SISTEMA] Saindo...")
                break
                
    except KeyboardInterrupt:
        print("\n[SISTEMA] Encerrando por teclado...")
    finally:
        if server_conn:
            # Shutdown antes do close para liberar threads bloqueadas no recv 
            try: server_conn.shutdown(socket.SHUT_RDWR) 
            except: pass
            server_conn.close()
        if peer_socket:
            peer_socket.close()
        

if __name__ == "__main__":
    main()