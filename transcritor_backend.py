import os
import sys
import threading
import whisper
import re
import io
from datetime import datetime

class TranscritorBackend:
    def __init__(self):
        """Inicializa o backend do transcritor"""
        self.model = None
        self.model_name = None
        self.stop_transcription = False
        self.monitor_running = False
        self.download_progress_callback = None
        self.transcription_progress_callback = None
        self.transcription_complete_callback = None
        self.transcription_update_callback = None
        self.error_callback = None
        
        # Dicionário com descrições dos modelos
        self.model_descriptions = {
            "tiny": "Muito rápido, baixa precisão",
            "base": "Rápido, precisão moderada",
            "small": "Equilibrado entre velocidade e precisão",
            "medium": "Boa precisão, velocidade moderada",
            "large": "Alta precisão, mais lento"
        }
        
        # Dicionário com tamanhos aproximados dos modelos
        self.model_sizes = {
            "tiny": "75MB",
            "base": "140MB",
            "small": "460MB",
            "medium": "1.5GB",
            "large": "3GB"
        }
    
    def set_callbacks(self, download_progress=None, transcription_progress=None, 
                     transcription_complete=None, transcription_update=None, error=None):
        """Define callbacks para comunicação com o frontend"""
        self.download_progress_callback = download_progress
        self.transcription_progress_callback = transcription_progress
        self.transcription_complete_callback = transcription_complete
        self.transcription_update_callback = transcription_update
        self.error_callback = error
    
    def get_model_description(self, model_name):
        """Retorna a descrição de um modelo específico"""
        return self.model_descriptions.get(model_name, "")
    
    def get_model_size(self, model_name):
        """Retorna o tamanho aproximado de um modelo específico"""
        return self.model_sizes.get(model_name, "Desconhecido")
    
    def load_model(self, model_name):
        """Carrega um modelo Whisper"""
        self.model_name = model_name
        self.model = None
        
        print(f"Iniciando carregamento do modelo {model_name}")
        
        # Configurar monitoramento do download do modelo
        self._setup_download_monitor()
        
        try:
            # Carregar o modelo
            print(f"Chamando whisper.load_model({model_name})")
            self.model = whisper.load_model(model_name)
            print(f"Modelo {model_name} carregado com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao carregar modelo {model_name}: {e}")
            if self.error_callback:
                self.error_callback(f"Erro ao carregar modelo: {str(e)}")
            return False
    
    def _setup_download_monitor(self):
        """Configura o monitoramento do download do modelo"""
        if not self.download_progress_callback:
            print("Callback de progresso de download não configurado")
            return
            
        print(f"Configurando monitoramento de download para modelo {self.model_name}")
        
        # Thread para monitorar o progresso do download do modelo
        def monitor_download_progress():
            # Padrão para capturar a porcentagem de download
            pattern = re.compile(r'(\d+)%\|[█▒]+\| (\d+\.\d+)M/(\d+)M')
            alt_pattern = re.compile(r'(\d+)% \d+\.\d+M/(\d+\.\d+)M')
            
            # Simular progresso inicial para feedback imediato
            if self.download_progress_callback:
                self.download_progress_callback(1)
                print("Enviando progresso inicial de 1%")
            
            last_progress = 1
            check_count = 0
            max_checks = 600  # 5 minutos (600 * 0.5s)
            
            while last_progress < 100 and check_count < max_checks:
                check_count += 1
                found_progress = False
                
                # Verificar o terminal para o progresso de download
                try:
                    # Ler o arquivo de log mais recente na pasta temp
                    import glob
                    import os
                    temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp")
                    log_files = glob.glob(os.path.join(temp_dir, "*.log"))
                    
                    if log_files:
                        # Pegar os arquivos de log mais recentes (até 3)
                        recent_logs = sorted(log_files, key=os.path.getmtime, reverse=True)[:3]
                        
                        for log_file in recent_logs:
                            try:
                                # Ler as últimas linhas do arquivo
                                with open(log_file, 'r', errors='ignore') as f:
                                    # Ir para o final do arquivo e voltar algumas linhas
                                    f.seek(0, 2)
                                    file_size = f.tell()
                                    f.seek(max(0, file_size - 5000), 0)  # Ler os últimos 5000 bytes
                                    last_lines = f.read()
                                    
                                    # Procurar por padrões de progresso
                                    matches = pattern.findall(last_lines)
                                    if not matches:
                                        matches = alt_pattern.findall(last_lines)
                                    
                                    if matches:
                                        # Pegar o último match
                                        if len(matches[0]) >= 1:
                                            percent = int(matches[-1][0])
                                            
                                            if percent > last_progress:
                                                last_progress = percent
                                                # Atualizar a interface
                                                self.download_progress_callback(percent)
                                                print(f"Progresso de download detectado: {percent}%")
                                                found_progress = True
                                                break
                            except Exception as e:
                                print(f"Erro ao ler arquivo de log {log_file}: {e}")
                except Exception as e:
                    print(f"Erro ao monitorar progresso em logs: {e}")
                
                # Método alternativo: capturar diretamente da saída
                if not found_progress:
                    import sys
                    if hasattr(sys.stdout, 'getvalue'):
                        try:
                            output = sys.stdout.getvalue()
                            matches = pattern.findall(output)
                            if not matches:
                                matches = alt_pattern.findall(output)
                                
                            if matches:
                                percent = int(matches[-1][0])
                                
                                if percent > last_progress:
                                    last_progress = percent
                                    # Atualizar a interface
                                    self.download_progress_callback(percent)
                                    print(f"Progresso de download detectado na saída: {percent}%")
                                    found_progress = True
                        except Exception as e:
                            print(f"Erro ao capturar saída: {e}")
                
                # Se o modelo já estiver carregado, podemos parar o monitoramento
                if self.model is not None:
                    print("Modelo já carregado, finalizando monitoramento")
                    # Enviar 100% para completar a barra de progresso
                    self.download_progress_callback(100)
                    break
                
                # Se estamos há muito tempo sem encontrar progresso, simular progresso
                if not found_progress and check_count % 20 == 0 and last_progress < 95:
                    # A cada 10 segundos (20 * 0.5s), incrementar um pouco o progresso
                    # para dar feedback ao usuário
                    new_progress = min(95, last_progress + 5)
                    if new_progress > last_progress:
                        last_progress = new_progress
                        self.download_progress_callback(last_progress)
                        print(f"Simulando progresso: {last_progress}%")
                
                import time
                time.sleep(0.5)  # Verificar a cada meio segundo
            
            # Garantir que o progresso chegue a 100% no final
            if last_progress < 100 and self.model is not None:
                self.download_progress_callback(100)
                print("Finalizando progresso em 100%")
        
        # Iniciar thread de monitoramento
        download_monitor = threading.Thread(target=monitor_download_progress)
        download_monitor.daemon = True
        download_monitor.start()
        print("Thread de monitoramento de download iniciada")
    
    def transcribe(self, file_path, language=None, start_from_scratch=True):
        """Transcreve um arquivo de áudio"""
        if not os.path.exists(file_path):
            if self.error_callback:
                self.error_callback("O arquivo selecionado não existe.")
            return None
            
        if not self.model:
            if self.error_callback:
                self.error_callback("Nenhum modelo carregado. Carregue um modelo primeiro.")
            return None
            
        # Resetar flags
        self.stop_transcription = False
        self.monitor_running = True
        
        # Capturar a saída do Whisper usando um pipe
        buffer = io.StringIO()
        original_stdout = sys.stdout
        
        try:
            # Redirecionar a saída padrão para o buffer
            sys.stdout = buffer
            
            # Iniciar monitoramento em uma thread separada
            monitor_thread = threading.Thread(target=self._monitor_transcription_output, args=(buffer,))
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Transcrever áudio
            result = self.model.transcribe(
                file_path,
                language=language,
                verbose=True,  # Mostrar progresso no console
            )
            
            # Notificar que a transcrição foi concluída
            if self.transcription_complete_callback and not self.stop_transcription:
                self.transcription_complete_callback(result["text"])
                
            return result["text"] if not self.stop_transcription else None
            
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Erro na transcrição: {str(e)}")
            return None
        finally:
            # Restaurar a saída padrão
            sys.stdout = original_stdout
            # Parar a thread de monitoramento
            self.monitor_running = False
            monitor_thread.join(timeout=1.0)  # Esperar a thread terminar
    
    def _monitor_transcription_output(self, buffer):
        """Monitora a saída da transcrição e atualiza o progresso"""
        last_position = 0
        segment_count = 0
        total_segments_estimate = 100  # Estimativa inicial
        partial_transcription = ""
        
        while self.monitor_running and not self.stop_transcription:
            # Verificar se devemos parar
            if self.stop_transcription:
                break
                
            # Obter o conteúdo atual do buffer
            buffer.seek(0)
            content = buffer.read()
            
            # Verificar se há novos dados
            if len(content) > last_position:
                # Extrair apenas os novos dados
                new_content = content[last_position:]
                last_position = len(content)
                
                # Procurar por linhas de transcrição
                matches = re.findall(r'\[\d+:\d+\.\d+ --> \d+:\d+\.\d+\]\s+(.*)', new_content)
                if matches:
                    for match in matches:
                        # Adicionar o texto transcrito
                        if match.strip():
                            partial_transcription += " " + match.strip()
                            
                            # Notificar sobre a atualização da transcrição
                            if self.transcription_update_callback:
                                self.transcription_update_callback(partial_transcription)
                            
                            # Atualizar progresso
                            segment_count += 1
                            # Estimar o total de segmentos com base na duração do áudio
                            if "duration:" in content:
                                duration_match = re.search(r'duration:\s+(\d+\.\d+)', content)
                                if duration_match:
                                    duration = float(duration_match.group(1))
                                    # Estimar número total de segmentos (aproximadamente 1 segmento a cada 5 segundos)
                                    total_segments_estimate = max(20, int(duration / 5))
                            
                            # Calcular e atualizar o progresso
                            progress = min(0.99, segment_count / total_segments_estimate)
                            if self.transcription_progress_callback:
                                self.transcription_progress_callback(progress)
            
            # Verificar novamente se devemos parar
            if self.stop_transcription:
                break
                
            # Pequena pausa para não sobrecarregar a CPU
            import time
            time.sleep(0.1)
    
    def stop(self):
        """Para a transcrição em andamento"""
        self.stop_transcription = True
        self.monitor_running = False
