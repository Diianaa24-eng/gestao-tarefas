import customtkinter as ctk
from configparser import ConfigParser


def carregar_tema():
    try:
        config = ConfigParser()
        config.read("config.ini")
        return config.get("app", "theme", fallback="dark")
    except:
        return "dark"

ctk.set_appearance_mode(carregar_tema())
ctk.set_default_color_theme("blue")

from ui.login import JanelaLogin
from ui.menu import JanelaMenu
from ui.tarefas import JanelaTarefas
from ui.eventos import JanelaEventos
from ui.pagamentos import JanelaPagamentos
from ui.categorias import JanelaCategorias
from ui.calendario import JanelaCalendario
from ui.estatisticas import JanelaEstatisticas
from ui.definicoes import JanelaDefinicoes

class App:
    def __init__(self):
        self.utilizador = None
        self.janela_menu = None
    
    def iniciar(self):
        """Inicia a aplicação com a janela de login."""
        login = JanelaLogin()
        login.mainloop()
        
        if login.utilizador:
            self.utilizador = login.utilizador
            self._abrir_menu()
    
    def _abrir_menu(self):
        """Abre o menu principal."""
        
        root = ctk.CTk()
        root.withdraw()
        
        self.janela_menu = JanelaMenu(self.utilizador, self._callback_modulo)
        
        root.mainloop()
    
    def _callback_modulo(self, modulo, utilizador):
        """Callback para abrir módulos a partir do menu."""
        janelas = {
            "tarefas": JanelaTarefas,
            "eventos": JanelaEventos,
            "pagamentos": JanelaPagamentos,
            "categorias": JanelaCategorias,
            "calendario": JanelaCalendario,
            "estatisticas": JanelaEstatisticas,
            "definicoes": JanelaDefinicoes,
        }
        
        if modulo in janelas:
            janelas[modulo](utilizador)

if __name__ == "__main__":
    app = App()
    app.iniciar()
