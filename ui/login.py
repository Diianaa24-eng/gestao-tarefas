import customtkinter as ctk
from tkinter import messagebox
from auth import autenticar, registar_utilizador
from utils.validators import validar_email, validar_password, validar_campos_obrigatorios

class JanelaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Gestão Pessoal - Login")
        self.geometry("450x550")
        self.resizable(False, False)
        
        # Utilizador autenticado (será preenchido após login)
        self.utilizador = None
        
        self._criar_interface()
        self._centrar_janela()
    
    def _centrar_janela(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _criar_interface(self):
        # Frame principal
        self.frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_principal.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Logo/Título
        ctk.CTkLabel(
            self.frame_principal,
            text="🗂️",
            font=("Arial", 50)
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            self.frame_principal,
            text="Gestão Pessoal",
            font=("Arial", 28, "bold")
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            self.frame_principal,
            text="Organiza a tua vida",
            font=("Arial", 14),
            text_color="gray"
        ).pack(pady=(0, 30))
        
        # Tabview para Login/Registo
        self.tabview = ctk.CTkTabview(self.frame_principal, width=350, height=300)
        self.tabview.pack(fill="both", expand=True)
        
        self.tabview.add("Login")
        self.tabview.add("Registar")
        
        self._criar_tab_login()
        self._criar_tab_registo()
    
    def _criar_tab_login(self):
        tab = self.tabview.tab("Login")
        
        ctk.CTkLabel(tab, text="Email", anchor="w").pack(fill="x", pady=(20, 5))
        self.entry_email_login = ctk.CTkEntry(tab, width=300, placeholder_text="email@exemplo.com")
        self.entry_email_login.pack(pady=(0, 15))
        
        ctk.CTkLabel(tab, text="Password", anchor="w").pack(fill="x", pady=(0, 5))
        self.entry_password_login = ctk.CTkEntry(tab, width=300, show="•", placeholder_text="••••••••")
        self.entry_password_login.pack(pady=(0, 25))
        
        ctk.CTkButton(
            tab,
            text="Entrar",
            width=300,
            height=40,
            command=self._fazer_login
        ).pack(pady=(0, 10))
    
    def _criar_tab_registo(self):
        tab = self.tabview.tab("Registar")
        
        ctk.CTkLabel(tab, text="Nome", anchor="w").pack(fill="x", pady=(10, 5))
        self.entry_nome_registo = ctk.CTkEntry(tab, width=300, placeholder_text="O teu nome")
        self.entry_nome_registo.pack(pady=(0, 10))
        
        ctk.CTkLabel(tab, text="Email", anchor="w").pack(fill="x", pady=(0, 5))
        self.entry_email_registo = ctk.CTkEntry(tab, width=300, placeholder_text="email@exemplo.com")
        self.entry_email_registo.pack(pady=(0, 10))
        
        ctk.CTkLabel(tab, text="Password", anchor="w").pack(fill="x", pady=(0, 5))
        self.entry_password_registo = ctk.CTkEntry(tab, width=300, show="•", placeholder_text="Mínimo 6 caracteres")
        self.entry_password_registo.pack(pady=(0, 15))
        
        ctk.CTkButton(
            tab,
            text="Criar Conta",
            width=300,
            height=40,
            command=self._fazer_registo
        ).pack(pady=(0, 10))
    
    def _fazer_login(self):
        email = self.entry_email_login.get().strip()
        password = self.entry_password_login.get()
        
        # Validações
        valido, msg = validar_campos_obrigatorios(Email=email, Password=password)
        if not valido:
            messagebox.showwarning("Atenção", msg)
            return
        
        valido, msg = validar_email(email)
        if not valido:
            messagebox.showwarning("Atenção", msg)
            return
        
        # Autenticar
        sucesso, resultado = autenticar(email, password)
        if sucesso:
            self.utilizador = resultado
            self.destroy()
        else:
            messagebox.showerror("Erro", resultado)
    
    def _fazer_registo(self):
        nome = self.entry_nome_registo.get().strip()
        email = self.entry_email_registo.get().strip()
        password = self.entry_password_registo.get()
        
        # Validações
        valido, msg = validar_campos_obrigatorios(Nome=nome, Email=email, Password=password)
        if not valido:
            messagebox.showwarning("Atenção", msg)
            return
        
        valido, msg = validar_email(email)
        if not valido:
            messagebox.showwarning("Atenção", msg)
            return
        
        valido, msg = validar_password(password)
        if not valido:
            messagebox.showwarning("Atenção", msg)
            return
        
        # Registar
        sucesso, msg = registar_utilizador(nome, email, password)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.tabview.set("Login")
            self.entry_email_login.delete(0, "end")
            self.entry_email_login.insert(0, email)
        else:
            messagebox.showerror("Erro", msg)
