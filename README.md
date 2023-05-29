```bash
                       ****************************************************************************
                           ___  _   __      ____ ____ __  ___ __  __ __    ___  ______ ____   ___ 
                          / _ )| | / /____ / __//  _//  |/  // / / // /   / _ |/_  __// __ \ / _ \
                         / _  || |/ //___/_\ \ _/ / / /|_/ // /_/ // /__ / __ | / /  / /_/ // , _/
                        /____/ |___/     /___//___//_/  /_/ \____//____//_/ |_|/_/   \____//_/|_| 

                       ****************************************************************************
```

# BV-Simulation - Algoritmo de Berkeley

   Este projeto é uma implementação do Algoritmo de Berkeley, um algoritmo que permite sincronizar diversos computadores em um sistema distribuído. Este projeto é particularmente focado em um sistema distribuído        responsável pelo controle de compra/venda de ações em uma bolsa de valores. Ele foi desenvolvido como parte dos requisitos necessários para aprovação na disciplina de CC7261 - Sistemas Distribuídos do curso de Ciência da  Computação do Centro Universitário FEI, orientado pelo Prof. Calebe de Paula Bianchini

***
## Descrição

   O sistema distribuído é responsável pelo controle de compra/venda de ações em uma bolsa de valores (BV). A BV detém uma lista de ações, a quantidade dessas ações disponíveis para compra/venda e o valor atual de cada ação. Todas as vezes que a quantidade ou o preço de uma ação é modificado, essas informações são propagadas para as instituições intermediárias e seus sistemas de home-brokers (HB). Os sistemas de HB são responsáveis pelo envio dos pedidos de compra/venda para a BV.

   Devido à implementação utilizando `docker-compose` e `dockerfiles` é possível escalar o sistema, adicionando quantos Homebrokers e Robôs desejar. A configuração Defaut inicia o ambiente com 1 Bolsa de Valores, 2 Homebrokers e 4 Robôs( 2 para cada Homebroker).

***
## Requisitos

   - Mínimo de 1 processo representando a BV
   - Mínimo de 2 processos de HB vinculados a BV
   - Mínimo de 2 robôs para cada HB existente
   - O relógio de cada processo, no início do seu funcionamento, deve ser recuperado do relógio do sistema
   - A cada ciclo de 10 segundos, o relógio local de cada processo deve ser modificado aleatoriamente em ±2s
***
## Tecnologias Utilizadas

   - Python
   - Docker

***
## Como Executar

   Siga estas etapas para executar este projeto:

1. **Conceder permissões**

   Após clonar o reposítorio utilizando o comando ` git clone https://github.com/akajhon/BV-Simulation/`, é necessário conceder permissões de execução ao script principal:

```
chmod +x ./simulation.sh
```

1. **Instalar o Docker**

   Primeiro, você precisa ter o Docker instalado em sua máquina. Se ainda não o instalou, você pode baixar o Docker [aqui](https://www.docker.com/products/docker-desktop) ou utilizar o parâmetro `requirements` junto ao script `simulation.sh`. O comando completo para esta tarefa é:

```
./simulation.sh requirements
```

2. **Construir as Imagens e Iniciar os Contêineres Docker**

   No diretório raiz do projeto, onde estão localizados os Dockerfiles e o docker-compose.yml, execute o comando abaixo para construir e iniciar as imagens Docker para a Bolsa de Valores, os Home Brokers e os Robôs.  Ao utilizar este parâmetro, os logs de execução serão exibidos em tempo real.

```
./simulation.sh start
```

4. **Verificar a Execução**

   Os logs de cada contêiner podem ser visualizados usando o comando `docker logs`. Porém, podemos usar o parâmetro `logs` junto ao script `simulation.sh` para visualizar as logs de todos os contâineres. Você pode usar:

```
./simulation.sh logs
```

5. **Parar a Execução**

   Para parar a execução de todos os contêineres e cancelar a simulação, você pode usar o comando:

```
./simulation.sh stop
```

   Note que todas estas etapas devem ser realizadas no terminal ou linha de comando e assumem que você está no diretório onde o docker-compose.yml e os Dockerfiles estão localizados.

***
## Autores
| <img src="https://avatars.githubusercontent.com/u/63318165?v=4" alt="Thales" width="150"/> | <img src="https://avatars.githubusercontent.com/u/69048604?v=4" alt="Joao" width="150"/> | <img src="https://avatars.githubusercontent.com/u/65295232?v=4" alt="Vitor" width="150"/> | <img src="https://avatars.githubusercontent.com/u/72151253?v=4" alt="Hugo" width="150"/> |
|:-------------------------------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------:|---------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| [Thales Oliveira Lacerda](https://github.com/LacThales)                                 | [João Pedro Rosa Cezarino](https://github.com/akajhon)                                      | [Vitor Martins Oliveira](https://github.com/vihmar)                                         | [Hugo Linhares Oliveira](https://github.com/hugolinhareso)                                       |
| R.A: 22.120.056-1                                                                          | R.A: 22.120.021-5                                                                           | R.A: 22.120.067-8                                                                           | R.A: 22.120.046-2                                                                          |
***

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE.md](LICENSE.md) para detalhes.
***
