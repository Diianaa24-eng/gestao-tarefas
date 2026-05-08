import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from db import obter_estatisticas_tarefas, obter_estatisticas_pagamentos, listar_tarefas

class JanelaEstatisticas(ctk.CTkToplevel):
    def __init__(self, utilizador):
        super().__init__()
        
        self.utilizador = utilizador
        
        self.title("Estatísticas")
        self.geometry("900x700")
        
        self._criar_interface()
    
    def _criar_interface(self):
        # Notebook para diferentes gráficos
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tabview.add("Tarefas")
        self.tabview.add("Pagamentos")
        self.tabview.add("Cronograma")
        
        self._criar_grafico_tarefas()
        self._criar_grafico_pagamentos()
        self._criar_cronograma()
    
    def _criar_grafico_tarefas(self):
        """Gráfico de pizza com estados das tarefas."""
        tab = self.tabview.tab("Tarefas")
        
        stats = obter_estatisticas_tarefas(self.utilizador['id_utilizador'])
        
        if not stats or stats['total'] == 0:
            ctk.CTkLabel(
                tab,
                text="Sem dados de tarefas",
                font=("Arial", 16)
            ).pack(expand=True)
            return
        
        # Criar figura
        fig = Figure(figsize=(8, 5), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        
        # Gráfico de pizza
        ax1 = fig.add_subplot(121)
        ax1.set_facecolor('#2b2b2b')
        
        labels = ['Concluídas', 'Pendentes', 'Em Progresso']
        sizes = [
            stats['concluidas'] or 0,
            stats['pendentes'] or 0,
            stats['em_progresso'] or 0
        ]
        colors = ['#22c55e', '#f59e0b', '#3b82f6']
        explode = (0.05, 0, 0)
        
        # Filtrar zeros
        filtered = [(l, s, c) for l, s, c in zip(labels, sizes, colors) if s > 0]
        if filtered:
            labels, sizes, colors = zip(*filtered)
            ax1.pie(sizes, explode=explode[:len(sizes)], labels=labels, colors=colors,
                    autopct='%1.1f%%', shadow=True, startangle=90,
                    textprops={'color': 'white'})
            ax1.set_title('Estado das Tarefas', color='white', fontsize=14)
        
        # Gráfico de barras
        ax2 = fig.add_subplot(122)
        ax2.set_facecolor('#2b2b2b')
        
        categorias = ['Total', 'Concluídas', 'Atrasadas']
        valores = [stats['total'], stats['concluidas'] or 0, stats['atrasadas'] or 0]
        cores = ['#3b82f6', '#22c55e', '#ef4444']
        
        bars = ax2.bar(categorias, valores, color=cores)
        ax2.set_title('Resumo de Tarefas', color='white', fontsize=14)
        ax2.tick_params(colors='white')
        ax2.spines['bottom'].set_color('white')
        ax2.spines['left'].set_color('white')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        # Adicionar valores nas barras
        for bar, val in zip(bars, valores):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(val), ha='center', color='white', fontsize=12)
        
        fig.tight_layout()
        
        # Incorporar no tkinter
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _criar_grafico_pagamentos(self):
        """Gráfico de pagamentos."""
        tab = self.tabview.tab("Pagamentos")
        
        stats = obter_estatisticas_pagamentos(self.utilizador['id_utilizador'])
        
        if not stats or stats['total'] == 0:
            ctk.CTkLabel(
                tab,
                text="Sem dados de pagamentos",
                font=("Arial", 16)
            ).pack(expand=True)
            return
        
        fig = Figure(figsize=(8, 5), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2b2b2b')
        
        categorias = ['Valor Total', 'Pago', 'Pendente']
        valores = [
            float(stats['valor_total'] or 0),
            float(stats['valor_pago'] or 0),
            float(stats['valor_pendente'] or 0)
        ]
        cores = ['#3b82f6', '#22c55e', '#f59e0b']
        
        bars = ax.bar(categorias, valores, color=cores)
        ax.set_title('Resumo de Pagamentos (€)', color='white', fontsize=14)
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        for bar, val in zip(bars, valores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{val:.2f}€', ha='center', color='white', fontsize=11)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _criar_cronograma(self):
        """Gráfico de tarefas por data (timeline)."""
        tab = self.tabview.tab("Cronograma")
        
        tarefas = listar_tarefas(self.utilizador['id_utilizador'])
        
        if not tarefas:
            ctk.CTkLabel(
                tab,
                text="Sem tarefas para mostrar",
                font=("Arial", 16)
            ).pack(expand=True)
            return
        
        # Agrupar por mês
        from collections import defaultdict
        from datetime import datetime
        
        por_mes = defaultdict(int)
        for tarefa in tarefas:
            if tarefa['data_limite']:
                data = tarefa['data_limite']
                if isinstance(data, str):
                    data = datetime.strptime(data, "%Y-%m-%d").date()
                mes = data.strftime("%Y-%m")
                por_mes[mes] += 1
        
        if not por_mes:
            ctk.CTkLabel(tab, text="Sem dados", font=("Arial", 16)).pack(expand=True)
            return
        
        # Ordenar por mês
        meses = sorted(por_mes.keys())
        valores = [por_mes[m] for m in meses]
        
        fig = Figure(figsize=(8, 5), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2b2b2b')
        
        ax.plot(meses, valores, marker='o', color='#3b82f6', linewidth=2, markersize=8)
        ax.fill_between(meses, valores, alpha=0.3, color='#3b82f6')
        
        ax.set_title('Tarefas por Mês', color='white', fontsize=14)
        ax.set_xlabel('Mês', color='white')
        ax.set_ylabel('Número de Tarefas', color='white')
        ax.tick_params(colors='white', rotation=45)
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
