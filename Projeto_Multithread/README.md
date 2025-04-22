# River Crossing Simulation

Este projeto simula o clássico problema de sincronização conhecido como **River Crossing** com threads representando dois tipos de personagens: **Hackers (Linux)** e **Serfs (Microsoft Employees)**.

O objetivo é transportar os personagens de um lado do rio para o outro obedecendo regras específicas de combinação a bordo e visualizando o processo com arte ASCII em terminal.


## Descrição do Problema

- Existem dois tipos de personagens: **Hackers** e **Serfs**.
- Um barco pode transportar **exatamente 4 pessoas** por vez.
- **Combinações permitidas**:
  - 4 Hackers
  - 4 Serfs
  - 2 Hackers + 2 Serfs
- Apenas **uma thread** entre as 4 embarcadas pode chamar a função `rowBoat()` (representando o **capitão**).
- A travessia é **unidirecional**.
- A função `board()` deve ser chamada por todas as 4 threads antes da próxima leva embarcar.


## Estrutura

### `rivercrossing.c`
- Código principal da simulação com múltiplas threads usando `pthread` e `semaphore`.
- Implementa lógica de formação de grupos válidos de tripulantes e sincronização de embarque/desembarque.
- Gera um log com eventos como:
  - Posição na fila
  - Embarque
  - Escolha do capitão
  - Travessia

### `visualizer.py`
- Visualizador interativo em ASCII do processo de travessia.
- Lê um log de execução (`log.txt` ou `exemplo_out.txt`) e anima a travessia no terminal.
- Representa personagens com:
  - Hackers: `(^.^)`
  - Serfs: `(◣_◢)`
  - Barco animado com ícones de capitão e diferentes estilos conforme a composição da tripulação.


## Uso

1. Compile o programa em C:

```bash
gcc -pthread rivercrossing.c -o rivercrossing 
```

- Se quiser evitar os *warnings*:

```bash
gcc -pthread rivercrossing.c -o rivercrossing -Wno-pointer-to-int-cast -Wno-int-to-pointer-cast
```

2. Execute o programa e redirecione a saída para um arquivo de log:

```bash
./rivercrossing > log.txt
```

3. Execute o visualizador:

```bash
python3 visualizer.py
```