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
HB_logger = logging.getLogger('HOMEBROKER')
HB_logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%H:%M:%S')
handler.setFormatter(formatter)
HB_logger.addHandler(handler)


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
        HB_logger.info(AMARELO + f'[+] HomeBroker aguardando Mensagens. Para cancelar pressione CTRL+C [+]' + RESET)
        self.channel.start_consuming()

    def handle_message(self, ch, method, properties, body):
        try:
            pedido = body.decode('utf-8')
            if pedido == "Sicronizar":
                #pass
                HB_logger.info(AMARELO + '[+] Iniciando sincronização com ROBO [+]' + RESET)
                self.sincronizar_relogio()
            elif pedido:
                nome_acao, operacao, quantidade, timestamp = pedido.split(',')
                quantidade = int(quantidade)
                pedido_bv = f"{nome_acao},{operacao},{quantidade},{self.relogio}"
                self.channel.basic_publish(exchange='', routing_key='bv', body=pedido_bv.encode('utf-8'))
                resposta = self.channel.basic_get('bv')[2].decode('utf-8')
                if resposta == "Sincronizar":
                    HB_logger.info(AMARELO + '[+] Iniciando sincronização com BV [+]' + RESET)
                    self.sincronizar_relogio()
                else:
                    HB_logger.info(VERDE + f'Pedido de {operacao} de {quantidade} {nome_acao} encaminhado ao BV com Sucesso!' + RESET)
        except Exception as e:
            HB_logger.info(VERMELHO + f'[!] ERRO NO HB: {e} [!]' + RESET)

    def atualizar_relogio(self):
        self.relogio += random.randint(-2, 2)

    def sincronizar_relogio(self):
        self.relogio = time.time()
        self.channel.basic_publish(exchange='', routing_key='bv', body=str(self.relogio).encode('utf-8'))
        tempo_coordenador = float(self.channel.basic_get('bv')[2].decode('utf-8'))
        self.relogio = (self.relogio + tempo_coordenador) / 2

if __name__ == "__main__":
    hb = HomeBroker()
    while True:
        hb.atualizar_relogio()
        time.sleep(5)
