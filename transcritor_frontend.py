import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from datetime import datetime
from transcritor_backend import TranscritorBackend

class TranscritorFrontend:
    def __init__(self, root):
        """Inicializa a interface do usuário do transcritor"""
        self.root = root
        
        # Configurar tema do customtkinter
        ctk.set_appearance_mode("system")  # Modo de aparência baseado no sistema (dark/light)
        ctk.set_default_color_theme("blue")  # Tema de cor padrão
        
        self.root.title("FalaMemo - Transcritor de Áudio")
        self.root.geometry("900x650")
        self.root.minsize(900, 650)
        
        # Inicializar backend
        self.backend = TranscritorBackend()
        
        # Configurar callbacks do backend
        self.backend.set_callbacks(
            download_progress=self.update_download_progress,
            transcription_progress=self.update_progress,
            transcription_complete=self.update_transcription_complete,
            transcription_update=self.update_partial_transcription,
            error=self.show_error
        )
        
        # Variáveis de controle
        self.transcription_thread = None
        self.transcription_paused = False
        self.current_file_path = None
        self.partial_transcription = ""
        self.transcription = None
        self.is_downloading = False
        self.is_transcribing = False
        
        # Configurar a interface
        self.setup_ui()
    

    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Título
        title_label = ctk.CTkLabel(main_frame, text="FalaMemo - Transcritor de Áudio", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=10)
        
        # Frame para seleção de arquivo
        self._setup_file_frame(main_frame)
        
        # Frame para opções de modelo
        self._setup_model_frame(main_frame)
        
        # Frame para botões de ação
        self._setup_action_frame(main_frame)
        
        # Frame para progresso
        self._setup_progress_frame(main_frame)
        
        # Frame para resultados
        self._setup_results_frame(main_frame)
    
    def _setup_file_frame(self, parent):
        """Configura o frame de seleção de arquivo"""
        file_frame = ctk.CTkFrame(parent)
        file_frame.pack(fill=tk.X, pady=10)
        
        file_label = ctk.CTkLabel(file_frame, text="Seleção de Arquivo", font=ctk.CTkFont(size=16, weight="bold"))
        file_label.pack(anchor="w", padx=10, pady=5)
        
        file_content_frame = ctk.CTkFrame(file_frame)
        file_content_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.file_path_var = tk.StringVar()
        ctk.CTkLabel(file_content_frame, text="Arquivo de Áudio:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_entry = ctk.CTkEntry(file_content_frame, textvariable=self.file_path_var, width=400)
        self.file_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        ctk.CTkButton(file_content_frame, text="Selecionar Arquivo", command=self.select_file).grid(row=0, column=2, padx=5, pady=5)
    
    def _setup_model_frame(self, parent):
        """Configura o frame de opções de modelo"""
        model_frame = ctk.CTkFrame(parent)
        model_frame.pack(fill=tk.X, pady=10)
        
        model_label = ctk.CTkLabel(model_frame, text="Opções de Modelo", font=ctk.CTkFont(size=16, weight="bold"))
        model_label.pack(anchor="w", padx=10, pady=5)
        
        # Opções de modelo
        options_frame = ctk.CTkFrame(model_frame)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Primeira linha de opções
        ctk.CTkLabel(options_frame, text="Modelo Whisper:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.model_var = tk.StringVar(value="base")
        model_options = ["tiny", "base", "small", "medium", "large"]
        
        # Função para mostrar descrição do modelo
        def update_model_description(*args):
            selected_model = self.model_var.get()
            description = self.backend.get_model_description(selected_model)
            self.model_description_label.configure(text=description)
            
            # Resetar o estado de pausa se o modelo for alterado
            if self.transcription_paused:
                self.transcription_paused = False
                self.transcribe_button.configure(text="Transcrever Áudio")
                if hasattr(self, 'continue_button'):
                    self.continue_button.grid_forget()
                self.stop_button.grid(row=0, column=1, padx=10)
        
        # Dropdown com os modelos
        model_dropdown = ctk.CTkOptionMenu(
            options_frame, 
            values=model_options, 
            variable=self.model_var,
            command=update_model_description
        )
        model_dropdown.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Label para descrição do modelo
        self.model_description_label = ctk.CTkLabel(
            options_frame, 
            text=self.backend.get_model_description("base"),
            font=ctk.CTkFont(size=11, slant="italic")
        )
        self.model_description_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        ctk.CTkLabel(options_frame, text="Idioma").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.language_var = tk.StringVar(value="pt")
        language_options = ["auto", "pt", "en", "es", "fr", "de", "it", "ja", "zh", "ru"]
        language_dropdown = ctk.CTkOptionMenu(options_frame, values=language_options, variable=self.language_var)
        language_dropdown.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Descrição do idioma
        language_description_label = ctk.CTkLabel(
            options_frame, 
            text="Idioma de transcrição",
            font=ctk.CTkFont(size=11, slant="italic")
        )
        language_description_label.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
    
    def _setup_action_frame(self, parent):
        """Configura o frame de botões de ação"""
        action_frame = ctk.CTkFrame(parent)
        action_frame.pack(fill=tk.X, pady=10)
        
        button_frame = ctk.CTkFrame(action_frame)
        button_frame.pack(pady=10)
        
        self.transcribe_button = ctk.CTkButton(
            button_frame, 
            text="Transcrever Áudio", 
            command=self.start_transcription, 
            width=150,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.transcribe_button.grid(row=0, column=0, padx=10)
        
        self.stop_button = ctk.CTkButton(
            button_frame, 
            text="Parar Transcrição", 
            command=self.stop_transcription, 
            width=150,
            height=35,
            state="disabled",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.stop_button.grid(row=0, column=1, padx=10)
        
        self.continue_button = ctk.CTkButton(
            button_frame,
            text="Continuar Transcrição",
            command=self.continue_transcription,
            width=150,
            height=35,
            state="disabled",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        # Não adicionar ao grid inicialmente
        
        self.save_button = ctk.CTkButton(
            button_frame, 
            text="Salvar Transcrição", 
            command=self.save_results, 
            width=150,
            height=35,
            state="disabled",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.save_button.grid(row=0, column=2, padx=10)
    
    def _setup_progress_frame(self, parent):
        """Configura o frame de progresso"""
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.pack(fill=tk.X, pady=10)
        
        # Barra de progresso com percentual
        progress_container = ctk.CTkFrame(progress_frame)
        progress_container.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(progress_container)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.progress_bar.set(0)  # Inicializa com 0%
        
        self.progress_percent_label = ctk.CTkLabel(progress_container, text="0%", width=50)
        self.progress_percent_label.pack(side=tk.RIGHT)
        
        self.status_var = tk.StringVar(value="Pronto para iniciar")
        status_label = ctk.CTkLabel(progress_frame, textvariable=self.status_var)
        status_label.pack(fill=tk.X, pady=5)
    
    def _setup_results_frame(self, parent):
        """Configura o frame de resultados"""
        results_frame = ctk.CTkFrame(parent)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        results_label = ctk.CTkLabel(results_frame, text="Transcrição", font=ctk.CTkFont(size=16, weight="bold"))
        results_label.pack(anchor="w", padx=10, pady=5)
        
        # Usando CTkTextbox para a área de transcrição (somente leitura)
        self.transcription_text = ctk.CTkTextbox(results_frame, wrap="word", font=ctk.CTkFont(size=13))
        self.transcription_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        # Tornar o campo somente leitura
        self.transcription_text.configure(state="disabled")
    

    
    def select_file(self):
        """Abre um diálogo para selecionar um arquivo de áudio"""
        file_path = filedialog.askopenfilename(
            title="Selecione um arquivo de áudio",
            filetypes=[
                ("Arquivos de Áudio", "*.mp3 *.wav *.flac *.m4a *.ogg"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.transcribe_button.configure(state="normal")
    
    def start_transcription(self):
        """Inicia o processo de transcrição"""
        file_path = self.file_path_var.get()
        
        # Se estiver continuando uma transcrição pausada
        if self.transcription_paused and self.current_file_path == file_path:
            self.continue_transcription()
            return
            
        # Caso contrário, iniciar uma nova transcrição
        if not file_path:
            messagebox.showerror("Erro", "Por favor, selecione um arquivo de áudio.")
            return
        
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            messagebox.showerror("Erro", "O arquivo selecionado não existe.")
            return
        
        # Armazenar o caminho do arquivo atual
        self.current_file_path = file_path
        
        # Limpar transcrição anterior
        self.transcription_text.configure(state="normal")
        self.transcription_text.delete("0.0", "end")
        self.transcription_text.configure(state="disabled")
        self.partial_transcription = ""
        self.transcription = None
        self.transcription_paused = False
        
        # Atualizar interface
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        self.status_var.set("Carregando modelo... (isso pode levar alguns minutos)")
        self.transcribe_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.save_button.configure(state="disabled")
        
        # Iniciar transcrição em uma thread separada
        self.transcription_thread = threading.Thread(target=self._transcribe_thread, args=(file_path,))
        self.transcription_thread.daemon = True
        self.transcription_thread.start()
    
    def _transcribe_thread(self, file_path):
        """Thread para executar a transcrição"""
        try:
            # Carregar modelo
            model_name = self.model_var.get()
            self.root.after(0, lambda: self.status_var.set(f"Carregando modelo {model_name}..."))
            
            # Mostrar mensagem de download na área de transcrição antes de carregar o modelo
            self.root.after(0, lambda: self.show_model_info(model_name))
            
            if not self.backend.load_model(model_name):
                self.root.after(0, lambda: self.show_error("Erro ao carregar o modelo."))
                self.root.after(0, self.reset_ui)
                return
            
            # Definir idioma
            language = None if self.language_var.get() == "auto" else self.language_var.get()
            
            # Atualizar status
            self.root.after(0, lambda: self.status_var.set("Transcrevendo áudio..."))
            self.root.after(0, lambda: self.configure_progress_bar_determinate())
            
            # Transcrever áudio
            result = self.backend.transcribe(file_path, language, start_from_scratch=True)
            
            # Verificar se a transcrição foi interrompida
            if self.backend.stop_transcription:
                self.root.after(0, lambda: self.status_var.set("Transcrição interrompida"))
                self.root.after(0, self.reset_ui)
                return
            
            # Atualizar UI com resultado final
            self.transcription = result
            self.root.after(0, self.update_transcription_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Erro na transcrição: {str(e)}"))
        finally:
            self.root.after(0, self.reset_ui)
    
    def continue_transcription(self):
        """Continua a transcrição de onde parou"""
        if not self.current_file_path:
            messagebox.showerror("Erro", "Nenhum arquivo para continuar a transcrição.")
            return
        
        # Esconder botão continuar e mostrar botão parar
        self.continue_button.grid_forget()
        self.stop_button.grid(row=0, column=1, padx=10)
        self.stop_button.configure(state="normal")
        
        # Atualizar estado
        self.transcription_paused = False
        self.backend.stop_transcription = False
        
        # Atualizar interface
        self.status_var.set("Continuando transcrição...")
        self.transcribe_button.configure(state="disabled")
        
        # Iniciar transcrição em uma thread separada
        self.transcription_thread = threading.Thread(target=self._continue_thread, args=(self.current_file_path,))
        self.transcription_thread.daemon = True
        self.transcription_thread.start()
    
    def _continue_thread(self, file_path):
        """Thread para continuar a transcrição"""
        try:
            # Carregar modelo se necessário
            model_name = self.model_var.get()
            if not self.backend.model or self.backend.model_name != model_name:
                self.root.after(0, lambda: self.status_var.set(f"Carregando modelo {model_name}..."))
                self.root.after(0, lambda: self.show_model_info(model_name))
                
                if not self.backend.load_model(model_name):
                    self.root.after(0, lambda: self.show_error("Erro ao carregar o modelo."))
                    self.root.after(0, self.reset_ui)
                    return
            
            # Definir idioma
            language = None if self.language_var.get() == "auto" else self.language_var.get()
            
            # Atualizar status
            self.root.after(0, lambda: self.status_var.set("Continuando transcrição..."))
            self.root.after(0, lambda: self.configure_progress_bar_determinate())
            
            # Transcrever áudio (continuando de onde parou)
            result = self.backend.transcribe(file_path, language, start_from_scratch=False)
            
            # Verificar se a transcrição foi interrompida
            if self.backend.stop_transcription:
                self.root.after(0, lambda: self.status_var.set("Transcrição interrompida"))
                self.root.after(0, self.reset_ui)
                return
            
            # Atualizar UI com resultado final
            self.transcription = result
            self.root.after(0, self.update_transcription_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Erro na transcrição: {str(e)}"))
        finally:
            self.root.after(0, self.reset_ui)
    
    def stop_transcription(self):
        """Para a transcrição em andamento"""
        # Parar o backend
        self.backend.stop()
        
        # Marcar como pausado
        self.transcription_paused = True
        
        # Atualizar interface
        self.status_var.set("Transcrição interrompida")
        
        # Habilitar o botão de salvar se houver transcrição parcial
        if self.partial_transcription:
            self.save_button.configure(state="normal")
            
            # Alternar botões: esconder Parar e mostrar Continuar na mesma posição
            self.stop_button.grid_forget()
            self.continue_button.grid(row=0, column=1, padx=10)
            self.continue_button.configure(state="normal")
        
        self.transcribe_button.configure(text="Transcrever Áudio", state="normal")
        
        # Resetar a barra de progresso
        self.reset_progress_bar()
    
    def reset_ui(self):
        """Reseta a interface após uma transcrição"""
        self.transcribe_button.configure(text="Transcrever Áudio", state="normal")
        
        if self.transcription_paused and self.partial_transcription:
            # Se pausado e com transcrição parcial, mostrar botão continuar
            self.stop_button.grid_forget()
            self.continue_button.grid(row=0, column=1, padx=10)
            self.continue_button.configure(state="normal")
        else:
            # Caso contrário, mostrar botão parar (desabilitado)
            self.stop_button.configure(state="disabled")
            if hasattr(self, 'continue_button'):
                self.continue_button.grid_forget()
        
        # Resetar a barra de progresso
        self.reset_progress_bar()
    
    def reset_progress_bar(self):
        """Reseta a barra de progresso"""
        self.progress_bar.stop()
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.set(0)
        self.progress_percent_label.configure(text="0%")
    
    def configure_progress_bar_determinate(self):
        """Configura a barra de progresso para modo determinado"""
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)
    
    def configure_progress_bar_indeterminate(self):
        """Configura a barra de progresso para modo indeterminado"""
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
    
    def update_progress(self, progress):
        """Atualiza a barra de progresso e o percentual"""
        self.is_downloading = False
        self.is_transcribing = True
        
        progress_percent = min(100, int(progress * 100))
        self.progress_bar.set(progress)
        self.progress_percent_label.configure(text=f"{progress_percent}%")
        
        # Atualizar o status para mostrar que está transcrevendo
        if self.status_var.get().startswith("Baixando modelo") or \
           self.status_var.get().startswith("Modelo"):
            self.status_var.set("Transcrevendo áudio...")
    
    def show_model_info(self, model_name):
        """Mostra informações sobre o modelo que será baixado"""
        try:
            # Resetar flags
            self.is_downloading = False
            self.is_transcribing = False
            
            # Mensagem detalhada na área de transcrição
            self.transcription_text.configure(state="normal")
            self.transcription_text.delete("0.0", "end")
            
            # Obter tamanhos dos modelos do backend
            download_message = (
                f"Carregando o modelo '{model_name}'...\n\n"
                "Se o modelo não estiver disponível localmente, ele será baixado.\n"
                "Este download ocorre apenas uma vez e o modelo ficará disponível offline para uso futuro.\n\n"
                "Tamanhos aproximados dos modelos:\n"
            )
            
            for model in ["tiny", "base", "small", "medium", "large"]:
                size = self.backend.get_model_size(model)
                if model == model_name:
                    download_message += f"- {model}: {size} (selecionado)\n"
                else:
                    download_message += f"- {model}: {size}\n"
            
            self.transcription_text.insert("0.0", download_message)
            self.transcription_text.configure(state="disabled")
        except Exception as e:
            print(f"Erro ao mostrar informações do modelo: {e}")
    
    def update_download_progress(self, percent):
        """Atualiza o progresso de download do modelo na interface"""
        try:
            self.is_downloading = True
            self.is_transcribing = False
            
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(percent / 100)
            self.progress_percent_label.configure(text=f"Baixando: {percent}%")
            
            model_name = self.model_var.get()
            self.status_var.set(f"Baixando modelo {model_name}... {percent}%")
            
            # Mensagem detalhada na área de transcrição
            self.transcription_text.configure(state="normal")
            self.transcription_text.delete("0.0", "end")
            
            # Obter tamanhos dos modelos do backend
            download_message = (
                f"Baixando o modelo '{model_name}'...\n\n"
                "Este modelo será baixado apenas uma vez e ficará disponível offline para uso futuro.\n"
                "Tamanhos aproximados:\n"
            )
            
            for model in ["tiny", "base", "small", "medium", "large"]:
                size = self.backend.get_model_size(model)
                if model == model_name:
                    download_message += f"- {model}: {size} (selecionado)\n"
                else:
                    download_message += f"- {model}: {size}\n"
            
            download_message += f"\nProgresso do download: {percent}%"
            
            self.transcription_text.insert("0.0", download_message)
            self.transcription_text.configure(state="disabled")
            print(f"Progresso de download atualizado: {percent}%")
            
            # Se o download estiver completo (100%), atualizar o status
            if percent >= 100:
                self.root.after(1000, self.update_model_loaded)
        except Exception as e:
            print(f"Erro ao atualizar progresso de download: {e}")
    
    def update_model_loaded(self):
        """Atualiza a interface quando o modelo foi carregado"""
        if self.is_downloading and not self.is_transcribing:
            self.is_downloading = False
            model_name = self.model_var.get()
            self.status_var.set(f"Modelo {model_name} carregado. Iniciando transcrição...")
            self.transcription_text.configure(state="normal")
            self.transcription_text.delete("0.0", "end")
            self.transcription_text.insert("0.0", f"Modelo {model_name} carregado com sucesso.\n\nIniciando transcrição do áudio...")
            self.transcription_text.configure(state="disabled")
    
    def update_partial_transcription(self, text):
        """Atualiza a UI com a transcrição parcial"""
        self.is_downloading = False
        self.is_transcribing = True
        
        self.partial_transcription = text
        
        # Atualizar o status para mostrar que está transcrevendo
        if self.status_var.get().startswith("Baixando modelo") or \
           self.status_var.get() == "Carregando modelo...":
            self.status_var.set("Transcrevendo áudio...")
        
        # Habilitar temporariamente para edição
        self.transcription_text.configure(state="normal")
        self.transcription_text.delete("0.0", "end")
        self.transcription_text.insert("0.0", text)
        # Voltar para somente leitura
        self.transcription_text.configure(state="disabled")
        # Rolar para o final
        self.transcription_text.see("end")
    
    def update_transcription_complete(self, text=None):
        """Atualiza a UI quando a transcrição é concluída"""
        if text:
            self.transcription = text
        
        # Habilitar temporariamente para edição
        self.transcription_text.configure(state="normal")
        self.transcription_text.delete("0.0", "end")
        self.transcription_text.insert("0.0", self.transcription)
        # Voltar para somente leitura
        self.transcription_text.configure(state="disabled")
        
        # Atualizar interface
        self.save_button.configure(state="normal")
        self.status_var.set("Transcrição concluída")
        self.progress_bar.set(1.0)  # 100%
        self.progress_percent_label.configure(text="100%")
    
    def save_results(self):
        """Salva os resultados da transcrição em um arquivo"""
        if not self.transcription and not self.partial_transcription:
            messagebox.showerror("Erro", "Não há transcrição para salvar.")
            return
        
        text_to_save = self.transcription if self.transcription else self.partial_transcription
        
        file_path = filedialog.asksaveasfilename(
            title="Salvar Transcrição",
            defaultextension=".txt",
            filetypes=[("Arquivo de Texto", "*.txt"), ("Todos os arquivos", "*.*")],
            initialfile=f"transcrição_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text_to_save)
            
            messagebox.showinfo("Sucesso", f"Transcrição salva em {file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(e)}")
    
    def show_error(self, message):
        """Exibe uma mensagem de erro"""
        messagebox.showerror("Erro", message)
        self.status_var.set("Erro")


if __name__ == "__main__":
    try:
        root = ctk.CTk()  # Usar CTk em vez de Tk
        app = TranscritorFrontend(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro fatal na inicialização do aplicativo: {e}")
        import traceback
        traceback.print_exc()
