#!/bin/bash

cat << "EOF"
****************************************************************************
   ___  _   __      ____ ____ __  ___ __  __ __    ___  ______ ____   ___ 
  / _ )| | / /____ / __//  _//  |/  // / / // /   / _ |/_  __// __ \ / _ \
 / _  || |/ //___/_\ \ _/ / / /|_/ // /_/ // /__ / __ | / /  / /_/ // , _/
/____/ |___/     /___//___//_/  /_/ \____//____//_/ |_|/_/   \____//_/|_| 

****************************************************************************
EOF

echo "\033[32m[!] Construindo e executando containers Docker... [!]\033[0m"

sudo docker-compose build

if [ $? -ne 0 ]; then
  echo "\033[31m[!] A construção dos serviços falhou... [!]\033[0m"
  exit 1
fi

sudo docker-compose up -d

if [ $? -ne 0 ]; then
  echo "\033[31m[!] A execução dos serviços falhou... [!]\033[0m"
  exit 1
fi

echo "\033[32m[!] Todos os serviços foram construídos e estão em execução! [!]\033[0m"

echo "\033[32m[!] Logs dos serviços em Execução: [!]\033[0m"

sudo docker-compose logs --tail=0 --follow