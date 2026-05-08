import customtkinter as ctk
from tkcalendar import Calendar
from datetime import datetime
from db import obter_itens_calendario

class JanelaCalendario(ctk.CTkToplevel):
    def __init__(self, utilizador):
        super().__init__()
        
        self.utilizador = utilizador
        self.itens = []
        
        self.title("Calendário")
        self.geometry("1000x650")
        
        self._criar_interface()
        self._carregar_itens()
    
    def _criar_interface(self):
       
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        
        frame_cal = ctk.CTkFrame(self)
        frame_cal.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(
            frame_cal,
            text="📆 Calendário",
            font=("Arial", 18, "bold")
        ).pack(pady=15)
        
        self.calendario = Calendar(
            frame_cal,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            font=("Arial", 11),
            background='#1e293b',
            foreground='white',
            headersbackground='#3b82f6',
            headersforeground='white',
            selectbackground='#22c55e',
            selectforeground='white',
            normalbackground='#2b2b2b',
            normalforeground='white',
            weekendbackground='#374151',
            weekendforeground='white',
            othermonthforeground='gray',
            othermonthbackground='#1e293b',
            othermonthweforeground='gray',
            othermonthwebackground='#1e293b'
        )
        self.calendario.pack(padx=20, pady=10, fill="both", expand=True)
        self.calendario.bind("<<CalendarSelected>>", self._data_selecionada)
        
        # Coluna direita - Detalhes do dia
        frame_detalhes = ctk.CTkFrame(self)
        frame_detalhes.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.label_data = ctk.CTkLabel(
            frame_detalhes,
            text="Seleciona uma data",
            font=("Arial", 18, "bold")
        )
        self.label_data.pack(pady=15)
        
        self.frame_itens = ctk.CTkScrollableFrame(frame_detalhes, height=450)
        self.frame_itens.pack(fill="both", expand=True, padx=15, pady=10)
        
        
        frame_legenda = ctk.CTkFrame(frame_detalhes, fg_color="transparent")
        frame_legenda.pack(fill="x", padx=15, pady=10)
        
        legenda = [
            ("🔵 Tarefa", "#3b82f6"),
            ("🟠 Evento", "#f59e0b"),
            ("🔴 Pagamento", "#ef4444")
        ]
        
        for texto, cor in legenda:
            ctk.CTkLabel(frame_legenda, text=texto, text_color=cor).pack(side="left", padx=10)
    
    def _carregar_itens(self):
        """Carrega todos os itens do calendário."""
        self.itens = obter_itens_calendario(self.utilizador['id_utilizador'])
        
        
        for item in self.itens:
            if item['data']:
                data = item['data']
                if isinstance(data, str):
                    data = datetime.strptime(data, "%Y-%m-%d").date()
                
               
                try:
                    self.calendario.calevent_create(data, item['titulo'], item['tipo'].lower())
                except:
                    pass
        
       
        self._mostrar_itens_data(datetime.now().strftime("%Y-%m-%d"))
    
    def _data_selecionada(self, event):
        """Callback quando uma data é selecionada."""
        data = self.calendario.get_date()
        self._mostrar_itens_data(data)
    
    def _mostrar_itens_data(self, data_str):
        """Mostra os itens de uma data específica."""
       
        try:
            data_obj = datetime.strptime(data_str, "%Y-%m-%d")
            data_formatada = data_obj.strftime("%d de %B de %Y")
            self.label_data.configure(text=f"📅 {data_formatada}")
        except:
            self.label_data.configure(text=f"📅 {data_str}")
        
        
        for widget in self.frame_itens.winfo_children():
            widget.destroy()
        
        
        itens_dia = []
        for item in self.itens:
            if item['data']:
                item_data = item['data']
                if hasattr(item_data, 'strftime'):
                    item_data = item_data.strftime("%Y-%m-%d")
                
                if item_data == data_str:
                    itens_dia.append(item)
        
        if not itens_dia:
            ctk.CTkLabel(
                self.frame_itens,
                text="Nenhum evento neste dia",
                text_color="gray"
            ).pack(pady=30)
            return
        
       
        for item in itens_dia:
            self._criar_card_item(item)
    
    def _criar_card_item(self, item):
        """Cria um card para um item do calendário."""
        cores = {
            "Tarefa": "#3b82f6",
            "Evento": "#f59e0b",
            "Pagamento": "#ef4444"
        }
        emojis = {
            "Tarefa": "📝",
            "Evento": "📅",
            "Pagamento": "💳"
        }
        
        cor = cores.get(item['tipo'], "#64748b")
        emoji = emojis.get(item['tipo'], "📌")
        
        card = ctk.CTkFrame(self.frame_itens, fg_color="#1e293b", corner_radius=10)
        card.pack(fill="x", pady=5)
        
       
        ctk.CTkFrame(card, width=5, fg_color=cor, corner_radius=0).pack(side="left", fill="y")
        
        
        conteudo = ctk.CTkFrame(card, fg_color="transparent")
        conteudo.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        
        frame_top = ctk.CTkFrame(conteudo, fg_color="transparent")
        frame_top.pack(fill="x")
        
        ctk.CTkLabel(
            frame_top,
            text=f"{emoji} {item['tipo']}",
            font=("Arial", 11),
            text_color=cor
        ).pack(side="left")
        
        ctk.CTkLabel(
            conteudo,
            text=item['titulo'],
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(5, 0))
        
        
        if item.get('info'):
            ctk.CTkLabel(
                conteudo,
                text=str(item['info']),
                font=("Arial", 11),
                text_color="gray",
                anchor="w"
            ).pack(fill="x")
