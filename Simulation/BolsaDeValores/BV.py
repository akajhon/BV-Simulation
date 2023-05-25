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
BV_logger = logging.getLogger('BOLSADEVALORES')
BV_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%H:%M:%S')
handler.setFormatter(formatter)
BV_logger.addHandler(handler)

class BolsaValores:
    def __init__(self, host='rabbitmq'):
        self.relogio = time.time()
        self.acoes = defaultdict(lambda: {'quantidade': 100, 'valor': 50.0})
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='bv')
        self.channel.queue_declare(queue='hb')
        self.channel.basic_consume(queue='bv', on_message_callback=self.handle_message, auto_ack=True)
        threading.Thread(target=self.start_consuming).start()

    def start_consuming(self):
        BV_logger.info(AMARELO + f'[+] BolsadeValores aguardando mensagens. Para cancelar pressione CTRL+C' + RESET)
        self.channel.start_consuming()

    def handle_message(self, ch, method, properties, body):
        try:
            pedido = body.decode('utf-8')
            if pedido == "Sincronizar":
                BV_logger.info(AMARELO + f'[+] Pedido de Sincronização Recebido. Iniciando...' + RESET)
                self.channel.basic_publish(exchange='', routing_key='bv', body=f"{self.relogio}".encode('utf-8'))
                #pass
            elif pedido:
                nome_acao, operacao, quantidade, relogio_hb = pedido.split(',')
                quantidade = int(quantidade)
                relogio_hb = float(relogio_hb)
                if relogio_hb > self.relogio + 2 or relogio_hb < self.relogio - 2:
                    self.channel.basic_publish(exchange='', routing_key='bv', body="Sincronizar".encode('utf-8'))
                else:
                    self.processar_pedido(nome_acao, operacao, quantidade)
                    self.channel.basic_publish(exchange='', routing_key='bv', body=f"{nome_acao},{operacao},{quantidade},{self.relogio}".encode('utf-8'))
        except Exception as e:
            BV_logger.info(VERMELHO + f'[!] ERRO NO BV: {e} [!]' + RESET)

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
            BV_logger.info(VERDE + f'Pedido de {operacao} de {quantidade} {nome_acao} processado com sucesso!' + RESET)
        except Exception as e:
            BV_logger.info(VERMELHO + f'[!] ERRO NO BV: {e} [!]' + RESET)

if __name__ == "__main__":
    bv = BolsaValores()
    while True:
        bv.atualizar_relogio()
        time.sleep(5)