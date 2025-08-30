# HawkDB com Docker

HawkDB é um sistema de consulta e exportação de dados para bancos MySQL, empacotado com Docker para uma execução simples e multiplataforma. Este guia explica como configurar e rodar a aplicação facilmente.

## ⚠️ Aviso Importante Sobre Permissões (Linux)

Antes de executar, é crucial entender como o Docker salva arquivos no seu computador.

**O Problema:** A aplicação, rodando dentro do container, precisa de permissão para criar e modificar arquivos nas pastas locais `exports` (para salvar seus relatórios) e `data` (para salvar suas configurações de conexão).

**A Solução (Comando único):** Para evitar problemas, execute o seguinte comando **uma vez** para dar as permissões corretas a ambas as pastas.

```bash
sudo chmod -R 777 ./exports ./data
```

*Este comando garante que o container possa escrever nos diretórios, resolvendo 99% dos problemas de "arquivo não apareceu" e "configuração não foi salva".*

## 🚀 Início Rápido

### 1\. Estrutura de Arquivos

Verifique se seu projeto contém os seguintes arquivos:

```bash
hawkdb/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── hawkdb.py
├── run-hawkdb.sh
└── README.md
```

### 2\. Execução (Linux/macOS)

O script `run-hawkdb.sh` automatiza todo o processo.

```bash
# 1. Torna o script executável (apenas na primeira vez)
chmod +x run-hawkdb.sh

# 2. Inicia a aplicação
./run-hawkdb.sh run
```

### 3\. Execução (Windows ou Manual)

Se não puder usar o script, siga os passos manuais:

```bash
# 1. Habilita o acesso à interface gráfica (apenas Linux)
xhost +local:docker

# 2. Constrói a imagem e sobe o container
docker-compose up --build hawkdb
```

## 🛠️ Comandos Disponíveis via Script

O script `run-hawkdb.sh` simplifica a gestão dos containers.

| Comando | Descrição |
|---|---|
| `./run-hawkdb.sh run` | Executa o HawkDB (padrão). |
| `./run-hawkdb.sh build` | Força a reconstrução da imagem Docker. |
| `./run-hawkdb.sh mysql` | Inicia o HawkDB junto com um MySQL de teste. |
| `./run-hawkdb.sh stop` | Para **todos** os containers do projeto (incluindo MySQL). |
| `./run-hawkdb.sh clean` | **CUIDADO:** Remove containers, imagens e volumes. |
| `./run-hawkdb.sh logs` | Mostra os logs da aplicação em tempo real. |

## 🕵️ Acessando os Containers (Terminal)

Para depurar ou executar comandos diretamente dentro de um container em execução, você pode abrir um shell interativo.

**Pré-requisito:** Os containers devem estar rodando. Use `./run-hawkdb.sh run` ou `./run-hawkdb.sh mysql`.

### Acessando o Container da Aplicação (HawkDB)

Este comando te dará acesso ao ambiente onde o script Python está rodando.

```bash
docker exec -it hawkdb-app /bin/bash
```

### Acessando o Container do Banco de Dados (MySQL)

Útil para gerenciar o banco de dados diretamente via linha de comando.

1.  **Acessar o terminal do container:**
    ```bash
    docker exec -it hawkdb-mysql /bin/bash
    ```
2.  **Conectar ao MySQL com o cliente de linha de comando (já dentro do container):**
    ```bash
    mysql -u hawkdb -p
    ```
      - Ele pedirá a senha. Digite: `hawkdb123`
      - Você estará no console do MySQL, pronto para executar comandos SQL.

## 🖥️ Configuração da Interface Gráfica

Para que a interface gráfica da aplicação apareça, o Docker precisa se conectar ao "servidor de janelas" do seu sistema operacional.

### Linux (X11)

O script `run-hawkdb.sh` já executa `xhost +local:docker` para você. Se encontrar problemas, execute manualmente.

### Windows (WSL2 + VcXsrv)

1.  Instale um X Server para Windows, como o **VcXsrv**.
2.  Inicie o VcXsrv (o ícone aparecerá na bandeja do sistema).
3.  Configure a variável de ambiente `DISPLAY` no seu terminal WSL2 (adicione ao `~/.bashrc`):
    ```bash
    export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2; exit;}'):0.0
    ```

### macOS (XQuartz)

1.  Instale o **XQuartz**.
2.  Inicie o XQuartz.
3.  Configure a variável `DISPLAY` (adicione ao `~/.zshrc` ou `~/.bash_profile`):
    ```bash
    export DISPLAY=host.docker.internal:0
    ```

## 📊 MySQL de Teste (Opcional)

Para testar a aplicação com um banco de dados MySQL local e pré-configurado, use o perfil `mysql`.

```bash
# Inicia o HawkDB junto com o container do MySQL
./run-hawkdb.sh mysql
```

Use as seguintes credenciais para se conectar ao banco de teste a partir do HawkDB:

  - **Host:** `localhost:3307`
  - **User:** `hawkdb`
  - **Password:** `hawkdb123`
  - **Database:** `hawkdb_test`

## 💾 Persistência de Dados

Seus dados e configurações são salvos fora do container, na raiz do projeto, para que não se percam.

  - **`./exports/`**: Todos os arquivos exportados (CSV, Excel, SQL) aparecerão aqui.
  - **`./data/`**: Arquivos de configuração da aplicação (como conexões salvas) são guardados aqui.

## 🔧 Troubleshooting (Solução de Problemas)

### Arquivo exportado ou configurações não são salvos (Linux)

  - Este é o problema mais comum\! Refere-se à **permissão de arquivos** nas pastas `./exports` ou `./data`. Volte para a seção **"⚠️ Aviso Importante Sobre Permissões (Linux)"** no topo deste guia e execute o comando sugerido.

### Interface gráfica não aparece (Linux)

```bash
# 1. Reabilite o acesso ao X11
xhost +local:docker

# 2. Verifique se a variável DISPLAY está configurada
echo $DISPLAY

# 3. Reinicie os containers
./run-hawkdb.sh stop
./run-hawkdb.sh run
```

### Container não inicia ou fecha sozinho

```bash
# Verifique os logs para encontrar a causa do erro
./run-hawkdb.sh logs

# Se necessário, reconstrua a imagem do zero
./run-hawkdb.sh build
```

## 🧹 Limpeza e Gerenciamento do Ambiente

### Parando os Containers

Para parar a aplicação e também o container do MySQL (se estiver rodando), use o comando `stop`.

```bash
# Para todos os containers do projeto (HawkDB e MySQL)
./run-hawkdb.sh stop
```

*O script foi ajustado para garantir que o container do MySQL, mesmo sendo opcional, seja parado com este comando.*

### Remoção Completa (Limpeza Geral)

Se desejar remover completamente o ambiente, incluindo containers, redes, volumes de dados do MySQL e a imagem Docker, use o comando `clean`.

```bash
# CUIDADO: Esta ação não pode ser desfeita.
./run-hawkdb.sh clean
```

-----

**Simples, rápido e eficiente\! 🦅**
