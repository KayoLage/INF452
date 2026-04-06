# Trabalho 1 INF 452 - Sockets

## O trabalho de Redes de Computadores busca fazer uma comunicação *Peer to Peer (P2P)* usando Sockets

> Veja em: [Especificação Trabalho](assets/trab_sockets.pdf)

---

### Temos a possibilidade de criar um servidor *dummy* de teste
### E depois, podemos testá-lo num servidor real

---

### Tutorial

#### Requisitos:
- `Python` 3.8+
- `Black` lib
  > `pip install black`

---

#### *Dummy server*

- Terminal 1:

Abre o servidor *Dummy* para ficar esperando conexões de outros *socket's* 

```
python cria_dummy_server.py
```

Espere algo assim:

`🤖 Servidor Dummy Central Online (Porta 10000)`

- Terminal 2:

```
python peer.py
```

Digite o nome do seu usuário, após o *ENTER* é esperado do lado do servidor:

`Cadastro: fulano em 127.0.0.1:53790`

> Se quiser simular a comunicação com outra pessoa, abra outro terminal e rode o `peer.py` novamente!

Os comandos estarão especificados nos *prints* de `peer.py`

---

#### Servidor real

Aqui você precisará de um *IP*, atribua-o em `OFFICIAL_IP` e no trecho:

```
# Conecta ao Servidor
ip_alvo = DUMMY_IP 
server_conn = conectar_servidor(ip_alvo, SERVER_PORT, nome, minha_porta)
```

basta trocar a variável `ip_alvo` de `DUMMY_IP` para `OFFICIAL_IP`

- **Autor:** *Kayo de Melo Lage*