import tkinter as tk
import customtkinter as ctk
import webbrowser
from transcritor_frontend import TranscritorFrontend

def add_developer_signature(root):
    """Adiciona a assinatura do desenvolvedor na parte inferior da janela"""
    # Frame para a assinatura (na parte inferior da janela principal)
    signature_frame = ctk.CTkFrame(root, fg_color="#242424", height=30)
    signature_frame.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Função para abrir o Instagram quando clicar no link
    def open_instagram():
        webbrowser.open("https://www.instagram.com/eusoucarlosmedeiros/")
    
    # Container centralizado para os elementos da assinatura
    container_frame = ctk.CTkFrame(signature_frame, fg_color="transparent")
    container_frame.pack(expand=True, fill=tk.BOTH)
    
    # Centralizar os widgets no container
    container_frame.grid_columnconfigure(0, weight=1)  # Coluna esquerda com peso 1
    container_frame.grid_columnconfigure(1, weight=0)  # Coluna do texto sem peso
    container_frame.grid_columnconfigure(2, weight=0)  # Coluna do link sem peso
    container_frame.grid_columnconfigure(3, weight=1)  # Coluna direita com peso 1
    container_frame.grid_rowconfigure(0, weight=1)     # Centralizar verticalmente
    
    # Label "Desenvolvido por:"
    signature_label = ctk.CTkLabel(
        container_frame, 
        text="Desenvolvido por ", 
        font=ctk.CTkFont(size=12),
        text_color="#CCCCCC"
    )
    signature_label.grid(row=0, column=1, sticky="e")
    
    # Botão com o nome do desenvolvedor (funciona como um link)
    signature_link = ctk.CTkButton(
        container_frame, 
        text="@eusoucarlosmedeiros", 
        font=ctk.CTkFont(size=12, underline=True),
        fg_color="transparent", 
        hover_color="#2B2B2B",
        text_color="#3B8ED0",
        height=25,
        command=open_instagram
    )
    signature_link.grid(row=0, column=2, sticky="w")

if __name__ == "__main__":
    try:
        # Configurar a janela principal
        root = ctk.CTk()
        root.title("FalaMemo - Transcritor de Áudio")
        root.geometry("900x650")
        root.minsize(900, 650)
        
        # Adicionar a assinatura do desenvolvedor
        add_developer_signature(root)
        
        # Inicializar a aplicação
        app = TranscritorFrontend(root)
        
        # Iniciar o loop principal
        root.mainloop()
    except Exception as e:
        print(f"Erro fatal na inicialização do aplicativo: {e}")
        import traceback
        traceback.print_exc()
