"""Execucao de tarefas bloqueantes (indexacao semantica, busca por
sentido) em segundo plano, sem travar a interface.

O documento fundador do projeto ja dizia, desde a v1: "Toda
importacao/indexacao roda numa thread separada... Evita travar a
interface." Isso nunca foi implementado de fato -- so existia um
threading.Lock em EmbeddingService (protege o modelo compartilhado
contra uso concorrente, o que so importa SE algo for multithread), mas
nenhum Thread real. Toda chamada a AcervoService.cadastrar/atualizar
(que indexa) e a EmbeddingService.buscar_semantico rodava direto na
thread da interface -- a mesma thread que desenha a janela e responde
a cliques. Como sentence-transformers roda inferencia de rede neural
de verdade, isso trava a janela por um instante a cada busca ou
importacao (pior no primeiro uso, quando o modelo ainda carrega).

Este modulo resolve isso com o padrao thread-de-trabalho +
fila-thread-safe + polling via widget.after(), que e a forma correta e
recomendada de tirar trabalho pesado da thread principal em Tkinter
(widgets do Tkinter nao podem ser tocados de fora da thread principal
-- por isso o resultado volta pela fila, e quem efetivamente atualiza
a tela e sempre o metodo `verificar`, rodando via `after` na thread
principal).
"""

from __future__ import annotations

import queue
import threading
from typing import Any, Callable, TypeVar

T = TypeVar("T")

INTERVALO_VERIFICACAO_MS = 50


def executar_em_segundo_plano(
    master: Any,
    tarefa: Callable[[], T],
    ao_concluir: Callable[[T], None],
    ao_falhar: Callable[[Exception], None] | None = None,
) -> None:
    """Roda `tarefa` (bloqueante) numa thread separada.

    Quando `tarefa` termina, `ao_concluir(resultado)` -- ou
    `ao_falhar(excecao)`, se ela lancar algo -- e chamado na thread
    principal (segura para mexer em widgets), via `master.after()`.

    `ao_falhar` e opcional: se omitido, uma excecao na tarefa e
    relancada na thread principal (aparece no console, nao trava
    silenciosamente).
    """
    fila: queue.Queue = queue.Queue()

    def trabalhar() -> None:
        try:
            resultado = tarefa()
        except Exception as erro:  # noqa: BLE001 - repassado, nao engolido
            fila.put(("erro", erro))
        else:
            fila.put(("sucesso", resultado))

    def verificar() -> None:
        try:
            status, valor = fila.get_nowait()
        except queue.Empty:
            master.after(INTERVALO_VERIFICACAO_MS, verificar)
            return

        if status == "sucesso":
            ao_concluir(valor)
        elif ao_falhar is not None:
            ao_falhar(valor)
        else:
            raise valor

    threading.Thread(target=trabalhar, daemon=True).start()
    master.after(INTERVALO_VERIFICACAO_MS, verificar)
