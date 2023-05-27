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
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
handler = logger.handlers[0]
handler.setFormatter(formatter)

class Robo:
    def __init__(self, hb_id='1', host='rabbitmq'):
            self.hb_id = hb_id
            self.relogio = time.time()
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
            self.channel = self.connection.channel()

            #  # Declare the exchange
            # self.channel.exchange_declare(exchange='exchange_robos', exchange_type='topic')

            # # Declare and bind the queue
            # queue_name = f'robo{hb_id}'
            # self.channel.queue_declare(queue=queue_name)
            # self.channel.queue_bind(exchange='exchange_robos', queue=queue_name, routing_key=f'robo{id}')

            # # Consume messages from the queue
            # self.channel.basic_consume(queue=queue_name, on_message_callback=self.handle_message, auto_ack=True)

            # Declarar a exchange de tópicos
            self.channel.exchange_declare(exchange='exchange_hb', exchange_type='direct')
            self.channel.queue_declare(queue=f'hb{hb_id}')

    def realizar_operacao(self):
        try:
            nome_acao = random.choice(['ACAO1', 'ACAO2', 'ACAO3'])
            operacao = random.choice(['compra', 'venda'])
            quantidade = random.randint(1, 10)
            pedido = f"{nome_acao},{operacao},{quantidade}"
            self.channel.basic_publish(exchange='exchange_hb', routing_key=f'hb{self.hb_id}', body=pedido.encode('utf-8'))
            logger.info(VERDE + f"[+] Pedido de {operacao} de {quantidade} {nome_acao} encaminhado ao HB com sucesso!" + RESET)
        except Exception as e:
            logger.info(VERMELHO + f'[!] ERRO NO ROBO: {e} [!]' + RESET)

if __name__ == "__main__":
    hb_id = sys.argv[1] if len(sys.argv) > 1 else '1'
    robo = Robo(hb_id=hb_id)
    while True:
        robo.realizar_operacao()
        time.sleep(5)