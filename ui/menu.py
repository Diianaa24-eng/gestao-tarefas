import customtkinter as ctk
from tkinter import messagebox
from db import obter_alertas, obter_estatisticas_tarefas

class JanelaMenu(ctk.CTkToplevel):
    def __init__(self, utilizador, app_callback):
        super().__init__()
        
        self.utilizador = utilizador
        self.app_callback = app_callback
        
        self.title("Gestão Pessoal")
        self.geometry("600x750")
        self.resizable(False, False)
        
        self._criar_interface()
        self._verificar_alertas()
        self._centrar_janela()
        
        
        self.protocol("WM_DELETE_WINDOW", self._sair)
    
    def _centrar_janela(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _criar_interface(self):
        
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=20)
        
    
        ctk.CTkLabel(
            frame,
            text=f"Olá, {self.utilizador['nome']}! 👋",
            font=("Arial", 24, "bold")
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            frame,
            text="O que queres fazer hoje?",
            font=("Arial", 14),
            text_color="gray"
        ).pack(pady=(0, 25))
        
        
        self._criar_estatisticas_rapidas(frame)
        
        
        botoes = [
            ("📝 Tarefas", "tarefas", "#10b981"),
            ("📅 Eventos", "eventos", "#f59e0b"),
            ("💳 Pagamentos", "pagamentos", "#ef4444"),
            ("📂 Categorias", "categorias", "#6366f1"),
            ("📆 Calendário", "calendario", "#14b8a6"),
            ("📊 Estatísticas", "estatisticas", "#8b5cf6"),
        ]
        
        for texto, modulo, cor in botoes:
            ctk.CTkButton(
                frame,
                text=texto,
                width=350,
                height=50,
                font=("Arial", 14, "bold"),
                fg_color=cor,
                hover_color=self._escurecer_cor(cor),
                command=lambda m=modulo: self._abrir_modulo(m)
            ).pack(pady=8)
        
        
        ctk.CTkFrame(frame, height=2, fg_color="gray").pack(fill="x", pady=20)
        
        
        frame_secundario = ctk.CTkFrame(frame, fg_color="transparent")
        frame_secundario.pack(fill="x")
        
        ctk.CTkButton(
            frame_secundario,
            text="⚙️ Definições",
            width=170,
            height=40,
            fg_color="#64748b",
            command=self._abrir_definicoes
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            frame_secundario,
            text="🚪 Sair",
            width=170,
            height=40,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            command=self._sair
        ).pack(side="right")
    
    def _criar_estatisticas_rapidas(self, parent):
        """Mostra um resumo rápido das tarefas."""
        stats = obter_estatisticas_tarefas(self.utilizador['id_utilizador'])
        
        if not stats or stats['total'] == 0:
            return
        
        frame_stats = ctk.CTkFrame(parent, fg_color="#1e293b", corner_radius=10)
        frame_stats.pack(fill="x", pady=(0, 20))
        
        
        dados = [
            ("📋", str(stats['total'] or 0), "Total"),
            ("✅", str(stats['concluidas'] or 0), "Concluídas"),
            ("⏳", str(stats['pendentes'] or 0), "Pendentes"),
            ("⚠️", str(stats['atrasadas'] or 0), "Atrasadas"),
        ]
        
        for i, (emoji, valor, label) in enumerate(dados):
            col_frame = ctk.CTkFrame(frame_stats, fg_color="transparent")
            col_frame.grid(row=0, column=i, padx=15, pady=15)
            
            ctk.CTkLabel(col_frame, text=emoji, font=("Arial", 20)).pack()
            ctk.CTkLabel(col_frame, text=valor, font=("Arial", 18, "bold")).pack()
            ctk.CTkLabel(col_frame, text=label, font=("Arial", 10), text_color="gray").pack()
        
        frame_stats.grid_columnconfigure((0, 1, 2, 3), weight=1)
    
    def _verificar_alertas(self):
        """Verifica e mostra alertas de itens próximos do prazo."""
        alertas = obter_alertas(self.utilizador['id_utilizador'], dias=3)
        
        if alertas:
            texto = "Tens itens próximos do prazo:\n\n"
            for alerta in alertas[:5]:  # Mostrar no máximo 5
                data = alerta.get('data_limite', alerta.get('data_pagamento', ''))
                texto += f"• {alerta['tipo']}: {alerta['titulo']} ({data})\n"
            
            if len(alertas) > 5:
                texto += f"\n... e mais {len(alertas) - 5} item(s)"
            
            messagebox.showinfo("🔔 Alertas", texto)
    
    def _escurecer_cor(self, hex_cor):
        """Escurece uma cor hex para o hover."""
        hex_cor = hex_cor.lstrip('#')
        r, g, b = tuple(int(hex_cor[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _abrir_modulo(self, modulo):
        """Abre o módulo selecionado."""
        self.app_callback(modulo, self.utilizador)
    
    def _abrir_definicoes(self):
        """Abre janela de definições."""
        self.app_callback("definicoes", self.utilizador)
    
    def _sair(self):
        """Termina a aplicação."""
        if messagebox.askyesno("Sair", "Tens a certeza que queres sair?"):
            self.quit()
            self.destroy()
