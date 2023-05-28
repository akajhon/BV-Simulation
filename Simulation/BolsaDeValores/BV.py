import pika
import sys
import time
import logging
import random
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

class BolsaDeValores:
    def __init__(self, host='rabbitmq'):
        self.relogio = time.time()
        self.acoes = {
            "ACAO1": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0},
            "ACAO2": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0},
            "ACAO3": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0},
            "ACAO4": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0},
            "ACAO5": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0},
            "ACAO6": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0},
            "ACAO7": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0},
            "ACAO8": {'quantidade': random.randint(50, 100), 'valor': round(random.uniform(10.0, 100.0), 2), 'disponivel_para_venda': 0}
        }
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='exchange_bv', exchange_type='topic')
        self.channel.exchange_declare(exchange='exchange_hb', exchange_type='direct')
        self.channel.queue_declare(queue='bv_queue')
        self.channel.queue_bind(exchange='exchange_bv', queue='bv_queue', routing_key='bv')
        self.channel.basic_consume(queue='bv_queue', on_message_callback=self.handle_message, auto_ack=True)
        threading.Thread(target=self.start_consuming).start()

    def start_consuming(self):
        logger.info(AMARELO + f'[?] BV aguardando mensagens...' + RESET)
        self.channel.start_consuming()

    def enviar_acoes(self, hb_id):
        logger.info(ROXO + f'[*] Lista de ações enviada da BV ao {hb_id}' + RESET)
        self.channel.basic_publish(exchange='exchange_hb', routing_key=hb_id, body=f"Lista;{self.acoes}".encode('utf-8'))

    def handle_message(self, ch, method, properties, body):
        try:
            pedido = body.decode('utf-8')
            if "Sincronizar" in pedido:
                label, tempo_hb, hb_id = pedido.split(',')
                self.sincronizar_relogio(tempo_hb, hb_id)
            elif "Lista" in pedido:
                label, hb_id = pedido.split(',')
                self.enviar_acoes(hb_id)
            elif pedido:
                nome_acao, operacao, quantidade, relogio_hb, hb_id = pedido.split(',')
                quantidade = int(quantidade)
                relogio_hb = float(relogio_hb)
                hb_id = str(hb_id)
                if relogio_hb > self.relogio + 2 or relogio_hb < self.relogio - 2:
                    logger.info(CIANO + f'[$] Sincronizar enviado da BV ao {hb_id}' + RESET)
                    self.channel.basic_publish(exchange='exchange_hb', routing_key=hb_id, body=f"Sincronizar,{self.relogio}".encode('utf-8'))
                self.processar_pedido(nome_acao, operacao, quantidade, hb_id)
        except Exception as e:
            logger.info(VERMELHO + f'[!] ERRO: {e}' + RESET)

    def processar_pedido(self, nome_acao, operacao, quantidade, hb_id):
        try:
            if nome_acao not in self.acoes:
                return logger.info(VERMELHO + f'[!] A ação {nome_acao} não existe !' + RESET)
            if operacao not in ['compra', 'venda']:
                return logger.info(VERMELHO + f'[!] A operação {operacao} é inválida. As operações válidas são \'compra\' e \'venda\' !' + RESET)
            acao = self.acoes[nome_acao]
            if operacao == 'compra':
                if quantidade > acao['quantidade']:
                    return logger.info(VERMELHO + f"[!] A quantidade a ser comprada {quantidade} é maior do que a quantidade disponível {acao['quantidade']} para {nome_acao} !" + RESET)
                acao['quantidade'] -= quantidade
                acao['disponivel_para_venda'] += quantidade
                acao['valor'] = round(acao['valor'] * 1.01, 2)
            elif operacao == 'venda':
                if quantidade > acao['disponivel_para_venda']:
                    return logger.info(VERMELHO + f"[!] A quantidade a ser vendida {quantidade} é maior do que a quantidade disponível para venda {acao['disponivel_para_venda']} para {nome_acao} !" + RESET)
                acao['disponivel_para_venda'] -= quantidade
                acao['quantidade'] += quantidade
                acao['valor'] = round(acao['valor'] * 0.99, 2)
            logger.info(VERDE + f'[+] Pedido de {operacao} de {quantidade} {nome_acao}, realizado por {hb_id}, processado com sucesso!' + RESET)
        except Exception as e:
            logger.info(VERMELHO + f'[!] ERRO: {e}' + RESET)

    def atualizar_relogio(self):
        self.relogio += random.randint(-2, 2)

    def sincronizar_relogio(self, tempo_hb, hb_id):
        logger.info(CIANO + f'[$] Sincronizando com {hb_id}...' + RESET)
        logger.info(CIANO + f'[$] Tempo da BV (antes de sincronizar): {self.formata_relogio()}' + RESET)
        self.relogio = (self.relogio + float(tempo_hb)) / 2
        logger.info(CIANO + f'[$] Tempo da BV (após sincronizar): {self.formata_relogio()}' + RESET)
        logger.info(CIANO + f'[$] Finalizada sincronização com o {hb_id}!' + RESET)

    def formata_relogio(self):
        return time.strftime('%H:%M:%S', time.localtime(self.relogio))

if __name__ == "__main__":
    bv = BolsaDeValores()
    while True:
        time.sleep(10)
        bv.atualizar_relogio()