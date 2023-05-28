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
ROXO = '\033[95m'
CIANO = '\033[96m'
RESET = '\033[0m'

pika_logger = logging.getLogger('pika')
pika_logger.setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
handler = logger.handlers[0]
handler.setFormatter(formatter)

class Robo:
    def __init__(self, hb_id='1', robo_id='1', host='rabbitmq'):
        self.hb_id = hb_id
        self.robo_id = robo_id
        self.acoes = {}
        self.acoes_possuidas = {}
        self.recebeu_acoes = False
        self.conectado = False
        self.relogio = time.time()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='exchange_robos', exchange_type='topic')
        queue_name = f'robo{robo_id}'
        self.channel.queue_declare(queue=queue_name)
        self.channel.queue_bind(exchange='exchange_robos', queue=queue_name, routing_key=f'robo{robo_id}')
        self.channel.exchange_declare(exchange='exchange_hb', exchange_type='direct')
        self.channel.queue_declare(queue=f'hb{hb_id}')
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.handle_message, auto_ack=True)
        self.solicita_lista()
        threading.Thread(target=self.start_consuming).start()

    def start_consuming(self):
        logger.info(AMARELO + f'[?] robo{self.robo_id} aguardando mensagens...' + RESET)
        self.channel.start_consuming()

    def solicita_lista(self):
        logger.info(ROXO + f'[*] robo{self.robo_id} solicitando lista de ações ao hb{self.hb_id}...' + RESET)
        pedido_bv = f"LRobo,robo{self.robo_id}"
        self.channel.basic_publish(exchange='exchange_hb', routing_key=f'hb{self.hb_id}', body=pedido_bv.encode('utf-8'))

    def handle_message(self, ch, method, properties, body):
        try:
            pedido = body.decode('utf-8')
            if "Lista" in pedido:
                logger.info(ROXO + f'[*] Lista de ações recebida no robo{self.robo_id}!' + RESET)
                label, acoes, hb_id = pedido.split(';')
                self.acoes = eval(acoes)
                logger.info(ROXO + f'[*] Ações recebidas de {hb_id}:' + RESET)
                for acao, info in self.acoes.items():
                    logger.info(ROXO + f'{acao}: {info}'+ RESET)     
                self.recebeu_acoes = True
        except Exception as e:
            logger.info(VERMELHO + f'[!] ERRO: {e}' + RESET)

    def realizar_operacao(self):
        try:
            if self.recebeu_acoes == True and self.conectado == False:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
                self.channel = self.connection.channel()
                self.channel.exchange_declare(exchange='exchange_hb', exchange_type='direct')
                self.channel.queue_declare(queue=f'hb{self.hb_id}')
                self.conectado = True
            if len(self.acoes) > 0:
                nome_acao = random.choice(list(self.acoes.keys()))
                operacao = random.choice(['compra', 'venda'])
                quantidade_maxima_para_compra = self.acoes[nome_acao]['quantidade']
                quantidade_maxima_para_venda = self.acoes_possuidas.get(nome_acao, 0)
                if operacao == 'compra' and quantidade_maxima_para_compra > 0:
                    quantidade = random.randint(1, quantidade_maxima_para_compra)
                    self.acoes_possuidas[nome_acao] = self.acoes_possuidas.get(nome_acao, 0) + quantidade
                elif operacao == 'venda' and quantidade_maxima_para_venda > 0:
                    quantidade = random.randint(1, quantidade_maxima_para_venda)
                    self.acoes_possuidas[nome_acao] -= quantidade
                else:
                    return
                pedido = f"{nome_acao},{operacao},{quantidade},robo{self.robo_id}"
                self.channel.basic_publish(exchange='exchange_hb', routing_key=f'hb{self.hb_id}', body=pedido.encode('utf-8'))
                logger.info(VERDE + f"[+] Pedido de {operacao} de {quantidade} {nome_acao} encaminhado ao hb{self.hb_id} com sucesso!" + RESET)
                self.solicita_lista()
            # if len(self.acoes) > 0:
            #     nome_acao = random.choice(list(self.acoes.keys()))
            #     operacao = random.choice(['compra', 'venda'])
            #     quantidade = random.randint(1, self.acoes[nome_acao]['quantidade'])
            #     pedido = f"{nome_acao},{operacao},{quantidade},robo{self.robo_id}"
            #     self.channel.basic_publish(exchange='exchange_hb', routing_key=f'hb{self.hb_id}', body=pedido.encode('utf-8'))
            #     logger.info(VERDE + f"[+] Pedido de {operacao} de {quantidade} {nome_acao} encaminhado ao hb{self.hb_id} com sucesso!" + RESET)
            #     self.solicita_lista()
        except Exception as e:
            logger.info(VERMELHO + f'[!] ERRO: {e}' + RESET)

if __name__ == "__main__":
    hb_id = sys.argv[1] if len(sys.argv) > 1 else '1'
    robo_id = sys.argv[2] if len(sys.argv) > 2 else '1'
    robo = Robo(hb_id=hb_id, robo_id=robo_id)
    while True:
        time.sleep(5)
        robo.realizar_operacao()