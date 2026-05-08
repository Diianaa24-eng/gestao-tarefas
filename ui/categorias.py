import customtkinter as ctk
from tkinter import messagebox
from db import listar_categorias, criar_categoria, atualizar_categoria, remover_categoria
from utils.validators import validar_campos_obrigatorios


class JanelaCategorias(ctk.CTkToplevel):
    def __init__(self, utilizador):
        super().__init__()

        self.utilizador = utilizador
        self.categoria_selecionada = None

        self.title("Gestão de Categorias")
        self.geometry("800x600")

        self._criar_interface()
        self._listar_categorias()

    def _criar_interface(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        frame_form = ctk.CTkFrame(self)
        frame_form.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(frame_form, text="Nova Categoria", font=("Arial", 18, "bold")).pack(pady=(15, 20))

        ctk.CTkLabel(frame_form, text="Nome *", anchor="w").pack(fill="x", padx=20, pady=(10, 2))
        self.entry_nome = ctk.CTkEntry(frame_form, width=260)
        self.entry_nome.pack(padx=20, pady=(0, 10))

        ctk.CTkButton(
            frame_form,
            text="💾 Guardar",
            width=260,
            fg_color="#22c55e",
            command=self._guardar_categoria
        ).pack(padx=20, pady=(15, 8))

        ctk.CTkButton(
            frame_form,
            text="🗑️ Remover",
            width=260,
            fg_color="#ef4444",
            command=self._remover_categoria
        ).pack(padx=20, pady=8)

        ctk.CTkButton(
            frame_form,
            text="🧹 Limpar",
            width=260,
            fg_color="#64748b",
            command=self._limpar_formulario
        ).pack(padx=20, pady=8)

        frame_lista = ctk.CTkFrame(self)
        frame_lista.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(frame_lista, text="As Tuas Categorias", font=("Arial", 18, "bold")).pack(pady=15)

        self.frame_categorias = ctk.CTkScrollableFrame(frame_lista, height=450)
        self.frame_categorias.pack(fill="both", expand=True, padx=15, pady=10)

    def _listar_categorias(self):
        for widget in self.frame_categorias.winfo_children():
            widget.destroy()

        categorias = listar_categorias(self.utilizador["id_utilizador"])

        if not categorias:
            ctk.CTkLabel(self.frame_categorias, text="Nenhuma categoria encontrada", text_color="gray").pack(pady=50)
            return

        for categoria in categorias:
            self._criar_card_categoria(categoria)

    def _criar_card_categoria(self, categoria):
        card = ctk.CTkFrame(self.frame_categorias, fg_color="#1e293b", corner_radius=10)
        card.pack(fill="x", pady=6)

        ctk.CTkFrame(card, width=5, fg_color="#6366f1", corner_radius=0).pack(side="left", fill="y")

        label = ctk.CTkLabel(
            card,
            text=f"📂 {categoria['nome']}",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        label.pack(fill="x", padx=15, pady=14)

        for widget in [card, label]:
            widget.bind("<Button-1>", lambda e, c=categoria: self._selecionar_categoria(c))

    def _selecionar_categoria(self, categoria):
        self.categoria_selecionada = categoria
        self.entry_nome.delete(0, "end")
        self.entry_nome.insert(0, categoria.get("nome", ""))

    def _guardar_categoria(self):
        nome = self.entry_nome.get().strip()

        valido, msg = validar_campos_obrigatorios(Nome=nome)
        if not valido:
            messagebox.showwarning("Atenção", msg)
            return

        try:
            if self.categoria_selecionada:
                atualizar_categoria(
                    self.categoria_selecionada["id_categoria"],
                    nome,
                    self.utilizador["id_utilizador"]
                )
                messagebox.showinfo("Sucesso", "Categoria atualizada!")
            else:
                criar_categoria(nome, self.utilizador["id_utilizador"])
                messagebox.showinfo("Sucesso", "Categoria criada!")

            self._limpar_formulario()
            self._listar_categorias()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao guardar categoria:\n{e}")

    def _remover_categoria(self):
        if not self.categoria_selecionada:
            messagebox.showwarning("Atenção", "Seleciona uma categoria primeiro.")
            return

        if messagebox.askyesno(
            "Confirmar",
            "Tens a certeza que queres remover esta categoria?\nAs tarefas desta categoria também serão removidas."
        ):
            try:
                remover_categoria(self.categoria_selecionada["id_categoria"])
                messagebox.showinfo("Sucesso", "Categoria removida!")
                self._limpar_formulario()
                self._listar_categorias()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover categoria:\n{e}")

    def _limpar_formulario(self):
        self.categoria_selecionada = None
        self.entry_nome.delete(0, "end")
