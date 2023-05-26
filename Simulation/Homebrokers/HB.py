import pika
import time
import sys
import logging
import random
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


class HomeBroker:
    def __init__(self, host='rabbitmq'):
        self.relogio = time.time()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='hb')
        self.channel.queue_declare(queue='bv')
        self.channel.basic_consume(queue='hb', on_message_callback=self.handle_message, auto_ack=True)
        threading.Thread(target=self.start_consuming).start()

    def start_consuming(self):
        logger.info(AMARELO + f'[#] Aguardando mensagens...' + RESET)
        self.channel.start_consuming()

    def handle_message(self, ch, method, properties, body):
        try:
            pedido = body.decode('utf-8')
            if "Sincronizar" in pedido:
                logger.info(AMARELO + '[#] Iniciando sincronização com BV' + RESET)
                label, tempo_bv = pedido.split(',')
                self.sincronizar_relogio(tempo_bv)
            elif pedido:
                nome_acao, operacao, quantidade = pedido.split(',')
                quantidade = int(quantidade)
                pedido_bv = f"{nome_acao},{operacao},{quantidade},{self.relogio}"
                self.channel.basic_publish(exchange='', routing_key='bv', body=pedido_bv.encode('utf-8'))
                logger.info(VERDE + f'[+] Pedido de {operacao} de {quantidade} {nome_acao} encaminhado ao BV com Sucesso!' + RESET)
        except Exception as e:
            logger.info(VERMELHO + f'[!] ERRO: {e}' + RESET)

    def atualizar_relogio(self):
        self.relogio += random.randint(-2, 2)

    def sincronizar_relogio(self, tempo_bv):
        self.channel.basic_publish(exchange='', routing_key='bv', body=f"Sincronizar,{self.relogio}".encode('utf-8'))
        logger.info(AMARELO + f'[#] Tempo do HB (antes de sincronizar): {self.formata_relogio()}' + RESET)
        self.relogio = (self.relogio + float(tempo_bv)) / 2
        logger.info(AMARELO + f'[#] Tempo do HB (após sincronizar): {self.formata_relogio()}' + RESET)

    def formata_relogio(self):
        return time.strftime('%H:%M:%S', time.localtime(self.relogio))


if __name__ == "__main__":
    hb = HomeBroker()
    while True:
        hb.atualizar_relogio()
        time.sleep(10)
