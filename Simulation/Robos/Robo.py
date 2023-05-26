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

# def __init__(self, hb_id, host='rabbitmq'):
#         self.hb_id = hb_id
#         self.relogio = time.time()
#         self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
#         self.channel = self.connection.channel()

#         # Declarar a exchange de tópicos
#         self.channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

#         self.channel.queue_declare(queue=f'robo{hb_id}')

#     def realizar_operacao(self):
#         # Restante do código
#         # Quando for publicar a mensagem, use o id do HomeBroker na chave de roteamento:
#         self.channel.basic_publish(exchange='topic_logs', routing_key=f'hb{self.hb_id}', body=pedido.encode('utf-8'))

#     Neste código, hb_id é o id do HomeBroker ao qual o robô está associado. 
#     O robô publica mensagens na exchange de tópicos com a chave de roteamento correspondente ao seu HomeBroker associado. 
#     Isso garante que a mensagem seja encaminhada para a fila correta.

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
            logger.info(VERDE + f"[+] Pedido de {operacao} de {quantidade} {nome_acao} encaminhado ao HB com sucesso!" + RESET)
        except Exception as e:
            logger.info(VERMELHO + f'[!] ERRO: {e} [!]' + RESET)


if __name__ == "__main__":
    robo = Robo()
    while True:
        robo.realizar_operacao()
        time.sleep(5)
