# Trabalho 1 INF 452 - *Sockets*

## O trabalho de Redes de Computadores busca fazer uma comunicação *Peer to Peer (P2P)* usando *Sockets*

> Veja em: [Especificação Trabalho](assets/trab_sockets.pdf)

---

### Temos a possibilidade de criar um servidor *Dummy* de teste
### E depois, podemos testá-lo num servidor real

---

## Tutorial

### Requisitos:
- `Python` 3.8+
- `Black` lib
  > `pip install black`

---

### *Dummy server*

#### Se quiser algo mais *plug-and-play*, rode o .sh `rodar_p2p.sh` que simula a comunicação usando um servidor *Dummy* entre 3 *peers*

Baixe `tmux` se ainda não tiver baixado:

```
sudo apt update       # atualiza pacotes do ubuntu
sudo apt install tmux # baixa tmux
```

Execute o .sh:

```
chmod +x rodar_p2p.sh # dar permissão para o .sh executar no seu pc
./rodar_p2p.sh        # executa o .sh
``` 

#### Ou faça na mão:

- Terminal 1:

Abre o servidor *Dummy* para ficar esperando conexões de outros *socket's* 

```
python cria_dummy_server.py
```

Espere algo assim:

`<aguardando conexão>`

- Terminal 2:

```
python peer.py
```

Digite o nome do seu usuário, após o *ENTER* é esperado do lado/terminal do *peer*:


`<inicia conexão TCP serv.>`

`USER fulano:50340`

`<cadastro usuário ativo>`

`<aguardando conexão>`

Já do lado do servidor:

`<conexão TCP realizada>`

`<cadastro usuário ativo>`

> Se quiser simular a comunicação com outra pessoa, o que é comum e recomendado, abra outro terminal e rode o `peer.py` novamente!

### Comandos possíveis de serem executados pelo usuário

`/chat <nome_usuario>`  -> Cria uma conexão p2p com usuário com nome <nome_usuario>

`/bye`                  -> Fecha a conexão p2p com usuário <nome_usuario>

`/list`                 -> Lista todos os usuários on-line no servidor

`/exit`                 -> Desconecta do servidor


---

### Servidor real

Aqui você precisará de um *IP*.

Para tal, basta trocar a varíavel `IP` pelo *IP* do servidor que deseja conectar bem como a porta que o hosteia e executar `peer.py`

### **Autores:** *Kayo de Melo Lage & Caio César Oliveira Cândido*
### **Matrículas:** 116211 | 116215

