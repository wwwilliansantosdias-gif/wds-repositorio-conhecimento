"""Janela de Backup -- tela propria do MVP (Fase 8, docs/roadmap.md).

Lista os backups existentes e permite criar um novo ou restaurar um
existente, delegando toda a logica ao BackupController. Abre como
janela separada (modal), sem substituir a janela principal, seguindo
o mesmo padrao ja usado pela Lixeira e pelo Editor Markdown.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tkinter import messagebox
from typing import Any

import customtkinter as ctk

from controllers.backup_controller import BackupController


class BackupWindow(ctk.CTkToplevel):
    """Janela modal para criar e restaurar backups do Acervo."""

    def __init__(
        self,
        master: Any,
        backup_controller: BackupController,
    ) -> None:
        super().__init__(master)
        self.transient(master)
        self.lift()
        self.focus_force()
        self.grab_set()
        self.title("Backup")
        self.geometry("560x600")
        self._controller = backup_controller

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=(
                "Um backup contem uma copia completa do banco de dados, "
                "dos arquivos do acervo e do indice de busca por sentido."
            ),
            text_color="gray60",
            justify="left",
            wraplength=520,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        ctk.CTkButton(
            self,
            text="Criar backup agora",
            height=36,
            command=self._criar_backup,
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))

        self._lista_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._lista_scroll.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self._lista_scroll.grid_columnconfigure(0, weight=1)

        self._atualizar_lista()

    def _atualizar_lista(self) -> None:
        for widget in self._lista_scroll.winfo_children():
            widget.destroy()

        backups = self._controller.listar_backups()

        if not backups:
            ctk.CTkLabel(
                self._lista_scroll,
                text="Nenhum backup foi criado ainda.",
                text_color="gray60",
            ).grid(row=0, column=0, pady=40)
            return

        for indice, caminho in enumerate(backups):
            item = self._criar_item_backup(caminho)
            item.grid(row=indice, column=0, sticky="ew", pady=(0, 8))

    def _criar_item_backup(self, caminho: Path) -> ctk.CTkFrame:
        item = ctk.CTkFrame(self._lista_scroll, fg_color="gray17", corner_radius=8)
        item.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            item,
            text=self._rotulo_data(caminho),
            anchor="w",
            justify="left",
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 0))

        ctk.CTkLabel(
            item,
            text=self._rotulo_tamanho(caminho),
            text_color="gray60",
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

        ctk.CTkButton(
            item,
            text="Restaurar",
            width=90,
            height=28,
            fg_color="gray40",
            hover_color="gray30",
            command=lambda: self._restaurar(caminho),
        ).grid(row=0, column=1, rowspan=2, padx=12, pady=10)

        return item

    @staticmethod
    def _rotulo_data(caminho: Path) -> str:
        # wds_backup_AAAAMMDD_HHMMSS.zip
        try:
            marca = caminho.stem.replace("wds_backup_", "")
            momento = datetime.strptime(marca, "%Y%m%d_%H%M%S")
            return momento.strftime("%d/%m/%Y as %H:%M:%S")
        except ValueError:
            return caminho.name

    @staticmethod
    def _rotulo_tamanho(caminho: Path) -> str:
        try:
            tamanho_mb = caminho.stat().st_size / (1024 * 1024)
        except OSError:
            return caminho.name
        return f"{tamanho_mb:.1f} MB"

    def _criar_backup(self) -> None:
        resultado = self._controller.criar_backup()
        if not resultado.sucesso:
            messagebox.showerror("Nao foi possivel criar o backup", resultado.mensagem_erro)
            return
        messagebox.showinfo(
            "Backup criado", f"Backup salvo em:\n{resultado.caminho}"
        )
        self._atualizar_lista()

    def _restaurar(self, caminho: Path) -> None:
        confirmar = messagebox.askyesno(
            "Restaurar backup",
            "Isso vai substituir o banco de dados, o acervo e o indice de "
            "busca atuais pelo conteudo deste backup. Um estado de "
            "seguranca do que existe agora e guardado automaticamente e "
            "so e descartado se a restauracao terminar com sucesso.\n\n"
            "Deseja continuar?",
        )
        if not confirmar:
            return

        resultado = self._controller.restaurar_backup(caminho)
        if not resultado.sucesso:
            messagebox.showerror(
                "Nao foi possivel restaurar", resultado.mensagem_erro
            )
            return

        messagebox.showinfo(
            "Backup restaurado",
            "O backup foi restaurado com sucesso. Feche e abra o WDS "
            "novamente para que a janela principal reflita os dados "
            "restaurados.",
        )
        self.destroy()
