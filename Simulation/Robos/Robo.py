import pika
import time
import random
import logging
import sys
import threading

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
        self.acoes = {}
        self.recebeu_acoes = False
        self.relogio = time.time()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='exchange_robos', exchange_type='topic')
        queue_name = f'robo{hb_id}'
        self.channel.queue_declare(queue=queue_name)
        self.channel.queue_bind(exchange='exchange_robos', queue=queue_name, routing_key=f'robo{hb_id}')
        self.channel.exchange_declare(exchange='exchange_hb', exchange_type='direct')
        self.channel.queue_declare(queue=f'hb{hb_id}')
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.handle_message, auto_ack=True)
        self.solicita_lista()
        threading.Thread(target=self.start_consuming).start()

    def realizar_operacao(self):
        try:
            if self.recebeu_acoes == True:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
                self.channel = self.connection.channel()
                self.channel.exchange_declare(exchange='exchange_hb', exchange_type='direct')
                self.channel.queue_declare(queue=f'hb{self.hb_id}')
            nome_acao = random.choice(['ACAO1', 'ACAO2', 'ACAO3'])
            operacao = random.choice(['compra', 'venda'])
            quantidade = random.randint(1, 10)
            pedido = f"{nome_acao},{operacao},{quantidade}"
            self.channel.basic_publish(exchange='exchange_hb', routing_key=f'hb{self.hb_id}', body=pedido.encode('utf-8'))
            logger.info(VERDE + f"[+] Pedido de {operacao} de {quantidade} {nome_acao} encaminhado ao HB com sucesso!" + RESET)
        except Exception as e:
            logger.info(VERMELHO + f'[!] ERRO NO ROBO1: {e} [!]' + RESET)

    def handle_message(self, ch, method, properties, body):
        try:
            logger.info(AMARELO + '[#] Pedido recebido no Robo!' + RESET)
            pedido = body.decode('utf-8')
            if "Lista" in pedido:
                logger.info(AMARELO + '[#] Lista de ações recebida no Robo!' + RESET)
                label, acoes, hb_id = pedido.split(';')
                logger.info(AMARELO + f'[#] {acoes} recebidas de {hb_id}' + RESET)
                self.acoes = eval(acoes)
                self.recebeu_acoes = True
        except Exception as e:
            logger.info(VERMELHO + f'[!] ERRO NO ROBO2: {e} [!]' + RESET)

    def start_consuming(self):
        logger.info(AMARELO + f'[#] ROBO Aguardando mensagens...' + RESET)
        self.channel.start_consuming()

    def solicita_lista(self):
        logger.info(AMARELO + f'[#] ROBO{self.hb_id} Solicitando Lista de Ações ao HB...' + RESET)
        pedido_bv = f"LRobo,robo{self.hb_id}"
        self.channel.basic_publish(exchange='exchange_hb', routing_key=f'hb{self.hb_id}', body=pedido_bv.encode('utf-8'))


if __name__ == "__main__":
    hb_id = sys.argv[1] if len(sys.argv) > 1 else '1'
    robo = Robo(hb_id=hb_id)
    while True:
        time.sleep(5)
        robo.realizar_operacao()
