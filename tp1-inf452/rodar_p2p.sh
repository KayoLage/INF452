#!/bin/bash

SESSION="p2p_chat"

# Inicia uma nova sessão e esconde a janela inicial (-d)
tmux new-session -d -s $SESSION

# Divisões para criar o grid 2x2
tmux split-window -h -t $SESSION          # Divide horizontalmente (Esquerda/Direita)
tmux select-pane -t 0
tmux split-window -v -t $SESSION          # Divide a esquerda verticalmente (Cima/Baixo)
tmux select-pane -t 2
tmux split-window -v -t $SESSION          # Divide a direita verticalmente (Cima/Baixo)

# --- Execução dos comandos em cada quadrante --- #

# Quadrante 0 (Superior Esquerdo): SERVIDOR
tmux send-keys -t $SESSION:0.0 "python3 cria_dummy_server.py" C-m

# Quadrante 1 (Inferior Esquerdo): PEER 1
tmux send-keys -t $SESSION:0.1 "python3 peer.py" C-m

# Quadrante 2 (Superior Direito): PEER 2
tmux send-keys -t $SESSION:0.2 "python3 peer.py" C-m

# Quadrante 3 (Inferior Direito): PEER 3
tmux send-keys -t $SESSION:0.3 "python3 peer.py" C-m

# Anexa à sessão para você começar a interagir
tmux attach-session -t $SESSION