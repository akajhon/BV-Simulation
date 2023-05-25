#!/bin/bash

handle_sigint() {
    echo -e "\033[32m[!] CTRL+C pressionado! Parando todos os serviços... [!]\033[0m"
    sudo docker-compose down
    exit
}

trap "handle_sigint" 2

cat << "EOF"
****************************************************************************
   ___  _   __      ____ ____ __  ___ __  __ __    ___  ______ ____   ___ 
  / _ )| | / /____ / __//  _//  |/  // / / // /   / _ |/_  __// __ \ / _ \
 / _  || |/ //___/_\ \ _/ / / /|_/ // /_/ // /__ / __ | / /  / /_/ // , _/
/____/ |___/     /___//___//_/  /_/ \____//____//_/ |_|/_/   \____//_/|_| 

****************************************************************************
EOF

echo -e "\033[32m[!] Construindo e executando containers Docker... [!]\033[0m"

sudo docker-compose build

if [ $? -ne 0 ]; then
  echo -e "\033[31m[!] A construção dos serviços falhou... [!]\033[0m"
  exit 1
fi

sudo docker-compose up -d

if [ $? -ne 0 ]; then
  echo -e "\033[31m[!] A execução dos serviços falhou... [!]\033[0m"
  exit 1
fi

echo -e "\033[32m[!] Todos os serviços foram construídos e estão em execução! [!]\033[0m"

echo -e "\033[32m[!] Logs dos serviços em Execução: [!]\033[0m"

sudo docker-compose logs --tail=0 --follow