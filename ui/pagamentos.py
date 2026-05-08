import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
from db import listar_pagamentos, criar_pagamento, atualizar_pagamento, remover_pagamento
from utils.validators import validar_campos_obrigatorios, validar_valor


class JanelaPagamentos(ctk.CTkToplevel):
    def __init__(self, utilizador):
        super().__init__()

        self.utilizador = utilizador
        self.pagamento_selecionado = None

        self.title("Gestão de Pagamentos")
        self.geometry("1000x700")

        self._criar_interface()
        self._listar_pagamentos()

    def _criar_interface(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self._criar_formulario()
        self._criar_lista()

    def _criar_formulario(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Novo Pagamento", font=("Arial", 18, "bold")).pack(pady=(15, 20))

        ctk.CTkLabel(frame, text="Descrição *", anchor="w").pack(fill="x", padx=20, pady=(10, 2))
        self.entry_descricao = ctk.CTkEntry(frame, width=280)
        self.entry_descricao.pack(padx=20, pady=(0, 8))

        ctk.CTkLabel(frame, text="Valor *", anchor="w").pack(fill="x", padx=20, pady=(10, 2))
        self.entry_valor = ctk.CTkEntry(frame, width=280, placeholder_text="Ex: 25.50")
        self.entry_valor.pack(padx=20, pady=(0, 8))

        ctk.CTkLabel(frame, text="Data *", anchor="w").pack(fill="x", padx=20, pady=(10, 2))
        self.entry_data = DateEntry(frame, width=30, date_pattern="yyyy-mm-dd")
        self.entry_data.pack(padx=20, pady=(0, 8))

        ctk.CTkLabel(frame, text="Estado *", anchor="w").pack(fill="x", padx=20, pady=(10, 2))
        self.combo_estado = ctk.CTkComboBox(frame, width=280, values=["Pendente", "Pago"])
        self.combo_estado.set("Pendente")
        self.combo_estado.pack(padx=20, pady=(0, 8))

        frame_botoes = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botoes.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            frame_botoes,
            text="💾 Guardar",
            width=130,
            fg_color="#22c55e",
            command=self._guardar_pagamento
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botoes,
            text="🗑️ Remover",
            width=130,
            fg_color="#ef4444",
            command=self._remover_pagamento
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            frame,
            text="🧹 Limpar",
            width=280,
            fg_color="#64748b",
            command=self._limpar_formulario
        ).pack(padx=20, pady=(0, 15))

    def _criar_lista(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Os Teus Pagamentos", font=("Arial", 18, "bold")).pack(pady=15)

        self.frame_pagamentos = ctk.CTkScrollableFrame(frame, height=550)
        self.frame_pagamentos.pack(fill="both", expand=True, padx=15, pady=10)

    def _listar_pagamentos(self):
        for widget in self.frame_pagamentos.winfo_children():
            widget.destroy()

        pagamentos = listar_pagamentos(self.utilizador["id_utilizador"])

        if not pagamentos:
            ctk.CTkLabel(self.frame_pagamentos, text="Nenhum pagamento encontrado", text_color="gray").pack(pady=50)
            return

        for pagamento in pagamentos:
            self._criar_card_pagamento(pagamento)

    def _criar_card_pagamento(self, pagamento):
        cor = "#22c55e" if pagamento.get("estado") == "Pago" else "#ef4444"

        card = ctk.CTkFrame(self.frame_pagamentos, fg_color="#1e293b", corner_radius=10)
        card.pack(fill="x", pady=6)

        ctk.CTkFrame(card, width=5, fg_color=cor, corner_radius=0).pack(side="left", fill="y")

        conteudo = ctk.CTkFrame(card, fg_color="transparent")
        conteudo.pack(side="left", fill="both", expand=True, padx=15, pady=10)

        valor = float(pagamento.get("valor") or 0)

        ctk.CTkLabel(
            conteudo,
            text=f"{pagamento['descricao']} - {valor:.2f}€",
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            conteudo,
            text=f"📅 {pagamento.get('data_pagamento', '')}  •  {pagamento.get('estado', '')}",
            text_color=cor,
            anchor="w"
        ).pack(fill="x", pady=(5, 0))

        for widget in [card, conteudo]:
            widget.bind("<Button-1>", lambda e, p=pagamento: self._selecionar_pagamento(p))

    def _selecionar_pagamento(self, pagamento):
        self.pagamento_selecionado = pagamento

        self.entry_descricao.delete(0, "end")
        self.entry_descricao.insert(0, pagamento.get("descricao", ""))

        self.entry_valor.delete(0, "end")
        self.entry_valor.insert(0, str(pagamento.get("valor", "")))

        if pagamento.get("data_pagamento"):
            self.entry_data.set_date(pagamento["data_pagamento"])

        self.combo_estado.set(pagamento.get("estado", "Pendente"))

    def _guardar_pagamento(self):
        descricao = self.entry_descricao.get().strip()
        valor_str = self.entry_valor.get().strip()
        data_pagamento = self.entry_data.get_date().strftime("%Y-%m-%d")
        estado = self.combo_estado.get()

        valido, msg = validar_campos_obrigatorios(Descrição=descricao, Valor=valor_str, Data=data_pagamento, Estado=estado)
        if not valido:
            messagebox.showwarning("Atenção", msg)
            return

        valido, msg = validar_valor(valor_str)
        if not valido:
            messagebox.showwarning("Atenção", msg)
            return

        valor = float(valor_str.replace(",", "."))

        try:
            if self.pagamento_selecionado:
                atualizar_pagamento(
                    self.pagamento_selecionado["id_pagamento"],
                    descricao,
                    valor,
                    data_pagamento,
                    estado,
                    self.utilizador["id_utilizador"]
                )
                messagebox.showinfo("Sucesso", "Pagamento atualizado!")
            else:
                criar_pagamento(descricao, valor, data_pagamento, estado, self.utilizador["id_utilizador"])
                messagebox.showinfo("Sucesso", "Pagamento criado!")

            self._limpar_formulario()
            self._listar_pagamentos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao guardar pagamento:\n{e}")

    def _remover_pagamento(self):
        if not self.pagamento_selecionado:
            messagebox.showwarning("Atenção", "Seleciona um pagamento primeiro.")
            return

        if messagebox.askyesno("Confirmar", "Tens a certeza que queres remover este pagamento?"):
            try:
                remover_pagamento(self.pagamento_selecionado["id_pagamento"])
                messagebox.showinfo("Sucesso", "Pagamento removido!")
                self._limpar_formulario()
                self._listar_pagamentos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover pagamento:\n{e}")

    def _limpar_formulario(self):
        self.pagamento_selecionado = None
        self.entry_descricao.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.combo_estado.set("Pendente")
