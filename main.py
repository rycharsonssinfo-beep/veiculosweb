# -*- coding: utf-8 -*-
"""Painel de Acessos — Sistema de Veículos | Grupo S&S Informática.

Todo o cadastro, a interface e as funções da aplicação estão neste arquivo.
O projeto não armazena senhas, dados de autenticação nem informações de sessão
em banco de dados. Favoritos e recentes permanecem apenas na aba do navegador.
"""

# ==================================================
# 1. IMPORTAÇÕES E CONFIGURAÇÃO DA PÁGINA
# ==================================================
from collections import Counter, defaultdict
from html import escape
from pathlib import Path
from urllib.parse import urlparse
import unicodedata

import streamlit as st

st.set_page_config(
    page_title="Painel de Acessos | Sistema de Veículos",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==================================================
# 2. IDENTIDADE VISUAL E ESTILIZAÇÃO CSS
# ==================================================
# A detecção de tema considera a seleção no menu do próprio Streamlit,
# não somente a preferência de cores do sistema operacional.
try:
    TEMA_ESCURO = st.context.theme.type == "dark"
except (AttributeError, RuntimeError):
    TEMA_ESCURO = False

CSS_BASE = r"""
:root {
  --ss-primary:#006b6d; --ss-primary-hover:#005254;
  --ss-bg:#f6f9f9; --ss-surface:#ffffff; --ss-soft:#e9f5f3;
  --ss-text:#183a3d; --ss-muted:#546d70; --ss-line:#dbe8e6;
  --ss-badge:#eaf3f2; --ss-badge-text:#236366;
  --ss-shadow:0 3px 16px rgba(12,69,70,.055);
}
html,body,[data-testid="stAppViewContainer"] {background:var(--ss-bg)!important;}
[data-testid="stHeader"] {background:var(--ss-bg)!important;}
.block-container {max-width:1440px;padding-top:.7rem;padding-bottom:2rem;}
#MainMenu,footer {visibility:hidden;}
.ss-brand {padding:.12rem 0 .1rem;}
.ss-kicker {text-transform:uppercase;letter-spacing:.14em;color:#007679;font-size:.72rem;font-weight:800;}
.ss-title {font-size:clamp(1.75rem,3vw,2.55rem);font-weight:800;letter-spacing:-.045em;color:var(--ss-text);line-height:1.13;margin:5px 0;}
.ss-subtitle {font-size:.99rem;font-weight:650;color:var(--ss-primary);margin:0;}
.ss-description {font-size:.88rem;color:var(--ss-muted);margin:7px 0 0;}
.ss-rule {height:1px;background:var(--ss-line);margin:12px 0 16px;}
.ss-metrics {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-bottom:20px;}
.ss-metric {display:flex;align-items:center;gap:13px;background:var(--ss-surface);border:1px solid var(--ss-line);border-radius:14px;padding:15px 18px;box-shadow:var(--ss-shadow);min-width:0;}
.ss-metric-icon {width:40px;height:40px;display:flex;align-items:center;justify-content:center;color:var(--ss-primary);background:var(--ss-soft);border-radius:11px;flex-shrink:0;}
.ss-metric-icon svg {width:22px;height:22px;stroke:currentColor;}
.ss-metric-label {font-size:.78rem;color:var(--ss-muted);font-weight:600;}
.ss-metric-value {font-size:1.7rem;font-weight:800;line-height:1.05;color:var(--ss-text);font-variant-numeric:tabular-nums;}
.ss-section-head {display:flex;align-items:baseline;justify-content:space-between;gap:10px;flex-wrap:wrap;margin:10px 0 9px;}
.ss-section-head h2 {font-size:1.12rem;letter-spacing:-.017em;color:var(--ss-text);margin:0;font-weight:760;}
.ss-section-head p {font-size:.81rem;color:var(--ss-muted);margin:0;}
.ss-results-meta {margin:4px 0 12px;color:var(--ss-muted);font-size:.82rem;}
.ss-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:12px 0;}
.ss-card {display:flex;flex-direction:column;min-width:0;background:var(--ss-surface);border:1px solid var(--ss-line);border-radius:14px;padding:14px;min-height:172px;box-shadow:var(--ss-shadow);transition:box-shadow .15s,border-color .15s,transform .15s;}
.ss-card:hover {border-color:#8dbfbc;box-shadow:0 9px 22px rgba(10,72,73,.12);transform:translateY(-2px);}
.ss-card--pending {border-style:dashed;}
.ss-card-top {display:flex;align-items:center;justify-content:space-between;gap:6px;margin-bottom:9px;}
.ss-card-icon {width:31px;height:31px;display:flex;align-items:center;justify-content:center;border-radius:9px;background:var(--ss-soft);color:var(--ss-primary);flex-shrink:0;}
.ss-card-icon svg {width:18px;height:18px;stroke:currentColor;}
.ss-tag {font-size:.69rem;font-weight:700;border-radius:100px;background:var(--ss-badge);color:var(--ss-badge-text);padding:4px 8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.ss-fav {width:32px;height:32px;border:1px solid transparent;background:transparent;color:var(--ss-muted);border-radius:8px;cursor:pointer;font-size:1.5rem;line-height:1;}
.ss-fav:hover,.ss-fav[aria-pressed="true"] {background:var(--ss-soft);color:var(--ss-primary);}
.ss-card-title {font-size:.92rem;font-weight:750;color:var(--ss-text);line-height:1.38;margin:0 0 6px;overflow-wrap:anywhere;}
.ss-card-city {font-size:.79rem;color:var(--ss-muted);margin:0 0 11px;}
.ss-grow {flex:1;min-height:8px;}
.ss-actions {display:flex;gap:7px;align-items:center;}
.ss-link {display:inline-flex;align-items:center;justify-content:center;gap:6px;flex:1;min-height:43px;padding:6px 12px;background:var(--ss-primary);color:white!important;text-decoration:none!important;border-radius:9px;font-size:.82rem;font-weight:750;box-sizing:border-box;}
.ss-link:hover {background:var(--ss-primary-hover);color:white!important;}
.ss-link svg {width:15px;height:15px;stroke:currentColor;flex-shrink:0;}
.ss-copy {min-height:43px;width:43px;display:inline-flex;align-items:center;justify-content:center;border:1px solid var(--ss-line);color:var(--ss-primary);background:var(--ss-surface);border-radius:9px;cursor:pointer;}
.ss-copy svg {height:17px;width:17px;stroke:currentColor;}
.ss-copy:hover {background:var(--ss-soft);}
.ss-no-link {width:100%;min-height:43px;border-radius:9px;display:inline-flex;align-items:center;justify-content:center;background:var(--ss-bg);border:1px dashed var(--ss-line);color:var(--ss-muted);font-size:.80rem;}
.ss-group {margin:18px 0 22px;}
.ss-group-title {font-weight:760;font-size:.95rem;color:var(--ss-text);margin:0 0 6px;}
.ss-group-title small {color:var(--ss-muted);font-weight:500;font-size:.76rem;}
.ss-toolbar {display:flex;align-items:center;justify-content:space-between;gap:9px;flex-wrap:wrap;margin-top:6px;}
.ss-fav-filter {background:var(--ss-surface);color:var(--ss-text);border:1px solid var(--ss-line);border-radius:9px;padding:8px 13px;font-size:.82rem;font-weight:680;cursor:pointer;min-height:42px;}
.ss-fav-filter[aria-pressed="true"] {background:var(--ss-soft);border-color:var(--ss-primary);color:var(--ss-primary);}
.ss-recent {margin:13px 0 12px;display:none;}
.ss-recent-label {font-size:.79rem;color:var(--ss-muted);font-weight:650;margin-bottom:8px;}
.ss-recent-links {display:flex;gap:7px;flex-wrap:wrap;}
.ss-recent-link {display:inline-flex;min-height:35px;align-items:center;border:1px solid var(--ss-line);border-radius:50px;padding:5px 11px;color:var(--ss-text)!important;background:var(--ss-surface);text-decoration:none!important;font-size:.79rem;}
.ss-recent-link:hover {background:var(--ss-soft);}
.ss-empty {border:1px dashed var(--ss-line);border-radius:13px;background:var(--ss-surface);padding:24px 18px;color:var(--ss-muted);text-align:center;font-size:.89rem;}
.ss-hidden {display:none!important;}
.ss-toast {position:fixed;bottom:20px;right:22px;background:#144849;color:white;border-radius:9px;box-shadow:0 8px 24px rgba(0,0,0,.21);padding:10px 14px;z-index:1000;font-size:.85rem;display:none;}
.ss-footer {margin:24px 0 0;padding:16px 0 6px;border-top:1px solid var(--ss-line);font-size:.79rem;color:var(--ss-muted);text-align:center;}
.ss-accessibility-note {font-size:.74rem;color:var(--ss-muted);margin-top:2px;}
.ss-fav:focus-visible,.ss-copy:focus-visible,.ss-link:focus-visible,.ss-fav-filter:focus-visible,.ss-recent-link:focus-visible {outline:3px solid #55b9b4;outline-offset:2px;}
div[data-testid="stTextInput"] input {background:var(--ss-surface);color:var(--ss-text);min-height:46px;border-radius:11px;border-color:var(--ss-line);}
div[data-testid="stTextInput"] input::placeholder {color:var(--ss-muted);}
div[data-testid="stTextInput"] input:focus {border-color:var(--ss-primary);box-shadow:0 0 0 1px var(--ss-primary);}
@media (max-width:1100px) {.ss-grid {grid-template-columns:repeat(3,minmax(0,1fr));}}
@media (max-width:790px) {.ss-grid {grid-template-columns:repeat(2,minmax(0,1fr));}.ss-metrics {gap:8px;}.ss-metric {padding:11px 13px;}}
@media (max-width:560px) {
  .block-container {padding-left:1rem;padding-right:1rem;padding-top:.35rem;}
  .ss-grid {grid-template-columns:1fr;gap:10px;}
  .ss-metrics {grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;}
  .ss-metric {display:block;padding:10px 9px;border-radius:11px;}
  .ss-metric-icon {width:28px;height:28px;margin-bottom:7px;}
  .ss-metric-icon svg {width:17px;height:17px;}
  .ss-metric-label {font-size:.68rem;line-height:1.2;}
  .ss-metric-value {font-size:1.45rem;}
  .ss-card {min-height:154px;}
  .ss-title {font-size:1.7rem;}
  .ss-toast {left:12px;right:12px;bottom:12px;}
}
@media (prefers-reduced-motion:reduce) {.ss-card {transition:none;}.ss-card:hover {transform:none;}}
"""
CSS_DARK = r"""
:root {
 --ss-primary:#18979a;--ss-primary-hover:#0e8083;
 --ss-bg:#101e21;--ss-surface:#1c3034;--ss-soft:#29474b;
 --ss-text:#e9f5f4;--ss-muted:#b4cccd;--ss-line:#395458;
 --ss-badge:#29484c;--ss-badge-text:#d0e9e9;
 --ss-shadow:0 4px 18px rgba(0,0,0,.15);
}
.ss-link {background:#087c80;color:#fff!important;}
div[data-testid="stImage"] {background:#ffffff;padding:6px;border-radius:10px;width:max-content;max-width:100%;}
.ss-link:hover {background:#06686c;}
.ss-kicker {color:#77cecb;}
"""
st.html('<style>'+CSS_BASE+(CSS_DARK if TEMA_ESCURO else '')+'</style>')

# ==================================================
# 3. CADASTRO DE ENTIDADES E LINKS
# ==================================================
# Edite esta lista para acrescentar, remover ou atualizar entidades.
# Não invente URL para registros pendentes: mantenha url="" até confirmar.
# Categorias aceitas: Prefeituras, Câmaras, Consórcios, Institutos, SAAEs.
ENTIDADES = [
    {
        "nome": "Prefeitura Municipal de Abaiara",
        "municipio": "Abaiara",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Abaiara"
    },
    {
        "nome": "Prefeitura Municipal de Acopiara",
        "municipio": "Acopiara",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Acopiara"
    },
    {
        "nome": "Prefeitura Municipal de Amontada",
        "municipio": "Amontada",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Amontada"
    },
    {
        "nome": "Prefeitura Municipal de Araripe",
        "municipio": "Araripe",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Araripe"
    },
    {
        "nome": "Prefeitura Municipal de Aratuba",
        "municipio": "Aratuba",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Aratuba"
    },
    {
        "nome": "Prefeitura Municipal de Arneiroz",
        "municipio": "Arneiroz",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Arneiroz"
    },
    {
        "nome": "Prefeitura Municipal de Barbalha",
        "municipio": "Barbalha",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Barbalha"
    },
    {
        "nome": "Prefeitura Municipal de Barreira",
        "municipio": "Barreira",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Barreira"
    },
    {
        "nome": "Prefeitura Municipal de Baturite",
        "municipio": "Baturite",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Baturite"
    },
    {
        "nome": "Prefeitura Municipal de Campos Sales",
        "municipio": "Campos Sales",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/CamposSales"
    },
    {
        "nome": "Prefeitura Municipal de Caridade",
        "municipio": "Caridade",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Caridade"
    },
    {
        "nome": "Prefeitura Municipal de Caucaia",
        "municipio": "Caucaia",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Caucaia"
    },
    {
        "nome": "Prefeitura Municipal de Cedro",
        "municipio": "Cedro",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Cedro"
    },
    {
        "nome": "Prefeitura Municipal de Cedro - Pernambuco",
        "municipio": "Cedro - Pernambuco",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/CedroPe"
    },
    {
        "nome": "Prefeitura Municipal de Crateus",
        "municipio": "Crateus",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Crateus"
    },
    {
        "nome": "Prefeitura Municipal de Cruz",
        "municipio": "Cruz",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Cruz"
    },
    {
        "nome": "Prefeitura Municipal de Eusebio",
        "municipio": "Eusebio",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Eusebio"
    },
    {
        "nome": "Prefeitura Municipal de Farias Brito",
        "municipio": "Farias Brito",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/FariasBrito"
    },
    {
        "nome": "Prefeitura Municipal de Granjeiro",
        "municipio": "Granjeiro",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Granjeiro"
    },
    {
        "nome": "Prefeitura Municipal de Guaramiranga",
        "municipio": "Guaramiranga",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Guaramiranga"
    },
    {
        "nome": "Prefeitura Municipal de Hidrolândia",
        "municipio": "Hidrolândia",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Hidrolandia"
    },
    {
        "nome": "Prefeitura Municipal de Itaiçaba",
        "municipio": "Itaiçaba",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Itaicaba"
    },
    {
        "nome": "Prefeitura Municipal de Itaitinga",
        "municipio": "Itaitinga",
        "categoria": "Prefeituras",
        "url": ""
    },
    {
        "nome": "Prefeitura Municipal de Itapiuna",
        "municipio": "Itapiuna",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Itapiuna"
    },
    {
        "nome": "Prefeitura Municipal de Jaguaribe",
        "municipio": "Jaguaribe",
        "categoria": "Prefeituras",
        "url": ""
    },
    {
        "nome": "Prefeitura Municipal de Jardim",
        "municipio": "Jardim",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Jardim"
    },
    {
        "nome": "Prefeitura Municipal de Jati",
        "municipio": "Jati",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Jati"
    },
    {
        "nome": "Prefeitura Municipal de Maranguape",
        "municipio": "Maranguape",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Maranguape"
    },
    {
        "nome": "Prefeitura Municipal de Martinópole",
        "municipio": "Martinópole",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Martinopole"
    },
    {
        "nome": "Prefeitura Municipal de Nova Russas",
        "municipio": "Nova Russas",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/NovaRussas"
    },
    {
        "nome": "Prefeitura Municipal de Oros",
        "municipio": "Oros",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Oros"
    },
    {
        "nome": "Prefeitura Municipal de Palhano",
        "municipio": "Palhano",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Palhano"
    },
    {
        "nome": "Prefeitura Municipal de Palmácia",
        "municipio": "Palmácia",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Palmacia"
    },
    {
        "nome": "Prefeitura Municipal de Paracuru",
        "municipio": "Paracuru",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Paracuru"
    },
    {
        "nome": "Prefeitura Municipal de Paraipaba",
        "municipio": "Paraipaba",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Paraipaba"
    },
    {
        "nome": "Prefeitura Municipal de Paramoti",
        "municipio": "Paramoti",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Paramoti"
    },
    {
        "nome": "Prefeitura Municipal de Pedra Branca",
        "municipio": "Pedra Branca",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/PedraBranca"
    },
    {
        "nome": "Prefeitura Municipal de Pereiro",
        "municipio": "Pereiro",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Pereiro"
    },
    {
        "nome": "Prefeitura Municipal de Porteiras",
        "municipio": "Porteiras",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Porteiras"
    },
    {
        "nome": "Prefeitura Municipal de Quiterianópolis",
        "municipio": "Quiterianópolis",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Quiterianopolis"
    },
    {
        "nome": "Prefeitura Municipal de Quixelô",
        "municipio": "Quixelô",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Quixelo"
    },
    {
        "nome": "Prefeitura Municipal de Redenção",
        "municipio": "Redenção",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Redencao"
    },
    {
        "nome": "Prefeitura Municipal de Santa Quitéria",
        "municipio": "Santa Quitéria",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/SantaQuiteria"
    },
    {
        "nome": "Prefeitura Municipal de Sobral",
        "municipio": "Sobral",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Sobral"
    },
    {
        "nome": "Prefeitura Municipal de Tabuleiro do Norte",
        "municipio": "Tabuleiro do Norte",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/TabuleirodoNorte"
    },
    {
        "nome": "Prefeitura Municipal de Tarrafas",
        "municipio": "Tarrafas",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Tarrafas"
    },
    {
        "nome": "Prefeitura Municipal de Tururu",
        "municipio": "Tururu",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/Tururu"
    },
    {
        "nome": "Prefeitura Municipal de Várzea Alegre",
        "municipio": "Várzea Alegre",
        "categoria": "Prefeituras",
        "url": "https://ssveiculos.ssinformatica.net/VarzeaAlegre"
    },
    {
        "nome": "Câmara Municipal de Acaraú",
        "municipio": "Acaraú",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMAcarau"
    },
    {
        "nome": "Câmara Municipal de Amontada",
        "municipio": "Amontada",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMAmontada"
    },
    {
        "nome": "Câmara Municipal de Aratuba",
        "municipio": "Aratuba",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMAratuba"
    },
    {
        "nome": "Câmara Municipal de Arneiroz",
        "municipio": "Arneiroz",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMArneiroz"
    },
    {
        "nome": "Câmara Municipal de Banabuiú",
        "municipio": "Banabuiú",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMBanabuiu"
    },
    {
        "nome": "Câmara Municipal de Barreira",
        "municipio": "Barreira",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMBarreira"
    },
    {
        "nome": "Câmara Municipal do Crato",
        "municipio": "Crato",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMCrato"
    },
    {
        "nome": "Câmara Municipal de Cruz",
        "municipio": "Cruz",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMCruz"
    },
    {
        "nome": "Câmara Municipal de Farias Brito",
        "municipio": "Farias Brito",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMFariasBrito"
    },
    {
        "nome": "Câmara Municipal de General Sampaio",
        "municipio": "General Sampaio",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMGeneralSampaio"
    },
    {
        "nome": "Câmara Municipal de Guaraciaba do Norte",
        "municipio": "Guaraciaba do Norte",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMGuaraciabaNorte"
    },
    {
        "nome": "Câmara Municipal de Guaramiranga",
        "municipio": "Guaramiranga",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMGuaramiranga"
    },
    {
        "nome": "Câmara Municipal de Itaiçaba",
        "municipio": "Itaiçaba",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMItaicaba"
    },
    {
        "nome": "Câmara Municipal de Itapiuna",
        "municipio": "Itapiuna",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMItapiuna"
    },
    {
        "nome": "Câmara Municipal de Jardim",
        "municipio": "Jardim",
        "categoria": "Câmaras",
        "url": ""
    },
    {
        "nome": "Câmara Municipal de Maranguape",
        "municipio": "Maranguape",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMMaranguape"
    },
    {
        "nome": "Câmara Municipal de Nova Russas",
        "municipio": "Nova Russas",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMNovaRussas"
    },
    {
        "nome": "Câmara Municipal de Oros",
        "municipio": "Oros",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMOros"
    },
    {
        "nome": "Câmara Municipal de Palmácia",
        "municipio": "Palmácia",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMPalmacia"
    },
    {
        "nome": "Câmara Municipal de Paracuru",
        "municipio": "Paracuru",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMParacuru"
    },
    {
        "nome": "Câmara Municipal de Paraipaba",
        "municipio": "Paraipaba",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMParaipaba"
    },
    {
        "nome": "Câmara Municipal de Pereiro",
        "municipio": "Pereiro",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMPereiro"
    },
    {
        "nome": "Câmara Municipal de Quiterianópolis",
        "municipio": "Quiterianópolis",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMQuiterianopolis"
    },
    {
        "nome": "Câmara Municipal de Quixelô",
        "municipio": "Quixelô",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMQuixelo"
    },
    {
        "nome": "Câmara Municipal de Sobral",
        "municipio": "Sobral",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMSobral"
    },
    {
        "nome": "Câmara Municipal de Tabuleiro do Norte",
        "municipio": "Tabuleiro do Norte",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMTabuleiroDoNorte"
    },
    {
        "nome": "Câmara Municipal de Várzea Alegre",
        "municipio": "Várzea Alegre",
        "categoria": "Câmaras",
        "url": "https://ssveiculos.ssinformatica.net/CMVarzeaAlegre"
    },
    {
        "nome": "Consórcio Ass. Púb. dos Mun do Maciço de Baturité P/ Saneamento Amb-AMSA",
        "municipio": "Não informado",
        "categoria": "Consórcios",
        "url": "https://ssveiculos.ssinformatica.net/CAPMBaturite"
    },
    {
        "nome": "Consórcio PUB. de Manejo dos R. Solidos do Vale do Jaguaribe -CONVALE",
        "municipio": "Não informado",
        "categoria": "Consórcios",
        "url": ""
    },
    {
        "nome": "Consórcio Intermunicipal de Gestão Integrada de Resíduos Sólidos- COMARES",
        "municipio": "Não informado",
        "categoria": "Consórcios",
        "url": ""
    },
    {
        "nome": "Consórcio PUB. de Man dos Resi. Solidos da Regiao Cariri Oriental",
        "municipio": "Não informado",
        "categoria": "Consórcios",
        "url": ""
    },
    {
        "nome": "Consórcio Público de Manejo de Resíduos Sólidos de Pacajus",
        "municipio": "Pacajus",
        "categoria": "Consórcios",
        "url": "https://ssveiculos.ssinformatica.net/CPMRSRMBPacajus"
    },
    {
        "nome": "Consórcio Público de Saúde da Microrregião do Crato",
        "municipio": "Não informado",
        "categoria": "Consórcios",
        "url": "https://ssveiculos.ssinformatica.net/CPSCrato"
    },
    {
        "nome": "Fundo de Previdência do Municipio de Palmácia",
        "municipio": "Palmácia",
        "categoria": "Institutos",
        "url": ""
    },
    {
        "nome": "Instituto de Previdência do Municipio de Caucaia",
        "municipio": "Caucaia",
        "categoria": "Institutos",
        "url": "https://ssveiculos.ssinformatica.net/IPMCaucaia"
    },
    {
        "nome": "Instituto de Previdência dos Servidores Públicos do MUN. de Santa Quitéria",
        "municipio": "Santa Quitéria",
        "categoria": "Institutos",
        "url": "https://ssveiculos.ssinformatica.net/IPSSantaQuiteria"
    },
    {
        "nome": "Serviço Autônomo de Água e Esgoto de Banabuiú",
        "municipio": "Banabuiú",
        "categoria": "SAAEs",
        "url": "https://ssveiculos.ssinformatica.net/SaaeBanabuiu"
    },
    {
        "nome": "Serviço Autônomo de Água e Esgoto de Jaguaribe",
        "municipio": "Jaguaribe",
        "categoria": "SAAEs",
        "url": "https://ssveiculos.ssinformatica.net/SAAEJaguaribe"
    },
    {
        "nome": "Serviço Autônomo de Água e Esgoto de Quixelô",
        "municipio": "Quixelô",
        "categoria": "SAAEs",
        "url": "https://ssveiculos.ssinformatica.net/SaaeQuixelo"
    },
    {
        "nome": "Serviço Autônomo de Água e Esgoto-SAAE/Sobral",
        "municipio": "Sobral",
        "categoria": "SAAEs",
        "url": "https://ssveiculos.ssinformatica.net/SaaeSobral"
    },
    {
        "nome": "Serviço Autônomo de Água e Esgoto de Nova Russas",
        "municipio": "Nova Russas",
        "categoria": "SAAEs",
        "url": "https://ssveiculos.ssinformatica.net/SaaeNovaRussas"
    }
]

# URLs recebidas no TXT mas não atribuídas com segurança a uma das 89 entidades.
# Não aparecem como botões de acesso municipal até validação humana.
URLS_EM_CONFERENCIA = [
    {
        "url": "https://ssveiculos.ssinformatica.net/Acarau",
        "slug": "Acarau"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/Aquiraz",
        "slug": "Aquiraz"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/Aracoiaba",
        "slug": "Aracoiaba"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/Assare",
        "slug": "Assare"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/Choro",
        "slug": "Choro"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/CMErere",
        "slug": "CMErere"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/CMFortaleza",
        "slug": "CMFortaleza"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/CMGuaiuba",
        "slug": "CMGuaiuba"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/CMIraucuba",
        "slug": "CMIraucuba"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/CPRAltoJaguaribe",
        "slug": "CPRAltoJaguaribe"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/CPSAraripe",
        "slug": "CPSAraripe"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/CPSBrejoSanto",
        "slug": "CPSBrejoSanto"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/CPSCascavel",
        "slug": "CPSCascavel"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/GuaraciabaNorte",
        "slug": "GuaraciabaNorte"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/HidrolandiaRecuperado",
        "slug": "HidrolandiaRecuperado"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/Ipueiras",
        "slug": "Ipueiras"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/Iracema",
        "slug": "Iracema"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/Jaguaruana",
        "slug": "Jaguaruana"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/Morrinhos",
        "slug": "Morrinhos"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/Pacoti",
        "slug": "Pacoti"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/Potiretama",
        "slug": "Potiretama"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/SaaePedraBranca",
        "slug": "SaaePedraBranca"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/SSInformatica",
        "slug": "SSInformatica"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/Treinamento",
        "slug": "Treinamento"
    },
    {
        "url": "https://ssveiculos.ssinformatica.net/Ubajara",
        "slug": "Ubajara"
    }
]

CATEGORIAS = ["Prefeituras", "Câmaras", "Consórcios", "Institutos", "SAAEs"]


# ==================================================
# 4. ÍCONES, VALIDAÇÕES E FUNÇÕES AUXILIARES
# ==================================================
ICONES = {
    "Todas": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    "Prefeituras": '<path d="M3 21h18M5 21V9l7-5 7 5v12M9 21v-7h6v7M8 10h1M15 10h1"/>',
    "Câmaras": '<path d="M3 21h18M5 21V9h14v12M9 21v-5h6v5M5 9l7-5 7 5M9 12h1M14 12h1"/>',
    "Consórcios": '<circle cx="12" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="M11 7 6 17M13 7l5 10M7 19h10"/>',
    "Institutos": '<path d="m3 9 9-6 9 6M4 10h16M6 10v10M10 10v10M14 10v10M18 10v10M3 21h18"/>',
    "SAAEs": '<path d="M12 22a8 8 0 0 0 8-8c0-5-8-12-8-12S4 9 4 14a8 8 0 0 0 8 8Z"/><path d="M9 16a3 3 0 0 0 3 3"/>',
    "Ativos": '<path d="M20 6 9 17l-5-5"/>',
    "Pendentes": '<path d="M12 9v4m0 4h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.72 3h16.92a2 2 0 0 0 1.72-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/>',
}


def normalizar(texto):
    """Normalização com remoção de acentos, inclusive letras em maiúsculas."""
    return "".join(
        c for c in unicodedata.normalize("NFKD", str(texto or ""))
        if not unicodedata.combining(c)
    ).casefold()


def url_valida(url):
    """Somente HTTPS e domínio oficial; o caminho original não é modificado."""
    if not isinstance(url, str) or not url or any(c.isspace() for c in url):
        return False
    try:
        p = urlparse(url)
        return (
            p.scheme == "https"
            and p.hostname == "ssveiculos.ssinformatica.net"
            and not p.username and not p.password
            and not p.port
            and p.path not in ("", "/")
        )
    except ValueError:
        return False


def id_entidade(entidade):
    return "|".join(normalizar(entidade[k]) for k in ("nome", "municipio", "categoria"))


def catalogo_unico(itens):
    """Remove duplicações de entidades sem fabricar URLs."""
    unicos = {}
    for item in itens:
        chave = id_entidade(item)
        if chave not in unicos or (not unicos[chave]["url"] and item["url"]):
            unicos[chave] = item
    return list(unicos.values())


def diagnosticar(itens):
    """Validação simples para evitar regressões ao editar o cadastro."""
    problemas, nomes, urls = [], set(), set()
    obrigatorios = ("nome", "municipio", "categoria", "url")
    for indice, e in enumerate(itens, 1):
        if any(k not in e for k in obrigatorios):
            problemas.append(f"Registro {indice}: campo obrigatório ausente")
            continue
        ident = id_entidade(e)
        if ident in nomes:
            problemas.append(f"Registro repetido: {e['nome']}")
        nomes.add(ident)
        if e["categoria"] not in CATEGORIAS:
            problemas.append(f"Categoria inválida: {e['nome']}")
        if not e["nome"].strip() or not e["municipio"].strip():
            problemas.append(f"Nome ou município em branco: registro {indice}")
        if e["url"]:
            if not url_valida(e["url"]):
                problemas.append(f"URL inválida ou fora do domínio oficial: {e['nome']}")
            if e["url"] in urls:
                problemas.append(f"URL repetida: {e['url']}")
            urls.add(e["url"])
    return problemas


def svg_icone(categoria):
    corpo = ICONES.get(categoria, ICONES["Todas"])
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{corpo}</svg>'
    )


def ordem_busca(entidade, termo):
    """Correspondência exata, início de palavra e por fim ocorrências gerais."""
    nome, municipio = normalizar(entidade["nome"]), normalizar(entidade["municipio"])
    if not termo:
        prioridade = 0
    elif termo in (nome, municipio):
        prioridade = 0
    elif nome.startswith(termo) or municipio.startswith(termo):
        prioridade = 1
    elif any(p.startswith(termo) for p in nome.split() + municipio.split()):
        prioridade = 2
    else:
        prioridade = 3
    return (prioridade, nome, municipio)


def filtrar(itens, termo="", categoria="Todas", somente_com_link=False):
    termo = normalizar(termo).strip()
    filtrados = [
        e for e in itens
        if (categoria == "Todas" or e["categoria"] == categoria)
        and (not somente_com_link or url_valida(e["url"]))
        and (
            not termo or termo in normalizar(" ".join(
                (e["nome"], e["municipio"], e["categoria"])
            ))
        )
    ]
    return sorted(filtrados, key=lambda e: ordem_busca(e, termo))


def renderizar_indicadores(total, com_url, pendentes):
    dados = [
        ("Todas", "Entidades", total),
        ("Ativos", "Com link", com_url),
        ("Pendentes", "Pendentes", pendentes),
    ]
    partes = ['<div class="ss-metrics" aria-label="Resumo do cadastro">']
    for categoria, titulo, numero in dados:
        partes.append(
            '<div class="ss-metric"><div class="ss-metric-icon">'
            + svg_icone(categoria) + '</div><div><div class="ss-metric-label">'
            + escape(titulo) + '</div><div class="ss-metric-value">'
            + str(numero) + '</div></div></div>'
        )
    st.html("".join(partes) + "</div>")


def criar_card(entidade):
    """Card com URL original, favorito por sessão e cópia rápida."""
    nome = escape(entidade["nome"], quote=True)
    cidade = escape(entidade["municipio"], quote=True)
    cat = escape(entidade["categoria"].removesuffix("s"), quote=True)
    chave = escape(id_entidade(entidade), quote=True)
    url = entidade["url"]
    if url_valida(url):
        destino = escape(url, quote=True)
        acoes = (
            '<a class="ss-link" data-action="open" data-key="' + chave
            + '" data-name="' + nome + '" data-url="' + destino
            + '" href="' + destino
            + '" target="_blank" rel="noopener noreferrer">Abrir sistema '
            + '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg></a>'
            + '<button type="button" class="ss-copy" data-action="copy" '
            + 'data-url="' + destino + '" title="Copiar link" aria-label="Copiar link de '
            + nome + '"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></svg></button>'
        )
        status = ""
    else:
        acoes = '<span class="ss-no-link">Link não cadastrado</span>'
        status = " ss-card--pending"
    return (
        f'<article class="ss-card{status}" data-key="{chave}">'
        '<div class="ss-card-top"><span class="ss-card-icon">'
        + svg_icone(entidade["categoria"])
        + f'</span><span class="ss-tag">{cat}</span>'
        + f'<button type="button" class="ss-fav" data-action="favorite" data-key="{chave}" '
        + f'aria-pressed="false" aria-label="Favoritar {nome}" title="Favoritar">☆</button></div>'
        + f'<h3 class="ss-card-title">{nome}</h3><p class="ss-card-city">{cidade}</p>'
        + f'<div class="ss-grow"></div><div class="ss-actions">{acoes}</div></article>'
    )


# ==================================================
# 5. INTERAÇÕES DOS CARDS — SOMENTE DADOS DE NAVEGAÇÃO
# ==================================================
# O JS atua apenas sobre HTML produzido a partir do cadastro local. Nenhum
# conteúdo HTML externo, arquivo remoto ou credencial é interpretado aqui.
# Favoritos e histórico são individuais por aba, usando sessionStorage.
INTERACOES_JS = r"""
<script>
(() => {
  'use strict';
  const roots = document.querySelectorAll('#ss-directory');
  const root = roots.length ? roots[roots.length - 1] : null;
  if (!root || root.dataset.initialized === '1') return;
  root.dataset.initialized = '1';
  const keys = {fav:'ss-veiculos:favs:v2',recent:'ss-veiculos:recent:v2',only:'ss-veiculos:only-favs:v2'};
  const memory = window.__ssVeiculosMemory || (window.__ssVeiculosMemory={});
  const read = (key, fallback) => {
    try { const raw = window.sessionStorage.getItem(key); return raw ? JSON.parse(raw) : fallback; }
    catch (e) { return key in memory ? memory[key] : fallback; }
  };
  const save = (key, value) => {
    memory[key] = value;
    try { window.sessionStorage.setItem(key, JSON.stringify(value)); } catch (e) {}
  };
  const getFavorites = () => new Set(read(keys.fav, []));
  const cardList = () => Array.from(root.querySelectorAll('.ss-card'));
  let onlyFavorites = Boolean(read(keys.only, false));
  const toast = root.querySelector('.ss-toast');
  const notify = (message) => {
    toast.textContent = message; toast.style.display='block';
    clearTimeout(root.__ssToastTimeout);
    root.__ssToastTimeout = setTimeout(() => {toast.style.display='none'}, 2400);
  };
  function refreshFavorites() {
    const favorites = getFavorites();
    const toggle = root.querySelector('[data-action="favorites-filter"]');
    toggle.setAttribute('aria-pressed', String(onlyFavorites));
    toggle.textContent = (onlyFavorites ? '★ Exibir todas' : '☆ Meus favoritos') + ' ('+favorites.size+')';
    let visible = 0;
    cardList().forEach(card => {
      const selected = favorites.has(card.dataset.key);
      const button = card.querySelector('[data-action="favorite"]');      if (button) {
        button.textContent = selected ? '★' : '☆';
        button.setAttribute('aria-pressed', String(selected));
        button.setAttribute('aria-label', (selected?'Remover dos favoritos: ':'Favoritar: ')+card.querySelector('.ss-card-title').textContent);
        button.title = selected?'Remover favorito':'Favoritar';
      }
      const hide = onlyFavorites && !selected;
      card.classList.toggle('ss-hidden',hide);
      if (!hide) visible++;
    });
    root.querySelectorAll('.ss-group').forEach(group => {
      group.classList.toggle('ss-hidden', !group.querySelector('.ss-card:not(.ss-hidden)'));
    });
    const empty = root.querySelector('[data-fav-empty]');
    if (empty) empty.classList.toggle('ss-hidden', visible > 0);
    const count = root.querySelector('[data-result-count]');
    if (count) count.textContent = visible+' '+(visible===1?'entidade exibida':'entidades exibidas');
  }
  function recordAccess(name,url,key) {
    if (!url || !url.startsWith('https://ssveiculos.ssinformatica.net/')) return;
    const previous = read(keys.recent, []);
    const history = [{name,url,key},...previous.filter(item => item.key !== key)].slice(0,6);
    save(keys.recent,history);
    refreshRecents();
  }
  function refreshRecents() {
    const items = read(keys.recent, []);
    const bar = root.querySelector('.ss-recent');
    const container = root.querySelector('.ss-recent-links');
    container.replaceChildren();
    bar.style.display = items.length ? 'block':'none';
    items.forEach(item => {
      if (!item.url || !item.url.startsWith('https://ssveiculos.ssinformatica.net/')) return;
      const link = document.createElement('a');
      link.className = 'ss-recent-link';
      link.href=item.url; link.target='_blank'; link.rel='noopener noreferrer';
      link.textContent=item.name; link.title=item.name;
      link.dataset.action='recent-open';link.dataset.key=item.key;
      container.appendChild(link);
    });
  }
  root.addEventListener('click', async (event) => {
    const control = event.target.closest('[data-action]');
    if (!control || !root.contains(control)) return;
    const action=control.dataset.action;
    if(action==='favorite'){
      const fav=getFavorites();
      fav.has(control.dataset.key)?fav.delete(control.dataset.key):fav.add(control.dataset.key);
      save(keys.fav,[...fav]); refreshFavorites();
    }
    if(action==='favorites-filter'){
      onlyFavorites=!onlyFavorites;
      save(keys.only,onlyFavorites); refreshFavorites();
    }
    if(action==='copy'){
      try {await navigator.clipboard.writeText(control.dataset.url);notify('Link copiado.');}
      catch (e) { window.prompt('Copie o endereço:',control.dataset.url); }
    }
    if(action==='open'){
      recordAccess(control.dataset.name,control.dataset.url,control.dataset.key);
    }
    if(action==='recent-open'){
      recordAccess(control.textContent,control.href,control.dataset.key);
    }
  });
  if (!window.__ssVeiculosShortcutInstalled) {
    document.addEventListener('keydown', (event) => {
      if ((event.ctrlKey||event.metaKey) && event.key.toLowerCase()==='k') {
        const input=document.querySelector('input[type="search"]');
        if (input) {event.preventDefault(); input.focus(); input.select();}
      }
    });
    window.__ssVeiculosShortcutInstalled=true;
  }
  refreshFavorites(); refreshRecents();
})();
</script>
"""


def renderizar_lista(lista, agrupar=False):
    partes = ['<div id="ss-directory" class="ss-directory">']
    partes.append(
        '<div class="ss-toolbar"><span class="ss-results-meta" '
        'data-result-count aria-live="polite">'
        + f'{len(lista)} entidades exibidas</span>'
        + '<button type="button" data-action="favorites-filter" '
        'class="ss-fav-filter" aria-pressed="false">☆ Meus favoritos</button></div>'
    )
    partes.append(
        '<nav class="ss-recent" aria-label="Sistemas abertos recentemente">'
        '<div class="ss-recent-label">Abertos recentemente nesta aba</div>'
        '<div class="ss-recent-links"></div></nav>'
    )
    if agrupar:
        grupos = defaultdict(list)
        for e in lista:
            grupos[e["municipio"]].append(e)
        for cidade in sorted(grupos, key=normalizar):
            itens = grupos[cidade]
            partes.append(
                '<section class="ss-group"><h3 class="ss-group-title">'
                + escape(cidade)
                + f' <small>({len(itens)} {"entidade" if len(itens)==1 else "entidades"})</small>'
                + '</h3><div class="ss-grid">'
            )
            partes.extend(criar_card(e) for e in itens)
            partes.append('</div></section>')
    else:
        partes.append('<section class="ss-grid" aria-label="Entidades municipais">')
        partes.extend(criar_card(e) for e in lista)
        partes.append('</section>')
    partes.append(
        '<div class="ss-empty ss-hidden" data-fav-empty>'
        'Nenhuma entidade favoritada nesta seleção.</div>'
        '<div class="ss-toast" role="status" aria-live="polite"></div></div>'
    )
    # st.html não usa iframe; todos os botões ficam acessíveis ao teclado.
    st.html(''.join(partes)+INTERACOES_JS, unsafe_allow_javascript=True)


def limpar_filtros():
    st.session_state["busca"] = ""
    st.session_state["categoria_atual"] = "Todas"
    st.session_state["somente_link"] = False
    st.session_state["agrupar"] = False


# ==================================================
# 6. CABEÇALHO E INDICADORES (RENDERIZAÇÃO ESTÁTICA)
# ==================================================
logo_path = Path(__file__).resolve().parent / "Grupo-SS.png"
marca, titulo = st.columns([1.25, 5.5], gap="medium", vertical_alignment="center")
with marca:
    if logo_path.is_file():
        st.image(str(logo_path), width=210)
    else:
        st.markdown("**Grupo S&S**")
with titulo:
    st.html("""<header class="ss-brand">
      <div class="ss-kicker">Central municipal</div>
      <h1 class="ss-title">Painel de Acessos</h1>
      <p class="ss-subtitle">Sistema de Veículos</p>
      <p class="ss-description">Localize a entidade e abra seu ambiente de trabalho.</p>
    </header>""")
st.html('<div class="ss-rule" aria-hidden="true"></div>')

registros = catalogo_unico(ENTIDADES)
alertas_cadastro = diagnosticar(ENTIDADES)
com_link = sum(url_valida(e["url"]) for e in registros)
pendentes = len(registros) - com_link
renderizar_indicadores(len(registros), com_link, pendentes)

# ==================================================
# 7. PESQUISA E FILTROS — FRAGMENTO RÁPIDO
# ==================================================
@st.fragment

def painel_pesquisa():
    st.html(
        '<div class="ss-section-head"><h2>Encontrar entidade</h2>'
        '<p>Ctrl + K para buscar rapidamente</p></div>'
    )
    pesquisa = st.text_input(
        "Pesquisar por nome ou município",
        placeholder="Ex.: Maranguape, Caucaia ou SAAE",
        key="busca",
        type="search",
        live="250ms",
        label_visibility="collapsed",
    )
    totais_por_categoria = Counter(e["categoria"] for e in registros)
    categoria = st.pills(
        "Categorias",
        ["Todas"] + CATEGORIAS,
        default="Todas",
        required=True,
        key="categoria_atual",
        label_visibility="collapsed",
        format_func=lambda c: f"{c} · {len(registros) if c == 'Todas' else totais_por_categoria[c]}",
        wrap=True,
    )
    left, mid, right = st.columns([1.45, 1.45, 1], gap="small", vertical_alignment="center")
    with left:
        somente_com_link = st.toggle("Somente com link", value=False, key="somente_link")
    with mid:
        agrupar = st.toggle("Agrupar por município", value=False, key="agrupar")
    with right:
        st.button("Limpar filtros", icon=":material/refresh:", key="limpar", on_click=limpar_filtros, use_container_width=True)
    lista = filtrar(registros, pesquisa, categoria or "Todas", somente_com_link)
    st.html(
        '<div class="ss-section-head"><h2>Entidades municipais</h2>'
        '<p>' + str(len(lista)) + ' resultado(s) encontrado(s)</p></div>'
    )
    if not lista:
        st.html('<div class="ss-empty" role="status">Nenhuma entidade encontrada. Tente outro nome ou remova os filtros.</div>')
    # Sempre renderiza o histórico, mesmo que a pesquisa não tenha resultados.
    renderizar_lista(lista, agrupar=agrupar)
    st.html('<p class="ss-accessibility-note">Favoritos e recentes ficam somente nesta aba do navegador.</p>')


painel_pesquisa()

# ==================================================
# 8. CONFERÊNCIA CADASTRAL
# ==================================================
with st.expander(f"Conferência cadastral · {pendentes} sem link / {len(URLS_EM_CONFERENCIA)} URLs não associadas", expanded=False):
    st.caption("Estes registros não são apresentados como sistemas municipais com link confirmado.")
    st.markdown("**Entidades aguardando endereço**")
    for e in registros:
        if not url_valida(e["url"]):
            st.markdown(f"- {escape(e['nome'])} ({escape(e['categoria'])})")
    st.markdown("**Endereços recebidos ainda sem correspondência confirmada**")
    st.code("\n".join(x["url"] for x in URLS_EM_CONFERENCIA), language="text")
    if alertas_cadastro:
        st.warning("Foram encontradas inconsistências no cadastro. Verifique antes de publicar novas alterações.")
        st.code("\n".join(alertas_cadastro), language="text")
    else:
        st.caption("Cadastro principal sem nomes, categorias ou URLs duplicados/inválidos.")

# ==================================================
# 9. RODAPÉ INSTITUCIONAL
# ==================================================
st.html('<footer class="ss-footer">Grupo S&S Informática | Soluções para Gestão Municipal</footer>')
