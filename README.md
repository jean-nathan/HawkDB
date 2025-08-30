# HawkDB 🦅

**HawkDB** é um sistema de consulta e exportação de dados para bancos MySQL, projetado para ser simples, prático e multiplataforma. Com uma interface gráfica intuitiva, ele permite que usuários executem consultas SQL e exportem os resultados para múltiplos formatos, como **CSV**, **Excel (XLSX)** e **SQL INSERTs**.

O grande diferencial deste projeto é sua arquitetura 100% containerizada com **Docker**, o que garante uma configuração mínima e uma execução consistente em qualquer sistema operacional (Windows, macOS ou Linux).

*(Sugestão: tire um print da aplicação e substitua o link acima)*

-----

## ✨ Principais Funcionalidades

  - **Conexão Simplificada:** Interface clara para conectar-se a qualquer banco de dados MySQL.
  - **Gerenciador de Conexões:** Salve e gerencie múltiplas configurações de banco de dados para acesso rápido.
  - **Editor SQL:** Uma área de texto simples para escrever e executar suas consultas.
  - **Exportação Flexível:** Exporte os resultados das suas consultas para os formatos mais populares: `.csv`, `.xlsx` e `.sql`.
  - **Execução Multiplataforma:** Graças ao Docker, o HawkDB roda de forma idêntica no Windows, macOS e Linux.
  - **Ambiente Isolado:** Todas as dependências estão contidas no container Docker, mantendo seu sistema local limpo.

-----

## 🛠️ Tecnologias Utilizadas

  - **Backend & GUI:** Python 3.11 com a biblioteca Tkinter.
  - **Manipulação de Dados:** Pandas para uma exportação eficiente.
  - **Banco de Dados:** Conector oficial `mysql-connector-python`.
  - **Containerização:** Docker & Docker Compose.

-----

## 🚀 Como Executar

Este projeto foi desenhado para ser executado com Docker, eliminando a necessidade de instalar Python ou outras dependências manualmente no seu computador.

O guia completo de instalação, configuração e execução para **Windows, macOS e Linux** está detalhado em nosso guia específico para Docker.

### ➡️ **[Clique aqui para acessar o Guia de Configuração com Docker](./README-Docker.md)**

-----

## 📂 Estrutura do Repositório

Uma visão geral dos arquivos e diretórios mais importantes:

  - `hawkdb.py`: O código-fonte principal da aplicação, contendo toda a lógica e a interface gráfica.
  - `docker-compose.yml`: Arquivo que orquestra a construção e execução dos containers Docker.
  - `run-hawkdb.sh`: Script de conveniência para simplificar os comandos do Docker.
  - `README-Docker.md`: Instruções técnicas detalhadas para configurar e rodar o ambiente.
  - `data/`: Diretório (ignorado pelo Git) onde suas configurações de conexão salvas são armazenadas.
  - `exports/`: Diretório (ignorado pelo Git) onde os arquivos exportados pela aplicação são salvos.

-----

## 🤝 Contribuindo

Contribuições são sempre bem-vindas\! Se você tem ideias para novas funcionalidades, melhorias ou correções de bugs, sinta-se à vontade para:

1.  Fazer um "Fork" do repositório.
2.  Criar um novo "Branch" (`git checkout -b feature/minha-feature`).
3.  Fazer seus "Commits" (`git commit -m 'Adiciona minha feature'`).
4.  Enviar para o seu branch (`git push origin feature/minha-feature`).
5.  Abrir um "Pull Request".

-----

## 📄 Licença

Este projeto está licenciado sob a Licença MIT.

-----

Desenvolvido por **Jean Nathan**.
