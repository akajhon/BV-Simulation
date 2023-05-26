import pika
import sys
import time
import logging
import random
import threading
from collections import defaultdict

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


class BolsaValores:
    def __init__(self, host='rabbitmq'):
        self.relogio = time.time()
        self.acoes = defaultdict(lambda: {'quantidade': 100, 'valor': 50.0})
        # self.acoes = {
        #     "ACAO1": {'quantidade': random.randint(50, 100), 'valor': random.uniform(10.0, 100.0)},
        #     "ACAO2": {'quantidade': random.randint(50, 100), 'valor': random.uniform(10.0, 100.0)},
        #     "ACAO3": {'quantidade': random.randint(50, 100), 'valor': random.uniform(10.0, 100.0)},
        #     "ACAO4": {'quantidade': random.randint(50, 100), 'valor': random.uniform(10.0, 100.0)},
        #     "ACAO5": {'quantidade': random.randint(50, 100), 'valor': random.uniform(10.0, 100.0)},
        #     "ACAO6": {'quantidade': random.randint(50, 100), 'valor': random.uniform(10.0, 100.0)},
        #     "ACAO7": {'quantidade': random.randint(50, 100), 'valor': random.uniform(10.0, 100.0)},
        #     "ACAO8": {'quantidade': random.randint(50, 100), 'valor': random.uniform(10.0, 100.0)}
        # }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        
        #  # Declarar a exchange de tópicos
        # self.channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

        # # Declarar as filas para cada HomeBroker
        # self.queues = ['hb1', 'hb2', 'hb3', 'hb4', 'hb5']
        # for queue in self.queues:
        #     self.channel.queue_declare(queue=queue)
        #     self.channel.queue_bind(exchange='topic_logs', queue=queue, routing_key=queue)
            
        self.channel.queue_declare(queue='bv')
        self.channel.queue_declare(queue='hb')
        self.channel.basic_consume(queue='bv', on_message_callback=self.handle_message, auto_ack=True)
        threading.Thread(target=self.start_consuming).start()
        
        # # Consumir mensagens de cada fila
        # for queue in self.queues:
        #     self.channel.basic_consume(queue=queue, on_message_callback=self.handle_message, auto_ack=True)

        # threading.Thread(target=self.start_consuming).start()
        # self.enviar_acoes()
        
        # def enviar_acoes(self):
        #     for nome_acao, acao in self.acoes.items():
        #         for queue in self.queues:
        #             self.channel.basic_publish(exchange='topic_logs', routing_key=queue, body=f"{nome_acao},{acao['quantidade']},{acao['valor']}".encode('utf-8'))

    def start_consuming(self):
        logger.info(AMARELO + f'[#] Aguardando mensagens...' + RESET)
        self.channel.start_consuming()

    def handle_message(self, ch, method, properties, body):
        try:
            pedido = body.decode('utf-8')
            if "Sincronizar" in pedido:
                label, tempo_hb = pedido.split(',')
                self.sincronizar_relogio(tempo_hb)
            elif pedido:
                nome_acao, operacao, quantidade, relogio_hb = pedido.split(',')
                quantidade = int(quantidade)
                relogio_hb = float(relogio_hb)
                if relogio_hb > self.relogio + 2 or relogio_hb < self.relogio - 2:
                    self.channel.basic_publish(exchange='', routing_key='hb', body=f"Sincronizar,{self.relogio}".encode('utf-8'))
                self.processar_pedido(nome_acao, operacao, quantidade)
                # self.channel.basic_publish(exchange='', routing_key='bv', body=f"{nome_acao},{operacao},{quantidade},{self.relogio}".encode('utf-8'))
        except Exception as e:
            logger.info(VERMELHO + f'[!] ERRO: {e} [!]' + RESET)

    def atualizar_relogio(self):
        self.relogio += random.randint(-2, 2)

    def processar_pedido(self, nome_acao, operacao, quantidade):
        try:
            acao = self.acoes[nome_acao]
            if operacao == 'compra':
                acao['quantidade'] += quantidade
                acao['valor'] *= 1.01
            elif operacao == 'venda':
                acao['quantidade'] -= quantidade
                acao['valor'] *= 0.99
            logger.info(VERDE + f'[+] Pedido de {operacao} de {quantidade} {nome_acao} processado com sucesso!' + RESET)
        except Exception as e:
            logger.info(VERMELHO + f'[!] ERRO: {e} [!]' + RESET)

    def sincronizar_relogio(self, tempo_hb):
        logger.info(AMARELO + f'[#] Tempo do BV (antes de sincronizar): {self.formata_relogio()}' + RESET)
        self.relogio = (self.relogio + float(tempo_hb)) / 2
        logger.info(AMARELO + f'[#] Tempo do BV (após sincronizar): {self.formata_relogio()}' + RESET)
        logger.info(AMARELO + '[#] Finalizada sincronização com HB' + RESET)

    def formata_relogio(self):
        return time.strftime('%H:%M:%S', time.localtime(self.relogio))


if __name__ == "__main__":
    bv = BolsaValores()
    while True:
        bv.atualizar_relogio()
        time.sleep(10)
