#!/bin/bash

# ------------------------------- FUNÇÕES ----------------------------------------- #
banner() {
cat << "EOF"
****************************************************************************
   ___  _   __      ____ ____ __  ___ __  __ __    ___  ______ ____   ___ 
  / _ )| | / /____ / __//  _//  |/  // / / // /   / _ |/_  __// __ \ / _ \
 / _  || |/ //___/_\ \ _/ / / /|_/ // /_/ // /__ / __ | / /  / /_/ // , _/
/____/ |___/     /___//___//_/  /_/ \____//____//_/ |_|/_/   \____//_/|_| 

****************************************************************************
EOF
}

start_services() {
  echo -e "\033[32m[!] Construindo e executando containers Docker... [!]\033[0m"

  sudo docker compose build

  if [ $? -ne 0 ]; then
    echo -e "\033[31m[!] A construção dos serviços falhou... [!]\033[0m"
    exit 1
  fi

  sudo docker compose up -d

  if [ $? -ne 0 ]; then
    echo -e "\033[31m[!] A execução dos serviços falhou... [!]\033[0m"
    exit 1
  fi

  echo -e "\033[32m[!] Todos os serviços foram construídos e estão em execução! [!]\033[0m"

  echo -e "\033[32m[!] Logs dos serviços em Execução: [!]\033[0m"

  sudo docker compose logs --tail=0 --follow
}

stop_services() {
  echo -e "\033[31m[!] Parando todos os serviços... [!]\033[0m"
  sudo docker compose down
}

view_logs(){
  echo -e "\033[32m[!] Logs dos serviços em Execução: [!]\033[0m"
  sudo docker compose logs
}

verify_docker() {
    docker --version > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        return 1
    fi

    docker compose --version > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        return 1
    fi

    return 0
}

install_requirements() {
    # Verifique se Docker e Docker Compose estão instalados
    verify_docker

    # Se eles não estiverem instalados, instale-os
    if [ $? -ne 0 ]; then
        echo -e "\033[31m[!] Docker ou Docker Compose não estão instalados. Instalando... [!]\033[0m"

        sudo apt-get update

        sudo apt-get install -y \
            apt-transport-https \
            ca-certificates \
            curl \
            gnupg \
            lsb-release

        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

        echo \
            "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io

        sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

        sudo chmod +x /usr/local/bin/docker-compose

        echo -e "\033[32m[!] Docker e Docker Compose instalados com sucesso. [!]\033[0m"
    fi
}

# ------------------------------- EXECUÇÃO ---------------------------------------- #
if [[ "$1" == "start" ]];
then
  banner
	start_services
	exit 0
elif [[ "$1" == "stop" ]];
then
  banner
	stop_services
	exit 0
elif [[ "$1" == "requirements" ]];
then
  banner
	install_requirements
  exit 0
elif [[ "$1" == "logs" ]];
then
  banner
	view_logs
  exit 0
else
	echo -e "\033[01;31m[!] Parâmetro Desconhecido [!]\033[0m"
	exit 1
fi