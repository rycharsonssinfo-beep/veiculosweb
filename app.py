"""Ponto de entrada compatível com a implantação original no Streamlit Cloud.

O Streamlit executa este arquivo novamente em cada interação do usuário.
Utilizamos runpy.run_path para executar a interface de main.py a cada rerun.
Um 'from main import *' reutilizaria o módulo em cache e deixaria a tela vazia.
"""

from pathlib import Path
import runpy

ARQUIVO_PRINCIPAL = Path(__file__).resolve().with_name("main.py")
runpy.run_path(str(ARQUIVO_PRINCIPAL), run_name="__main__")
