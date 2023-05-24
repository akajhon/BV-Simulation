# Projeto: Algoritmo de Berkeley

Este projeto é uma implementação do Algoritmo de Berkeley, um algoritmo que permite sincronizar diversos computadores em um sistema distribuído. Este projeto é particularmente focado em um sistema distribuído responsável pelo controle de compra/venda de ações em uma bolsa de valores.

***
## Descrição

O sistema distribuído é responsável pelo controle de compra/venda de ações em uma bolsa de valores (BV). A BV detém uma lista de ações, a quantidade dessas ações disponíveis para compra/venda e o valor atual de cada ação. Todas as vezes que a quantidade ou o preço de uma ação é modificado, essas informações são propagadas para as instituições intermediárias e seus sistemas de home-brokers (HB). Os sistemas de HB são responsáveis pelo envio dos pedidos de compra/venda para a BV.

***
## Requisitos

- Mínimo de 1 processo representando a BV
- Mínimo de 2 processos de HB vinculados a BV
- Mínimo de 2 robôs para cada HB existente
- O relógio de cada processo, no início do seu funcionamento, deve ser recuperado do relógio do sistema
- A cada ciclo de 10 segundos, o relógio local de cada processo deve ser modificado aleatoriamente em ±2s
- 
***
## Tecnologias Utilizadas

- Python
- Docker

***
## Como Executar

Instruções sobre como executar o projeto serão adicionadas aqui.

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
