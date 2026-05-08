import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
from db import (
    listar_tarefas, criar_tarefa, atualizar_tarefa, 
    remover_tarefa, listar_categorias
)
from utils.validators import validar_data, validar_campos_obrigatorios
from utils.export import exportar_csv, exportar_pdf
from tkinter import filedialog

class JanelaTarefas(ctk.CTkToplevel):
    def __init__(self, utilizador):
        super().__init__()
        
        self.utilizador = utilizador
        self.tarefa_selecionada = None
        
        self.title("Gestão de Tarefas")
        self.geometry("1100x750")
        
        self._criar_interface()
        self._carregar_categorias()
        self._listar_tarefas()
    
    def _criar_interface(self):
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
       
        self._criar_painel_formulario()
        

        self._criar_painel_lista()
    
    def _criar_painel_formulario(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(
            frame,
            text="Nova Tarefa",
            font=("Arial", 18, "bold")
        ).pack(pady=(15, 20))
        

        campos_config = [
            ("Título *", "entry_titulo", None),
            ("Descrição", "entry_descricao", None),
            ("Data Limite *", "entry_data", "date"),
            ("Estado *", "combo_estado", "combo"),
            ("Categoria *", "combo_categoria", "combo_cat"),
        ]
        
        for label, attr, tipo in campos_config:
            ctk.CTkLabel(frame, text=label, anchor="w").pack(fill="x", padx=20, pady=(10, 2))
            
            if tipo == "date":
                widget = DateEntry(
                    frame, 
                    width=30, 
                    date_pattern='yyyy-mm-dd',
                    background='#3b82f6',
                    foreground='white'
                )
            elif tipo == "combo":
                widget = ctk.CTkComboBox(
                    frame, 
                    width=280,
                    values=["Pendente", "Em Progresso", "Concluída"]
                )
                widget.set("Pendente")
            elif tipo == "combo_cat":
                widget = ctk.CTkComboBox(frame, width=280, values=[])
            else:
                widget = ctk.CTkEntry(frame, width=280)
            
            widget.pack(padx=20, pady=(0, 5))
            setattr(self, attr, widget)
        
      
        frame_botoes = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botoes.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            frame_botoes,
            text="💾 Guardar",
            width=130,
            fg_color="#22c55e",
            command=self._guardar_tarefa
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_botoes,
            text="🗑️ Remover",
            width=130,
            fg_color="#ef4444",
            command=self._remover_tarefa
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            frame,
            text="🧹 Limpar",
            width=280,
            fg_color="#64748b",
            command=self._limpar_formulario
        ).pack(padx=20, pady=(0, 15))
    
    def _criar_painel_lista(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
       
        frame_header = ctk.CTkFrame(frame, fg_color="transparent")
        frame_header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            frame_header,
            text="As Tuas Tarefas",
            font=("Arial", 18, "bold")
        ).pack(side="left")
        
      
        ctk.CTkButton(
            frame_header,
            text="📥 CSV",
            width=70,
            fg_color="#64748b",
            command=self._exportar_csv
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            frame_header,
            text="📄 PDF",
            width=70,
            fg_color="#64748b",
            command=self._exportar_pdf
        ).pack(side="right", padx=5)
        
      
        frame_filtros = ctk.CTkFrame(frame, fg_color="#1e293b", corner_radius=10)
        frame_filtros.pack(fill="x", padx=15, pady=(0, 10))
        
       
        ctk.CTkLabel(frame_filtros, text="🔍").grid(row=0, column=0, padx=(15, 5), pady=10)
        self.entry_pesquisa = ctk.CTkEntry(frame_filtros, width=200, placeholder_text="Pesquisar...")
        self.entry_pesquisa.grid(row=0, column=1, padx=5, pady=10)
        self.entry_pesquisa.bind("<KeyRelease>", lambda e: self._listar_tarefas())
        
      
        ctk.CTkLabel(frame_filtros, text="Estado:").grid(row=0, column=2, padx=(20, 5), pady=10)
        self.filtro_estado = ctk.CTkComboBox(
            frame_filtros,
            width=130,
            values=["Todos", "Pendente", "Em Progresso", "Concluída"],
            command=lambda e: self._listar_tarefas()
        )
        self.filtro_estado.set("Todos")
        self.filtro_estado.grid(row=0, column=3, padx=5, pady=10)
        
       
        self.frame_tarefas = ctk.CTkScrollableFrame(frame, height=450)
        self.frame_tarefas.pack(fill="both", expand=True, padx=15, pady=10)
    
    def _carregar_categorias(self):
        """Carrega categorias do utilizador."""
        categorias = listar_categorias(self.utilizador['id_utilizador'])
        self.categorias = {cat['nome']: cat['id_categoria'] for cat in categorias}
        self.combo_categoria.configure(values=list(self.categorias.keys()))
        
        if self.categorias:
            self.combo_categoria.set(list(self.categorias.keys())[0])
    
    def _listar_tarefas(self):
        """Lista tarefas com filtros aplicados."""
      
        for widget in self.frame_tarefas.winfo_children():
            widget.destroy()
        
     
        filtros = {}
        
        estado = self.filtro_estado.get()
        if estado != "Todos":
            filtros["estado"] = estado
        
        pesquisa = self.entry_pesquisa.get().strip()
        if pesquisa:
            filtros["pesquisa"] = pesquisa
        
       
        tarefas = listar_tarefas(self.utilizador['id_utilizador'], filtros)
        
        if not tarefas:
            ctk.CTkLabel(
                self.frame_tarefas,
                text="Nenhuma tarefa encontrada",
                text_color="gray"
            ).pack(pady=50)
            return
        
        
        for tarefa in tarefas:
            self._criar_card_tarefa(tarefa)
    
    def _criar_card_tarefa(self, tarefa):
        """Cria um card visual para uma tarefa."""
       
        cores = {
            "Pendente": "#f59e0b",
            "Em Progresso": "#3b82f6",
            "Concluída": "#22c55e"
        }
        cor = cores.get(tarefa['estado'], "#64748b")
        
     
        if tarefa['data_limite']:
            data_limite = tarefa['data_limite']
            if isinstance(data_limite, str):
                data_limite = datetime.strptime(data_limite, "%Y-%m-%d").date()
            
            if data_limite < datetime.now().date() and tarefa['estado'] != "Concluída":
                cor = "#ef4444"  # Vermelho para atrasadas
        
        card = ctk.CTkFrame(self.frame_tarefas, fg_color="#1e293b", corner_radius=10)
        card.pack(fill="x", pady=5)
        
       
        indicador = ctk.CTkFrame(card, width=5, fg_color=cor, corner_radius=0)
        indicador.pack(side="left", fill="y")
        
        
        conteudo = ctk.CTkFrame(card, fg_color="transparent")
        conteudo.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
       
        frame_top = ctk.CTkFrame(conteudo, fg_color="transparent")
        frame_top.pack(fill="x")
        
        ctk.CTkLabel(
            frame_top,
            text=tarefa['titulo'],
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(side="left")
        
        ctk.CTkLabel(
            frame_top,
            text=tarefa['estado'],
            font=("Arial", 11),
            text_color=cor
        ).pack(side="right")
        
    
        if tarefa.get('descricao'):
            ctk.CTkLabel(
                conteudo,
                text=tarefa['descricao'][:80] + ("..." if len(tarefa['descricao']) > 80 else ""),
                font=("Arial", 11),
                text_color="gray",
                anchor="w"
            ).pack(fill="x", pady=(5, 0))
        
       
        ctk.CTkLabel(
            conteudo,
            text=f"📅 {tarefa['data_limite']}",
            font=("Arial", 11),
            text_color="gray",
            anchor="w"
        ).pack(fill="x", pady=(5, 0))
        
    
        for widget in [card, conteudo, frame_top]:
            widget.bind("<Button-1>", lambda e, t=tarefa: self._selecionar_tarefa(t))
    
    def _selecionar_tarefa(self, tarefa):
        """Preenche o formulário com a tarefa selecionada."""
        self.tarefa_selecionada = tarefa
        
        self.entry_titulo.delete(0, "end")
        self.entry_titulo.insert(0, tarefa['titulo'])
        
        self.entry_descricao.delete(0, "end")
        self.entry_descricao.insert(0, tarefa.get('descricao', ''))
        
        if tarefa['data_limite']:
            self.entry_data.set_date(tarefa['data_limite'])
        
        self.combo_estado.set(tarefa['estado'])
        
        
        for nome, id_cat in self.categorias.items():
            if id_cat == tarefa['id_categoria']:
                self.combo_categoria.set(nome)
                break
    
    def _guardar_tarefa(self):
        """Cria ou atualiza uma tarefa."""
        titulo = self.entry_titulo.get().strip()
        descricao = self.entry_descricao.get().strip()
        data_limite = self.entry_data.get_date().strftime("%Y-%m-%d")
        estado = self.combo_estado.get()
        categoria_nome = self.combo_categoria.get()
        
      
        valido, msg = validar_campos_obrigatorios(
            Título=titulo, 
            Estado=estado, 
            Categoria=categoria_nome
        )
        if not valido:
            messagebox.showwarning("Atenção", msg)
            return
        
        if categoria_nome not in self.categorias:
            messagebox.showwarning("Atenção", "Seleciona uma categoria válida.")
            return
        
        id_categoria = self.categorias[categoria_nome]
        
        try:
            if self.tarefa_selecionada:
                
                atualizar_tarefa(
                    self.tarefa_selecionada['id_tarefa'],
                    titulo, descricao, data_limite, estado,
                    id_categoria, self.utilizador['id_utilizador']
                )
                messagebox.showinfo("Sucesso", "Tarefa atualizada!")
            else:
               
                criar_tarefa(
                    titulo, descricao, data_limite, estado,
                    id_categoria, self.utilizador['id_utilizador']
                )
                messagebox.showinfo("Sucesso", "Tarefa criada!")
            
            self._limpar_formulario()
            self._listar_tarefas()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao guardar tarefa:\n{e}")
    
    def _remover_tarefa(self):
        """Remove a tarefa selecionada."""
        if not self.tarefa_selecionada:
            messagebox.showwarning("Atenção", "Seleciona uma tarefa primeiro.")
            return
        
        if messagebox.askyesno("Confirmar", "Tens a certeza que queres remover esta tarefa?"):
            try:
                remover_tarefa(self.tarefa_selecionada['id_tarefa'])
                messagebox.showinfo("Sucesso", "Tarefa removida!")
                self._limpar_formulario()
                self._listar_tarefas()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover tarefa:\n{e}")
    
    def _limpar_formulario(self):
        """Limpa todos os campos do formulário."""
        self.tarefa_selecionada = None
        self.entry_titulo.delete(0, "end")
        self.entry_descricao.delete(0, "end")
        self.combo_estado.set("Pendente")
        if self.categorias:
            self.combo_categoria.set(list(self.categorias.keys())[0])
    
    def _exportar_csv(self):
        """Exporta tarefas para CSV."""
        ficheiro = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfilename="tarefas.csv"
        )
        if ficheiro:
            tarefas = listar_tarefas(self.utilizador['id_utilizador'])
            colunas = ['titulo', 'descricao', 'data_limite', 'estado']
            exportar_csv(tarefas, ficheiro, colunas)
            messagebox.showinfo("Sucesso", f"Exportado para:\n{ficheiro}")
    
    def _exportar_pdf(self):
        """Exporta tarefas para PDF."""
        ficheiro = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfilename="tarefas.pdf"
        )
        if ficheiro:
            tarefas = listar_tarefas(self.utilizador['id_utilizador'])
            colunas = ['titulo', 'descricao', 'data_limite', 'estado']
            exportar_pdf(tarefas, ficheiro, "As Minhas Tarefas", colunas)
            messagebox.showinfo("Sucesso", f"Exportado para:\n{ficheiro}")
