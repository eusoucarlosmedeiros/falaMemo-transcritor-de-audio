import os
import sys
import shutil
import whisper

def copy_whisper_assets():
    """Copia os arquivos de assets do Whisper para o diretório temporário correto"""
    print("Copiando arquivos de recursos do Whisper...")
    
    # Obter o caminho do módulo Whisper
    whisper_path = os.path.dirname(whisper.__file__)
    assets_path = os.path.join(whisper_path, "assets")
    
    # Verificar se o diretório de assets existe
    if not os.path.exists(assets_path):
        print(f"ERRO: Diretório de assets do Whisper não encontrado em {assets_path}")
        return False
    
    # Criar diretório temporário para os assets do Whisper
    temp_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'temp', 'whisper')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Copiar os arquivos de assets para o diretório temporário
    temp_assets_path = os.path.join(temp_dir, "assets")
    if os.path.exists(temp_assets_path):
        shutil.rmtree(temp_assets_path)
    
    try:
        shutil.copytree(assets_path, temp_assets_path)
        print(f"Assets copiados com sucesso para {temp_assets_path}")
        return True
    except Exception as e:
        print(f"ERRO ao copiar assets: {e}")
        return False

if __name__ == "__main__":
    success = copy_whisper_assets()
    if success:
        print("Arquivos de recursos do Whisper preparados com sucesso.")
        sys.exit(0)
    else:
        print("Falha ao preparar os arquivos de recursos do Whisper.")
        sys.exit(1)
