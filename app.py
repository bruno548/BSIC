import os
import time
import datetime
import py7zr
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# ================= CONFIGURAÇÕES VIA ENV =================
PASTA_SISTEMA = os.getenv("PASTA_SISTEMA")
LETRA_PENDRIVE = os.getenv("LETRA_PENDRIVE")
PASTA_BACKUP_PENDRIVE = os.path.join(LETRA_PENDRIVE, "Backups_Sistema")
NOME_SISTEMA = os.getenv("NOME_SISTEMA")
SENHA_7Z = os.getenv("SENHA_7Z")

# Configurações do Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID_NOTIFICACAO = os.getenv("CHAT_ID_NOTIFICACAO")

# Arquivo de Log Local
ARQUIVO_LOG = os.getenv("ARQUIVO_LOG")
# =========================================================

def registrar_log(mensagem):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{timestamp}] {mensagem}\n"
    print(mensagem)
    
    # Garante que a pasta do log existe antes de gravar
    pasta_log = os.path.dirname(ARQUIVO_LOG)
    if pasta_log and not os.path.exists(pasta_log):
        os.makedirs(pasta_log)
        
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as log:
        log.write(linha)

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID_NOTIFICACAO, 
        "text": mensagem, 
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar notificação para o Telegram: {e}")

def realizar_backup():
    registrar_log("--- Iniciando Processo de Backup Diário (7z + Env) ---")
    
    # Validação básica de carga das variáveis
    if not all([PASTA_SISTEMA, LETRA_PENDRIVE, SENHA_7Z, TELEGRAM_TOKEN, CHAT_ID_NOTIFICACAO]):
        print("❌ ERRO: Uma ou mais variáveis de ambiente não foram carregadas do arquivo .env")
        return

    # 1. Checar presença do Pendrive
    if not os.path.exists(LETRA_PENDRIVE):
        erro = "❌ ERRO CRÍTICO: O Pendrive de backup não foi encontrado! Certifique-se de que ele está conectado."
        registrar_log(erro)
        enviar_telegram(erro)
        return

    if not os.path.exists(PASTA_BACKUP_PENDRIVE):
        os.makedirs(PASTA_BACKUP_PENDRIVE)

    data_atual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_7z = f"{NOME_SISTEMA}_{data_atual}.7z"
    caminho_7z_local = os.path.join(os.getcwd(), nome_7z)
    caminho_7z_pendrive = os.path.join(PASTA_BACKUP_PENDRIVE, nome_7z)

    try:
        # 2. Compactar e Criptografar Localmente com AES-256
        registrar_log("Compactando e aplicando criptografia AES-256...")
        
        # O py7zr já usa AES-256 por padrão quando recebe o argumento 'password'
        with py7zr.SevenZipFile(caminho_7z_local, 'w', password=SENHA_7Z) as archive:
            archive.writeall(PASTA_SISTEMA, arcname=os.path.basename(PASTA_SISTEMA))
        
        tamanho_original = os.path.getsize(caminho_7z_local)
        registrar_log(f"Arquivo local gerado com sucesso ({tamanho_original / (1024*1024):.2f} MB).")

        # 3. Transferir para o Pendrive
        registrar_log("Transmitindo arquivo para o destino físico...")
        with open(caminho_7z_local, 'rb') as f_in:
            with open(caminho_7z_pendrive, 'wb') as f_out:
                f_out.write(f_in.read())

        # Remover temporário local
        os.remove(caminho_7z_local)

        # 4. Checagem de Integridade
        registrar_log("Validando persistência dos dados no bloco de memória...")
        if not os.path.exists(caminho_7z_pendrive):
            raise FileNotFoundError("O arquivo de backup falhou ao ser persistido no pendrive.")
            
        tamanho_destino = os.path.getsize(caminho_7z_pendrive)
        if tamanho_original != tamanho_destino:
            raise ValueError(f"Quebra de integridade! Tamanho local ({tamanho_original} bytes) difere do pendrive ({tamanho_destino} bytes).")

        # 5. Rotação (Manter apenas as últimas 6 cópias)
        arquivos_no_pendrive = [
            os.path.join(PASTA_BACKUP_PENDRIVE, f) 
            for f in os.listdir(PASTA_BACKUP_PENDRIVE) 
            if f.startswith(NOME_SISTEMA) and f.endswith(".7z")
        ]
        arquivos_no_pendrive.sort(key=os.path.getmtime)

        while len(arquivos_no_pendrive) > 6:
            antigo = arquivos_no_pendrive.pop(0)
            registrar_log(f"Removendo backup excedente antigo: {os.path.basename(antigo)}")
            os.remove(antigo)

        # Sucesso
        msg_sucesso = (
            f"✅ *Backup Concluído com Sucesso!*\n"
            f"📅 Data/Hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"📦 Arquivo: `{nome_7z}`\n"
            f"💾 Tamanho: {tamanho_destino / (1024*1024):.2f} MB\n"
            f"🔒 Proteção: Criptografado (AES-256).\n"
            f"ℹ️ Status da Mídia: {len(arquivos_no_pendrive)}/6 cópias em disco."
        )
        registrar_log("Processo finalizado com êxito.")
        enviar_telegram(msg_sucesso)

    except Exception as e:
        erro_msg = f"💥 ERRO CRÍTICO NO BACKUP: {str(e)}"
        registrar_log(erro_msg)
        enviar_telegram(erro_msg)
        if os.path.exists(caminho_7z_local):
            os.remove(caminho_7z_local)

if __name__ == "__main__":
    realizar_backup()