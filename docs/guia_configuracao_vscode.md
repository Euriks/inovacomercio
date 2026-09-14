Guia Definitivo: Configuração do VS Code e Instalação de Dependências (InovaComércio MS)

Este guia orienta passo a passo sobre como configurar o ambiente de desenvolvimento no Visual Studio Code (VS Code) no Windows (PowerShell) e instalar todas as bibliotecas necessárias para o ecossistema.

Passo 1: Abrir o Projeto no VS Code

Abra o VS Code.

No menu superior, clique em File > Open Folder... (Arquivo > Abrir Pasta...).

Selecione a pasta raiz do projeto: C:\Users\Euriks\Documents\inovacomercio.

Passo 2: Criar e Ativar o Ambiente Virtual (.venv)

O ambiente virtual isola as dependências do projeto do seu sistema operacional Python global.

Abra o terminal integrado no VS Code pressionando as teclas Ctrl + ~ (ou vá em Terminal > New Terminal).

Certifique-se de que o terminal está no diretório correto e execute o comando para criar o ambiente virtual:

python -m venv .venv


Ative o ambiente virtual no PowerShell:

.\.venv\Scripts\Activate.ps1


Nota: Se o PowerShell exibir um erro de permissão (Script Execution Policy), execute temporariamente:
Set-ExecutionPolicy Unrestricted -Scope Process e tente ativar novamente.

Passo 3: Selecionar o Interpretador Python no VS Code

Para que o Pylance (analisador de código do VS Code) reconheça todas as bibliotecas instaladas e elimine alertas de importação ausente:

Pressione Ctrl + Shift + P para abrir a Command Palette (Paleta de Comandos).

Digite e selecione: Python: Select Interpreter.

Escolha o interpretador localizado no seu ambiente virtual criado (.venv\Scripts\python.exe).

Passo 4: Instalar Todas as Dependências do Projeto

Com o ambiente virtual ativado ((.venv) visível no início da linha do terminal), instale os pacotes necessários:

Atualize o gerenciador de pacotes pip:

python -m pip install --upgrade pip


Instale as dependências da raiz / frontend:

pip install -r requirements.txt


Instale as dependências do backend Flask:

pip install -r backend/requirements.txt


Passo 5: Validar a Instalação

Para confirmar que tudo está funcionando corretamente e que não há erros de dependência, você pode rodar a verificação do Pytest:

pytest
