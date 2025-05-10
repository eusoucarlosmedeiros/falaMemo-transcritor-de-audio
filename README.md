# FalaMemo - Transcritor de Áudio

FalaMemo é uma aplicação para transcrição de áudio que utiliza o modelo Whisper da OpenAI. A aplicação permite transcrever arquivos de áudio em vários idiomas, com diferentes níveis de precisão.

## Recursos

- Diferentes modelos Whisper para escolher (tiny, base, small, medium, large)
- Suporte a múltiplos idiomas
- Exibição de transcrição em tempo real
- Capacidade de pausar e continuar transcrições
- Salvar transcrições em arquivo de texto

## Arquitetura do Projeto

O projeto segue uma arquitetura de separação entre frontend e backend:

- **main.py**: Ponto de entrada da aplicação
- **transcritor_frontend.py**: Interface gráfica usando CustomTkinter
- **transcritor_backend.py**: Lógica de transcrição usando Whisper
- **fix_whisper_assets.py**: Script auxiliar para lidar com recursos do Whisper
- **compile_completo.bat**: Script para compilar o executável

## Guia para Desenvolvedores

### Requisitos de Desenvolvimento

- Python 3.9+ (recomendado Python 3.10)
- Bibliotecas listadas em `requirements.txt`

### Configurando o Ambiente de Desenvolvimento

1. Clone o repositório:
   ```bash
   git clone https://github.com/eusoucarlosmedeiros/FalaMemo---Transcritor-de-Audio.git
   cd FalaMemo---Transcritor-de-Audio
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute a aplicação:
   ```bash
   python main.py
   ```

### Compilando o Executável

> **Nota**: O executável compilado não está incluído no repositório devido às limitações de tamanho do GitHub.

Para compilar o executável:

1. Certifique-se de que o ambiente virtual está ativado
2. Execute o script de compilação:
   ```bash
   # Windows
   compile_completo.bat
   ```

3. **Importante**: O script de compilação copia arquivos de recursos do Whisper do seu ambiente local. Se você encontrar erros relacionados a arquivos de recursos do Whisper (como `mel_filters.npz`), execute o script auxiliar antes da compilação:
   ```bash
   python fix_whisper_assets.py
   ```

4. O executável compilado estará disponível na pasta `dist`

### Solução de Problemas Comuns na Compilação

- **Erro "No such file or directory: whisper\assets\mel_filters.npz"**: Execute o script `fix_whisper_assets.py` para copiar os arquivos de recursos do Whisper para o local correto.

- **Erro "strip" durante a compilação**: Edite o arquivo `compile_completo.bat` e remova a opção `--strip` se ela estiver presente.

- **Executável não encontra recursos do Whisper**: Certifique-se de que a opção `--add-data="%WHISPER_PATH%\assets;whisper\assets"` está presente no script de compilação.

## Guia do Usuário

### Instalação

1. Baixe o arquivo `FalaMemo.exe` da página de releases
2. Execute o arquivo - não é necessário instalação

Na primeira execução, o programa baixará o modelo Whisper escolhido. Este download é feito apenas uma vez e o modelo ficará disponível offline para uso futuro.

### Como Usar

1. Abra o FalaMemo
2. Clique em "Selecionar Arquivo" e escolha um arquivo de áudio
3. Selecione o modelo Whisper desejado:
   - tiny: Muito rápido, baixa precisão
   - base: Rápido, precisão moderada
   - small: Equilibrado entre velocidade e precisão
   - medium: Boa precisão, velocidade moderada
   - large: Alta precisão, mais lento
4. Selecione o idioma (ou deixe em "auto" para detecção automática)
5. Clique em "Transcrever Áudio"
6. Aguarde a transcrição ser concluída
7. Use o botão "Salvar Transcrição" para salvar o resultado em um arquivo de texto

### Solução de Problemas

- **O programa não inicia**: Verifique se seu sistema atende aos requisitos mínimos
- **Erro ao transcrever**: Certifique-se de que o arquivo de áudio está em um formato suportado
- **Transcrição lenta**: Modelos maiores (medium, large) requerem mais recursos. Tente usar um modelo menor se seu computador for mais antigo.

---

Desenvolvido por [@eusoucarlosmedeiros](https://www.instagram.com/eusoucarlosmedeiros/) | WhatsApp: (41) 98459-5395
