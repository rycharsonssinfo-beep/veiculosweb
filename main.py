# -*- coding: utf-8 -*-
"""Painel de Acessos — Sistema de Veículos | Grupo S&S Informática.

Manutenção: edite somente a lista ENTIDADES abaixo para alterar os acessos.
Todos os links foram transcritos de ListagemVeiculos.txt, sem criação de URLs.
Registros sem vínculo inequívoco são mantidos para conferência e não
aparecem como sistemas com acesso disponível.
"""

# ==================================================
# 1. IMPORTAÇÕES E CONFIGURAÇÃO DA PÁGINA
# ==================================================
from collections import Counter
from html import escape
from pathlib import Path
import unicodedata
from urllib.parse import urlparse

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
st.markdown("""
<style>
:root {
    --ss-primary: #006363;
    --ss-teal: #007f86;
    --ss-ink: #19383c;
    --ss-muted: #67777b;
    --ss-line: #e2eeee;
    --ss-bg: #f5f9f9;
    --ss-soft: #e8f5f3;
}
html, body, [data-testid="stAppViewContainer"] {background:#f8fafa;}
[data-testid="stHeader"] {background:rgba(248,250,250,.96);}
.block-container {max-width: 1450px; padding-top: 1.1rem; padding-bottom: 2.6rem;}
#MainMenu, footer {visibility:hidden;}
.ss-top-accent {height:5px; max-width:180px; border-radius:12px; background:linear-gradient(90deg,#007f86,#006363); margin: 3px 0 13px;}
.ss-header {margin: 8px 0 12px;}
.ss-kicker {font-size:.76rem; text-transform:uppercase; letter-spacing:.16em; font-weight:700; color:var(--ss-teal);}
.ss-title {font-size:clamp(1.95rem,3.7vw,3.1rem); letter-spacing:-.04em; font-weight:790; line-height:1.13; color:#113f43; margin:.2rem 0 .35rem;}
.ss-subtitle {font-size:1.02rem; font-weight:650; color:#306166; margin:.25rem 0 .35rem;}
.ss-description {font-size:.93rem; line-height:1.55; color:var(--ss-muted); margin:.3rem 0 .9rem;}
.ss-divider {border:0;border-top:1px solid #e4eded; margin:16px 0 21px;}
.ss-section {margin:15px 0 8px;display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:8px;}
.ss-section-title {font-size:1.20rem;font-weight:770;color:var(--ss-ink);margin:0;letter-spacing:-.02em;}
.ss-section-sub {font-size:.86rem;color:var(--ss-muted);margin:0;}
.ss-kpis {display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px;margin:12px 0 22px;}
.ss-kpi {background:#fff;border:1px solid #e2ebeb;border-radius:15px;padding:17px 16px 15px;box-shadow:0 2px 9px rgba(19,79,79,.035);min-width:0;}
.ss-kpi-label {font-size:.78rem;font-weight:600;color:#65787a;line-height:1.3;}
.ss-kpi-count {color:#0d4b4c;font-weight:800;font-size:1.9rem;letter-spacing:-.05em;line-height:1.25;margin-top:8px;}
.ss-kpi-top {display:flex;align-items:center;justify-content:space-between;gap:8px;}
.ss-icon {height:31px;width:31px;border-radius:9px;color:#00737b;background:#edf7f6;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;}
.ss-icon svg {height:17px;width:17px;stroke:currentColor;}
.ss-search-caption {font-size:.86rem;color:var(--ss-muted);margin:5px 0 8px;}
.ss-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:15px;margin:12px 0 12px;}
.ss-card {background:#fff;border:1px solid #e1ebea;border-radius:16px;box-shadow:0 3px 12px rgba(24,74,74,.04);min-width:0;padding:19px 18px 17px;display:flex;flex-direction:column;min-height:218px;transition:transform .16s ease,box-shadow .16s ease,border-color .16s ease;}
.ss-card:hover {border-color:#a7cecd;box-shadow:0 9px 26px rgba(18,78,79,.10);transform:translateY(-2px);}
.ss-card-top {display:flex;justify-content:space-between;align-items:center;margin-bottom:13px;gap:8px;}
.ss-card-icon {display:inline-flex;align-items:center;justify-content:center;border-radius:11px;background:#eaf6f5;color:#00767b;width:37px;height:37px;flex-shrink:0;}
.ss-card-icon svg {width:20px;height:20px;stroke:currentColor;}
.ss-pill {font-size:.70rem;font-weight:700;padding:5px 9px;border-radius:999px;background:#f0f6f5;color:#33696a;white-space:nowrap;}
.ss-card-title {font-size:1.005rem;line-height:1.37;font-weight:750;color:#1d3e43;margin:0 0 9px;overflow-wrap:anywhere;}
.ss-card-city {font-size:.82rem;color:#738285;margin-bottom:18px;}
.ss-card-city strong {font-weight:620;color:#536669;}
.ss-card-spacer {flex:1;}
.ss-cta,.ss-no-link {width:100%;min-height:40px;border-radius:10px;display:inline-flex;justify-content:center;align-items:center;gap:8px;font-size:.88rem;font-weight:750;text-decoration:none!important;box-sizing:border-box;}
.ss-cta {background:#006a6c;color:#fff!important;border:1px solid #006a6c;transition:background .15s,transform .15s;}
.ss-cta:hover {background:#005253;color:#fff!important;}
.ss-cta:focus-visible {outline:3px solid #3da8ab;outline-offset:3px;}
.ss-cta svg {width:16px;height:16px;stroke:currentColor;}
.ss-no-link {color:#708185;border:1px dashed #d0dede;background:#f6f9f9;}
.ss-notice {border:1px solid #e1eceb;border-radius:12px;background:white;padding:20px;color:#587477;text-align:center;margin:14px 0;}
.ss-footer {margin-top:28px;border-top:1px solid #dceae9;padding-top:18px;color:#6b8183;font-size:.81rem;text-align:center;}
/* Os controles de pesquisa e categoria continuam nativos e acessíveis. */
div[data-testid="stTextInput"] input {border-radius:11px;background:#fff;border-color:#dae8e7;min-height:47px;}
div[data-testid="stTextInput"] input:focus {border-color:#007f86;box-shadow:0 0 0 1px #007f86;}
@media (max-width:1180px) {
    .ss-kpis {grid-template-columns:repeat(3,minmax(0,1fr));}
    .ss-grid {grid-template-columns:repeat(3,minmax(0,1fr));}
}
@media (max-width:850px) {
    .ss-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
    .ss-kpis {grid-template-columns:repeat(3,minmax(0,1fr));}
}
@media (max-width:600px) {
    .block-container {padding-left:1.05rem;padding-right:1.05rem;padding-top:.5rem;}
    .ss-grid {grid-template-columns:1fr;gap:11px;}
    .ss-kpis {grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;}
    .ss-kpi {padding:12px 12px 10px;border-radius:12px;}
    .ss-kpi-count {font-size:1.55rem;}
    .ss-card {min-height:190px;padding:16px;}
    .ss-title {font-size:1.92rem;}
    .ss-kpi-label {font-size:.73rem;}
}

/* Modo escuro do sistema: os componentes personalizados acompanham o Streamlit. */
@media (prefers-color-scheme: dark) {
  :root { --ss-ink:#e9f3f3; --ss-muted:#aec4c6; --ss-line:#375154; }
  html, body, [data-testid="stAppViewContainer"] {background:#101e21!important;color:#eaf3f3;}
  [data-testid="stHeader"] {background:rgba(16,30,33,.96)!important;}
  .ss-kicker {color:#7bd5d2;}
  .ss-title,.ss-section-title {color:#eaf7f6;}
  .ss-subtitle {color:#bee0df;}
  .ss-description,.ss-section-sub,.ss-search-caption {color:#acc5c7;}
  .ss-divider {border-color:#355054;}
  .ss-kpi,.ss-card {background:#1b3033;border-color:#385458;box-shadow:0 3px 13px rgba(0,0,0,.17);}
  .ss-card:hover {border-color:#5a9696;box-shadow:0 9px 26px rgba(0,0,0,.24);}
  .ss-kpi-label {color:#bbd2d3;}
  .ss-kpi-count {color:#e8fcf9;}
  .ss-icon,.ss-card-icon {background:#264548;color:#8fdbd4;}
  .ss-card-title {color:#f0f8f8;}
  .ss-card-city,.ss-card-city strong {color:#bad0d2;}
  .ss-pill {background:#29484c;color:#cee9e8;}
  .ss-cta {background:#006e72;color:#fff!important;border-color:#16868a;}
  .ss-cta:hover {background:#00595d;}
  .ss-no-link {background:#25383b;border-color:#4b666a;color:#b3c9ca;}
  .ss-notice {background:#1c3033;border-color:#385458;color:#c9dede;}
  .ss-footer {color:#acc4c6;border-color:#355054;}
  div[data-testid="stTextInput"] input {background:#1b3033!important;color:#f1f9f9!important;border-color:#48686c!important;}
  div[data-testid="stTextInput"] input::placeholder {color:#afc5c6!important;}
  /* A marca contém texto verde escuro: a base clara mantém sua legibilidade. */
  div[data-testid="stImage"] {background:#fff;padding:9px;border-radius:12px;box-sizing:border-box;}
}

@media (prefers-reduced-motion:reduce) {.ss-card,.ss-cta {transition:none!important;}}
</style>
""", unsafe_allow_html=True)

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

# Ícones vetoriais locais; não dependem de serviços ou CDNs externos.
ICONES = {
    "Todos os Acessos": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    "Prefeituras": '<path d="M3 21h18M5 21V9l7-5 7 5v12M9 21v-7h6v7M8 10h1M15 10h1"/>',
    "Câmaras": '<path d="M3 21h18M5 21V9h14v12M9 21v-5h6v5M5 9l7-5 7 5M9 12h1M14 12h1"/>',
    "Consórcios": '<circle cx="12" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="M11 7 6 17M13 7l5 10M7 19h10"/>',
    "Institutos": '<path d="m3 9 9-6 9 6M4 10h16M6 10v10M10 10v10M14 10v10M18 10v10M3 21h18"/>',
    "SAAEs": '<path d="M12 22a8 8 0 0 0 8-8c0-5-8-12-8-12S4 9 4 14a8 8 0 0 0 8 8Z"/><path d="M9 16a3 3 0 0 0 3 3"/>',
}

# ==================================================
# 4. FUNÇÕES AUXILIARES
# ==================================================
def normalizar(texto):
    """Permite pesquisa e ordenação sem distinguir acentos ou maiúsculas."""
    texto = str(texto or "")
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)).casefold()


def url_valida(endereco):
    """Exige URL HTTPS completa; nunca tenta adivinhar o endereço."""
    if not isinstance(endereco, str) or not endereco.strip():
        return False
    try:
        parsed = urlparse(endereco)
        return parsed.scheme == "https" and bool(parsed.hostname) and not any(c.isspace() for c in endereco)
    except ValueError:
        return False


def svg_icone(categoria):
    corpo = ICONES.get(categoria, ICONES["Todos os Acessos"])
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{corpo}</svg>'


def entidades_unicas(itens):
    """Desconsidera repetições de entidade/categoria/município no painel."""
    unicos = {}
    for entidade in itens:
        chave = (normalizar(entidade["nome"]), normalizar(entidade["municipio"]), entidade["categoria"])
        if chave not in unicos or (not url_valida(unicos[chave]["url"]) and url_valida(entidade["url"])):
            unicos[chave] = entidade
    return list(unicos.values())


def renderizar_indicadores(registros, totais):
    itens = [("Todos os Acessos", "Sistemas disponíveis", totais["Total de Acessos"])]
    itens.extend((cat, cat, totais[cat]) for cat in CATEGORIAS)
    partes = ['<section class="ss-kpis" aria-label="Indicadores do painel">']
    for cat, rotulo, quantidade in itens:
        partes.append(
            f'<div class="ss-kpi"><div class="ss-kpi-top">'
            f'<span class="ss-kpi-label">{escape(rotulo)}</span>'
            f'<span class="ss-icon">{svg_icone(cat)}</span></div>'
            f'<div class="ss-kpi-count">{quantidade}</div></div>'
        )
    partes.append('</section>')
    st.markdown("".join(partes), unsafe_allow_html=True)


def renderizar_cards(lista):
    """Cards responsivos com links originais; abrem em nova aba sem iframe."""
    resultado = ['<section class="ss-grid" aria-label="Entidades municipais">']
    seta = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>'
    for e in lista:
        nome, municipio, categoria = (escape(e[k], quote=True) for k in ("nome", "municipio", "categoria"))
        if url_valida(e["url"]):
            destino = escape(e["url"], quote=True)
            acesso = f'<a class="ss-cta" href="{destino}" target="_blank" rel="noopener noreferrer" aria-label="Abrir sistema de {nome} (nova aba)">Abrir sistema {seta}</a>'
        else:
            acesso = '<span class="ss-no-link" aria-label="Link não cadastrado">Link não cadastrado</span>'
        resultado.append(
            f'<article class="ss-card"><div class="ss-card-top">'
            f'<span class="ss-card-icon">{svg_icone(e["categoria"])}</span>'
            f'<span class="ss-pill">{categoria}</span></div>'
            f'<div class="ss-card-title">{nome}</div>'
            f'<div class="ss-card-city">Município: <strong>{municipio}</strong></div>'
            f'<div class="ss-card-spacer"></div>{acesso}</article>'
        )
    resultado.append('</section>')
    st.markdown("".join(resultado), unsafe_allow_html=True)


# ==================================================
# 5. CABEÇALHO DA APLICAÇÃO
# ==================================================
logo_path = Path(__file__).resolve().parent / "Grupo-SS.png"
marca, titulo = st.columns([1.25, 3.9], gap="medium", vertical_alignment="center")
with marca:
    if logo_path.is_file():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown("**Grupo S&S**")
with titulo:
    st.markdown("""<div class="ss-header">
        <div class="ss-top-accent"></div>
        <div class="ss-kicker">Grupo S&S · Gestão Municipal</div>
        <h1 class="ss-title">Painel de Acessos</h1>
        <div class="ss-subtitle">Sistema de Veículos</div>
        <div class="ss-description">Encontre e abra rapidamente o ambiente de cada entidade.</div>
    </div>""", unsafe_allow_html=True)
st.markdown('<hr class="ss-divider"/>', unsafe_allow_html=True)

# ==================================================
# 6. INDICADORES DO PAINEL
# ==================================================
registros = entidades_unicas(ENTIDADES)
quantidades = Counter(e["categoria"] for e in registros if url_valida(e["url"]))
contagem = {cat: quantidades.get(cat, 0) for cat in CATEGORIAS}
contagem["Total de Acessos"] = sum(contagem.values())
renderizar_indicadores(registros, contagem)

# ==================================================
# 7. PESQUISA E FILTROS POR CATEGORIA
# ==================================================
st.markdown('<div class="ss-section"><h2 class="ss-section-title">Localizar entidade</h2><p class="ss-section-sub">Busca por nome ou município</p></div>', unsafe_allow_html=True)
pesquisa = st.text_input(
    "Pesquisar por nome ou município",
    placeholder="Ex.: Maranguape, Caucaia ou SAAE",
    key="busca",
    label_visibility="collapsed",
    icon=":material/search:",
    type="search",
    live="250ms",  # Streamlit >= 1.64: atualiza após uma pausa ao digitar.
)

# Os filtros contam entidades cadastradas, inclusive as que ainda aguardam URL.
# Os indicadores acima, por outro lado, contam apenas sistemas com URL confirmada.
contagem_entidades = Counter(e["categoria"] for e in registros)
escolhas = ["Todos os Acessos"] + CATEGORIAS
categoria = st.pills(
    "Filtrar por categoria", escolhas, default="Todos os Acessos", required=True,
    key="categoria_atual", label_visibility="collapsed", wrap=True,
    format_func=lambda c: f"{'Todos' if c == 'Todos os Acessos' else c} · {len(registros) if c == 'Todos os Acessos' else contagem_entidades[c]}",
)

busca = normalizar(pesquisa).strip()
filtrados = [
    e for e in registros
    if (categoria == "Todos os Acessos" or e["categoria"] == categoria)
    and (not busca or busca in normalizar(" ".join((e["nome"], e["municipio"], e["categoria"]))))
]
filtrados.sort(key=lambda e: (normalizar(e["nome"]), normalizar(e["municipio"])))

# ==================================================
# 8. EXIBIÇÃO DOS CARDS DE ACESSO
# ==================================================
resultado_rotulo = "entidade encontrada" if len(filtrados) == 1 else "entidades encontradas"
st.markdown(
    '<div class="ss-section"><h2 class="ss-section-title">Entidades municipais</h2>'
    f'<p class="ss-section-sub">{len(filtrados)} {resultado_rotulo}</p></div>',
    unsafe_allow_html=True,
)
if filtrados:
    renderizar_cards(filtrados)
else:
    st.markdown('<div class="ss-notice">Nenhuma entidade encontrada. Tente outro nome ou categoria.</div>', unsafe_allow_html=True)
    if pesquisa:
        st.button("Limpar pesquisa", icon=":material/close:", on_click=lambda: st.session_state.update(busca=""))

# Há entidades cadastradas sem URL confirmada; permanecem pesquisáveis,
# mas o botão de acesso só é exibido quando o endereço HTTPS existe.
# URLs_EM_CONFERENCIA não são exibidas como acessos municipais até validação.

# ==================================================
# 9. RODAPÉ INSTITUCIONAL
# ==================================================
st.markdown('<div class="ss-footer">Grupo S&S Informática | Soluções para Gestão Municipal</div>', unsafe_allow_html=True)