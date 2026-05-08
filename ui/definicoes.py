import customtkinter as ctk
from tkinter import messagebox
from configparser import ConfigParser
from pathlib import Path


class JanelaDefinicoes(ctk.CTkToplevel):
    def __init__(self, utilizador):
        super().__init__()

        self.utilizador = utilizador
        self.config_path = Path("config.ini")

        self.title("Definições")
        self.geometry("500x400")
        self.resizable(False, False)

        self._criar_interface()

    def _criar_interface(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=35, pady=30)

        ctk.CTkLabel(
            frame,
            text="⚙️ Definições",
            font=("Arial", 24, "bold")
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            frame,
            text=f"Utilizador: {self.utilizador.get('nome', '')}",
            font=("Arial", 14),
            text_color="gray"
        ).pack(pady=(0, 25))

        ctk.CTkLabel(frame, text="Tema da aplicação", anchor="w").pack(fill="x", pady=(10, 5))

        self.combo_tema = ctk.CTkComboBox(
            frame,
            width=300,
            values=["dark", "light", "system"]
        )
        self.combo_tema.set(self._obter_tema_atual())
        self.combo_tema.pack(pady=(0, 20))

        ctk.CTkButton(
            frame,
            text="💾 Guardar Definições",
            width=300,
            height=40,
            fg_color="#22c55e",
            command=self._guardar_definicoes
        ).pack(pady=10)

        ctk.CTkLabel(
            frame,
            text="Nota: para veres o tema aplicado em toda a app,\nfecha e abre novamente o programa.",
            font=("Arial", 12),
            text_color="gray"
        ).pack(pady=20)

    def _obter_tema_atual(self):
        config = ConfigParser()
        config.read(self.config_path)

        if config.has_section("app"):
            return config.get("app", "theme", fallback="dark")

        return "dark"

    def _guardar_definicoes(self):
        tema = self.combo_tema.get()

        config = ConfigParser()
        config.read(self.config_path)

        if not config.has_section("app"):
            config.add_section("app")

        config.set("app", "theme", tema)

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                config.write(f)

            ctk.set_appearance_mode(tema)
            messagebox.showinfo("Sucesso", "Definições guardadas!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao guardar definições:\n{e}")
