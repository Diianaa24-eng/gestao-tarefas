import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
from db import listar_eventos, criar_evento, atualizar_evento, remover_evento
from utils.validators import validar_campos_obrigatorios, validar_hora


class JanelaEventos(ctk.CTkToplevel):
    def __init__(self, utilizador):
        super().__init__()

        self.utilizador = utilizador
        self.evento_selecionado = None

        self.title("Gestão de Eventos")
        self.geometry("1000x700")

        self._criar_interface()
        self._listar_eventos()

    def _criar_interface(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self._criar_formulario()
        self._criar_lista()

    def _criar_formulario(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(frame, text="Novo Evento", font=("Arial", 18, "bold")).pack(pady=(15, 20))

        ctk.CTkLabel(frame, text="Título *", anchor="w").pack(fill="x", padx=20, pady=(10, 2))
        self.entry_titulo = ctk.CTkEntry(frame, width=280)
        self.entry_titulo.pack(padx=20, pady=(0, 8))

        ctk.CTkLabel(frame, text="Descrição", anchor="w").pack(fill="x", padx=20, pady=(10, 2))
        self.entry_descricao = ctk.CTkEntry(frame, width=280)
        self.entry_descricao.pack(padx=20, pady=(0, 8))

        ctk.CTkLabel(frame, text="Data *", anchor="w").pack(fill="x", padx=20, pady=(10, 2))
        self.entry_data = DateEntry(frame, width=30, date_pattern="yyyy-mm-dd")
        self.entry_data.pack(padx=20, pady=(0, 8))

        ctk.CTkLabel(frame, text="Hora * (HH:MM)", anchor="w").pack(fill="x", padx=20, pady=(10, 2))
        self.entry_hora = ctk.CTkEntry(frame, width=280, placeholder_text="Ex: 14:30")
        self.entry_hora.pack(padx=20, pady=(0, 8))

        ctk.CTkLabel(frame, text="Local", anchor="w").pack(fill="x", padx=20, pady=(10, 2))
        self.entry_local = ctk.CTkEntry(frame, width=280)
        self.entry_local.pack(padx=20, pady=(0, 8))

        frame_botoes = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botoes.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            frame_botoes,
            text="💾 Guardar",
            width=130,
            fg_color="#22c55e",
            command=self._guardar_evento
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botoes,
            text="🗑️ Remover",
            width=130,
            fg_color="#ef4444",
            command=self._remover_evento
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

        ctk.CTkLabel(frame, text="Os Teus Eventos", font=("Arial", 18, "bold")).pack(pady=15)

        self.frame_eventos = ctk.CTkScrollableFrame(frame, height=550)
        self.frame_eventos.pack(fill="both", expand=True, padx=15, pady=10)

    def _listar_eventos(self):
        for widget in self.frame_eventos.winfo_children():
            widget.destroy()

        eventos = listar_eventos(self.utilizador["id_utilizador"])

        if not eventos:
            ctk.CTkLabel(self.frame_eventos, text="Nenhum evento encontrado", text_color="gray").pack(pady=50)
            return

        for evento in eventos:
            self._criar_card_evento(evento)

    def _criar_card_evento(self, evento):
        card = ctk.CTkFrame(self.frame_eventos, fg_color="#1e293b", corner_radius=10)
        card.pack(fill="x", pady=6)

        ctk.CTkFrame(card, width=5, fg_color="#f59e0b", corner_radius=0).pack(side="left", fill="y")

        conteudo = ctk.CTkFrame(card, fg_color="transparent")
        conteudo.pack(side="left", fill="both", expand=True, padx=15, pady=10)

        ctk.CTkLabel(
            conteudo,
            text=evento["titulo"],
            font=("Arial", 14, "bold"),
            anchor="w"
        ).pack(fill="x")

        detalhes = f"📅 {evento.get('data_evento', '')}  🕒 {evento.get('hora_evento', '')}"
        if evento.get("local"):
            detalhes += f"  📍 {evento['local']}"

        ctk.CTkLabel(conteudo, text=detalhes, text_color="gray", anchor="w").pack(fill="x", pady=(5, 0))

        if evento.get("descricao"):
            ctk.CTkLabel(
                conteudo,
                text=evento["descricao"],
                text_color="gray",
                anchor="w"
            ).pack(fill="x", pady=(5, 0))

        for widget in [card, conteudo]:
            widget.bind("<Button-1>", lambda e, ev=evento: self._selecionar_evento(ev))

    def _selecionar_evento(self, evento):
        self.evento_selecionado = evento

        self.entry_titulo.delete(0, "end")
        self.entry_titulo.insert(0, evento.get("titulo", ""))

        self.entry_descricao.delete(0, "end")
        self.entry_descricao.insert(0, evento.get("descricao", ""))

        if evento.get("data_evento"):
            self.entry_data.set_date(evento["data_evento"])

        self.entry_hora.delete(0, "end")
        self.entry_hora.insert(0, str(evento.get("hora_evento", "")))

        self.entry_local.delete(0, "end")
        self.entry_local.insert(0, evento.get("local", ""))

    def _guardar_evento(self):
        titulo = self.entry_titulo.get().strip()
        descricao = self.entry_descricao.get().strip()
        data_evento = self.entry_data.get_date().strftime("%Y-%m-%d")
        hora_evento = self.entry_hora.get().strip()
        local = self.entry_local.get().strip()

        valido, msg = validar_campos_obrigatorios(Título=titulo, Data=data_evento, Hora=hora_evento)
        if not valido:
            messagebox.showwarning("Atenção", msg)
            return

        valido, msg = validar_hora(hora_evento)
        if not valido:
            messagebox.showwarning("Atenção", msg)
            return

        try:
            if self.evento_selecionado:
                atualizar_evento(
                    self.evento_selecionado["id_evento"],
                    titulo,
                    descricao,
                    data_evento,
                    hora_evento,
                    local,
                    self.utilizador["id_utilizador"]
                )
                messagebox.showinfo("Sucesso", "Evento atualizado!")
            else:
                criar_evento(titulo, descricao, data_evento, hora_evento, local, self.utilizador["id_utilizador"])
                messagebox.showinfo("Sucesso", "Evento criado!")

            self._limpar_formulario()
            self._listar_eventos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao guardar evento:\n{e}")

    def _remover_evento(self):
        if not self.evento_selecionado:
            messagebox.showwarning("Atenção", "Seleciona um evento primeiro.")
            return

        if messagebox.askyesno("Confirmar", "Tens a certeza que queres remover este evento?"):
            try:
                remover_evento(self.evento_selecionado["id_evento"])
                messagebox.showinfo("Sucesso", "Evento removido!")
                self._limpar_formulario()
                self._listar_eventos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover evento:\n{e}")

    def _limpar_formulario(self):
        self.evento_selecionado = None
        self.entry_titulo.delete(0, "end")
        self.entry_descricao.delete(0, "end")
        self.entry_hora.delete(0, "end")
        self.entry_local.delete(0, "end")
