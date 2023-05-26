import pika
import time
import random
import logging
import sys

# Cores
VERDE = '\033[92m'
VERMELHO = '\033[91m'
AMARELO = '\033[93m'
RESET = '\033[0m'

pika_logger = logging.getLogger('pika')
pika_logger.setLevel(logging.WARNING)
RB_logger = logging.getLogger('ROBO_01')
RB_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%H:%M:%S')
handler.setFormatter(formatter)
RB_logger.addHandler(handler)


class Robo:
    def __init__(self, host='rabbitmq'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='hb')

    def realizar_operacao(self):
        try:
            nome_acao = random.choice(['ACAO1', 'ACAO2', 'ACAO3'])
            operacao = random.choice(['compra', 'venda'])
            quantidade = random.randint(1, 10)
            pedido = f"{nome_acao},{operacao},{quantidade}"
            self.channel.basic_publish(exchange='', routing_key='hb', body=pedido.encode('utf-8'))
            RB_logger.info(VERDE + f"Pedido de {operacao} de {quantidade} {nome_acao} encaminhado ao HB com sucesso!" + RESET)
        except Exception as e:
            RB_logger.info(VERMELHO + f'[!] ERRO NO ROBO: {e} [!]' + RESET)


if __name__ == "__main__":
    robo = Robo()
    while True:
        robo.realizar_operacao()
        time.sleep(5)
