import pika
import time
import sys
import logging
import random
import threading

# Cores
VERDE = '\033[32m'
VERMELHO = '\033[31m'
AMARELO = '\033[33m'
MAGENTA = '\033[35m'
CIANO = '\033[36m'
RESET = '\033[0m'

pika_logger = logging.getLogger('pika')
pika_logger.setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
handler = logger.handlers[0]
handler.setFormatter(formatter)

class HomeBroker:
    def __init__(self, host='rabbitmq', hb_id=0):
        self.hb_id = hb_id
        self.robo_id = 'robo1'
        self.acoes = {}
        self.relogio = time.time()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='exchange_hb', exchange_type='direct')
        self.channel.exchange_declare(exchange='exchange_bv', exchange_type='topic')
        self.channel.exchange_declare(exchange='exchange_robos', exchange_type='topic')
        queue_name = f'hb{hb_id}'
        self.channel.queue_declare(queue=queue_name)
        self.channel.queue_bind(exchange='exchange_hb', queue=queue_name, routing_key=f'hb{hb_id}')
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.handle_message, auto_ack=True)
        threading.Thread(target=self.start_consuming).start()

    def start_consuming(self):
        logger.info(AMARELO + f'[...] HB{self.hb_id} aguardando mensagens...' + RESET)
        self.channel.start_consuming()

    def solicita_lista(self):
        logger.info(MAGENTA + f'[*] HB{self.hb_id} solicitando lista de ações a BV...' + RESET)
        pedido_bv = f"Lista,hb{self.hb_id}"
        self.channel.basic_publish(exchange='exchange_bv', routing_key='bv', body=pedido_bv.encode('utf-8'))

    def repassa_lista(self):
        lista_acoes = f"Lista;{self.acoes};hb{self.hb_id}"
        self.channel.basic_publish(exchange='exchange_robos', routing_key=self.robo_id, body=lista_acoes.encode('utf-8'))
        logger.info(MAGENTA + f'[*] Lista de ações enviada pelo HB{self.hb_id} ao {self.robo_id} !' + RESET)

    def handle_message(self, ch, method, properties, body):
        try:
            pedido = body.decode('utf-8')
            if "Lista" in pedido:
                logger.info(MAGENTA + f'[*] Lista de ações recebida da BV no HB{self.hb_id} !' + RESET)
                label, acoes = pedido.split(';')
                self.acoes = eval(acoes)
                self.repassa_lista()
            elif "LRobo" in pedido:
                label, robo_id = pedido.split(',')
                logger.info(MAGENTA + f'[*] {robo_id} solicitou a lista de ações .' + RESET)
                self.robo_id = robo_id
                self.solicita_lista()
            elif "Sincronizar" in pedido:
                logger.info(CIANO + '[#] Iniciando sincronização com a BV...' + RESET)
                label, tempo_bv = pedido.split(',')
                self.sincronizar_relogio(tempo_bv)
            elif pedido:
                nome_acao, operacao, quantidade, robo_id = pedido.split(',')
                quantidade = int(quantidade)
                pedido_bv = f"{nome_acao},{operacao},{quantidade},{self.relogio},hb{self.hb_id}"
                self.channel.basic_publish(exchange='exchange_bv', routing_key='bv', body=pedido_bv.encode('utf-8'))
                logger.info(VERDE + f'[$] Pedido de {operacao} de {quantidade} {nome_acao}, realizado por {robo_id}, encaminhado a BV com sucesso!' + RESET)
        except Exception as e:
            logger.info(VERMELHO + f'[!] Erro em \'handle_message\' no HB{self.hb_id}: {e}' + RESET)

    def atualizar_relogio(self):
        self.relogio += random.randint(-2, 2)

    def sincronizar_relogio(self, tempo_bv):
        self.channel.basic_publish(exchange='exchange_bv', routing_key='bv', body=f"Sincronizar,{self.relogio},hb{self.hb_id}".encode('utf-8'))
        logger.info(CIANO + f'[#] Tempo do HB{self.hb_id} (antes de sincronizar): {self.formata_relogio()}' + RESET)
        self.relogio = (self.relogio + float(tempo_bv)) / 2
        logger.info(CIANO + f'[#] Tempo do HB{self.hb_id} (após sincronizar): {self.formata_relogio()}' + RESET)

    def formata_relogio(self):
        return time.strftime('%H:%M:%S', time.localtime(self.relogio))

if __name__ == "__main__":
    hb_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    hb = HomeBroker(hb_id=hb_id)
    while True:
        time.sleep(10)
        hb.atualizar_relogio()