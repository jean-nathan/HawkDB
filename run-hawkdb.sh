#!/bin/bash

# =============================================================================
# HawkDB - Script de execução simples e performático
# =============================================================================

set -e

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🦅 HawkDB - Sistema de Consulta${NC}"
echo -e "${BLUE}=============================${NC}"

# Função para mostrar ajuda
show_help() {
    echo -e "${GREEN}Uso: $0 [opção]${NC}"
    echo ""
    echo "Opções:"
    echo "  build     - Constrói a imagem Docker"
    echo "  run       - Executa o HawkDB (padrão)"
    echo "  mysql     - Inicia HawkDB + MySQL de teste"
    echo "  stop      - Para todos os containers do projeto (incluindo MySQL)"
    echo "  clean     - Remove containers e imagens"
    echo "  logs      - Mostra logs do container"
    echo "  help      - Mostra esta ajuda"
    echo ""
    echo -e "${YELLOW}Nota: Para usar a interface gráfica no Linux, execute:${NC}"
    echo -e "${YELLOW}xhost +local:docker${NC}"
}

# Verifica se Docker está rodando
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker não está rodando!${NC}"
        exit 1
    fi
}

# Configura X11 (Linux)
setup_x11() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo -e "${YELLOW}🔧 Configurando X11 forwarding...${NC}"
        xhost +local:docker >/dev/null 2>&1 || true
    fi
}

# Constrói a imagem
build_image() {
    echo -e "${GREEN}🔨 Construindo imagem HawkDB...${NC}"
    docker-compose build --no-cache
    echo -e "${GREEN}✅ Build concluído!${NC}"
}

# Executa o HawkDB
run_hawkdb() {
    echo -e "${GREEN}🚀 Iniciando HawkDB...${NC}"
    setup_x11
    
    # Cria diretórios se não existirem
    mkdir -p exports data
    
    docker-compose up hawkdb
}

# Executa com MySQL
run_with_mysql() {
    echo -e "${GREEN}🗄️ Iniciando HawkDB + MySQL...${NC}"
    setup_x11
    
    mkdir -p exports data
    
    docker-compose --profile mysql up -d mysql
    echo -e "${YELLOW}⏳ Aguardando MySQL inicializar...${NC}"
    sleep 10
    
    docker-compose up hawkdb
}

# Para containers
stop_containers() {
    echo -e "${YELLOW}🛑 Parando containers...${NC}"
    docker-compose --profile mysql down # <-- MUDANÇA AQUI: Adicionado --profile mysql
    echo -e "${GREEN}✅ Containers parados!${NC}"
}

# Limpeza completa
clean_all() {
    echo -e "${YELLOW}🧹 Removendo containers e imagens...${NC}"
    docker-compose --profile mysql down --rmi all --volumes --remove-orphans # <-- MUDANÇA AQUI: Adicionado --profile mysql
    docker system prune -f
    echo -e "${GREEN}✅ Limpeza concluída!${NC}"
}

# Mostra logs
show_logs() {
    docker-compose logs -f hawkdb
}

# Verifica argumentos
check_docker

case "${1:-run}" in
    "build")
        build_image
        ;;
    "run")
        run_hawkdb
        ;;
    "mysql")
        run_with_mysql
        ;;
    "stop")
        stop_containers
        ;;
    "clean")
        stop_containers
        clean_all
        ;;
    "logs")
        show_logs
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Opção inválida: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
