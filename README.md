# BSIC - Backup de Sistema com Integração em Nuvem (py7zr + Telegram)

O **BSIC** é um script de automação em Python projetado para realizar cópias de segurança (backups) compactadas de bancos de dados locais de forma segura, monitorada e resiliente. Desenvolvido inicialmente para cenários de automação comercial (como sistemas Delphi), o projeto se destaca por isolar completamente as credenciais de acesso e caminhos de diretórios através de variáveis de ambiente, além de emitir relatórios de status em tempo real via Telegram.

## Funcionalidades

*   **Compactação Eficiente:** Utiliza o formato `.7z` (via biblioteca `py7zr`) para garantir alta taxa de compressão e integridade dos arquivos.
*   **Segurança Estrita:** Zero credenciais expostas no código. Toda a configuração sensível reside em um arquivo local `.env` ignorado pelo Git.
*   **Alertas Instantâneos:** Envio de notificações automáticas para o seu celular/bot do Telegram informando o sucesso ou falhas críticas detalhadas (como pendrive desconectado ou falta de espaço).
*   **Logs Locais:** Registro detalhado de atividades (`backup_log.txt`) para auditoria interna, ideal para manutenção preventiva e checagem offline.

## Pré-requisitos

Antes de iniciar, certifique-se de ter instalado em sua máquina:
*   [Python 3.8 ou superior](https://www.python.org/)
*   Um token de Bot do Telegram (gerado via `@BotFather`) e o seu `Chat ID`.

## Configuração e Instalação

### 1. Clonar ou Baixar o Projeto
Clone o repositório ou baixe o arquivo `.zip` diretamente do GitHub e extraia na pasta de sua preferência (ex: `C:\Scripts\BSIC`).

### 2. Configurar o Ambiente Virtual (venv)
Navegue até a pasta raiz do projeto através do terminal/prompt e execute os comandos abaixo para isolar as dependências:

```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente virtual (Windows)
.\venv\Scripts\activate

# Instalar as dependências necessárias
pip install -r requirements.txt

Crie um arquivo chamado .env exatamente na raiz do projeto (onde o arquivo app.py reside) e configure as variáveis de acordo com o seu cenário:
# Configurações do Telegram
TELEGRAM_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui

# Caminhos do Sistema
DIRETORIO_ORIGEM=C:\Caminho\Para\BancoDeDados\Delphi
DIRETORIO_DESTINO=E:\Backup_Pendrive