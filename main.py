# -*- coding: utf-8 -*-
"""Painel de Acessos — Sistema de Veículos | Grupo S&S Informática.

A interface está neste arquivo; cadastros em veiculos_data.py, estilos e interações em assets/.
O projeto não armazena senhas, dados de autenticação nem informações de sessão
em banco de dados. Favoritos e recentes permanecem apenas na aba do navegador.
"""

# ==================================================
# 1. IMPORTAÇÕES E CONFIGURAÇÃO DA PÁGINA
# ==================================================
from collections import Counter, defaultdict
from base64 import b64encode
from functools import lru_cache
from html import escape
from pathlib import Path
from urllib.parse import urlparse
import unicodedata

import streamlit as st

st.set_page_config(
    page_title="Veículos Web | Painel de Acessos",
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

ROOT = Path(__file__).resolve().parent
PASTA_ASSETS = ROOT / "assets"
CSS_BASE = (PASTA_ASSETS / "painel.css").read_text(encoding="utf-8")
CSS_DARK = (PASTA_ASSETS / "painel_dark.css").read_text(encoding="utf-8")
# O tema selecionado no Streamlit tem prioridade; a preferência do navegador
# é um fallback para Firefox/Chrome quando o Streamlit está em modo automático.
CSS_TEMA = CSS_DARK if TEMA_ESCURO else "@media (prefers-color-scheme: dark) {\n" + CSS_DARK + "\n}"
st.html("<style>" + CSS_BASE + CSS_TEMA + "</style>")

# 3. DADOS — EM MÓDULO SEPARADO
from veiculos_data import ENTIDADES, ACESSOS_ADICIONAIS, CATEGORIAS, ROTULOS_CATEGORIA

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
    "Ambientes especiais": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 9h10M7 13h6"/>',
    "Ativos": '<path d="M20 6 9 17l-5-5"/>',
    "Pendentes": '<path d="M12 9v4m0 4h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.72 3h16.92a2 2 0 0 0 1.72-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/>',
    "Abrir": '<path d="M7 17 17 7M8 7h9v9"/>',
    "Copiar": '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>',
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


@lru_cache(maxsize=32)
def svg_icone(categoria):
    """Imagem SVG local em data URI; o sanitizador do st.html remove tags <svg>."""
    corpo = ICONES.get(categoria, ICONES["Todas"])
    cor = "#92ded9" if TEMA_ESCURO else "#006b6d"
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'fill="none" stroke="' + cor + '" stroke-width="1.9" '
        'stroke-linecap="round" stroke-linejoin="round">'
        + corpo + '</svg>'
    )
    codificado = b64encode(svg.encode("utf-8")).decode("ascii")
    return (
        '<img class="ss-svg" alt="" aria-hidden="true" '
        f'src="data:image/svg+xml;base64,{codificado}">'
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


def filtrar(itens, termo="", categoria="Todas"):
    termo = normalizar(termo).strip()
    filtrados = [
        e for e in itens
        if (categoria == "Todas" or e["categoria"] == categoria)
        and (
            not termo or termo in normalizar(" ".join(
                (e["nome"], e["municipio"], e["categoria"], urlparse(e["url"]).path.lstrip("/"))
            ))
        )
    ]
    return sorted(filtrados, key=lambda e: ordem_busca(e, termo))


def renderizar_indicadores(total, com_url, pendentes):
    dados = [
        ("Todas", "Registros", total),
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


def destacar_termo(texto, termo):
    """Destaca a correspondência sem perder acentos ou aceitar HTML da pesquisa."""
    texto = str(texto)
    busca = normalizar(termo).strip()
    if not busca:
        return escape(texto)
    letras, posicoes = [], []
    for indice, caractere in enumerate(texto):
        for letra in normalizar(caractere):
            letras.append(letra)
            posicoes.append(indice)
    inicio_norm = "".join(letras).find(busca)
    if inicio_norm == -1:
        return escape(texto)
    inicio = posicoes[inicio_norm]
    fim = posicoes[inicio_norm + len(busca) - 1] + 1
    return (
        escape(texto[:inicio])
        + '<mark class="ss-match">'
        + escape(texto[inicio:fim])
        + "</mark>"
        + escape(texto[fim:])
    )


def criar_card(entidade, termo=""):
    """Card com URL original, favorito por sessão e cópia rápida."""
    nome = escape(entidade["nome"], quote=True)
    nome_destacado = destacar_termo(entidade["nome"], termo)
    cidade_destacada = destacar_termo(entidade["municipio"], termo)
    # Oculta a segunda linha quando o município já aparece no nome completo.
    cidade_duplicada = normalizar(entidade["municipio"]) in normalizar(entidade["nome"])
    cat = escape(ROTULOS_CATEGORIA.get(entidade["categoria"], entidade["categoria"]), quote=True)
    classificacao = bool(entidade.get("conferencia"))
    chave = escape(id_entidade(entidade), quote=True)
    url = entidade["url"]
    if url_valida(url):
        destino = escape(url, quote=True)
        acoes = (
            '<a class="ss-link" data-action="open" data-key="' + chave
            + '" data-name="' + nome + '" data-url="' + destino
            + '" href="' + destino
            + '" target="_blank" rel="noopener noreferrer">Abrir sistema '
            + svg_icone("Abrir") + '</a>'
            + '<button type="button" class="ss-copy" data-action="copy" '
            + 'data-url="' + destino + '" title="Copiar link" aria-label="Copiar link de '
            + nome + '">' + svg_icone("Copiar") + '</button>'
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
        + f'<h3 class="ss-card-title">{nome_destacado}</h3>'
        + ('' if cidade_duplicada else f'<p class="ss-card-city">{cidade_destacada}</p>')
        + ('<p class="ss-review">Classificação a conferir</p>' if classificacao else '')
        + f'<div class="ss-grow"></div><div class="ss-actions">{acoes}</div></article>'
    )


# ==================================================
# 5. INTERAÇÕES DOS CARDS — SOMENTE DADOS DE NAVEGAÇÃO
# ==================================================
# O JS atua apenas sobre HTML produzido a partir do cadastro local. Nenhum
# conteúdo HTML externo, arquivo remoto ou credencial é interpretado aqui.
# Favoritos e histórico são individuais por aba, usando sessionStorage.
INTERACOES_JS = "<script>\n" + (PASTA_ASSETS / "interacoes.js").read_text(encoding="utf-8") + "\n</script>"


def renderizar_lista(lista, agrupar=False, termo=""):
    busca = termo.strip()[:80]
    busca_segura = escape(busca, quote=True)
    palavra = "resultado" if len(lista) == 1 else "resultados"
    contador = (
        f'{len(lista)} {palavra} para “{escape(busca)}”'
        if busca
        else f'{len(lista)} entidades exibidas'
    )
    partes = [f'<div id="ss-directory" class="ss-directory" data-search-label="{busca_segura}">']
    partes.append(
        '<div class="ss-toolbar"><span class="ss-results-meta" '
        'data-result-count aria-live="polite">'
        + contador + '</span>'
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
            partes.extend(criar_card(e, termo=termo) for e in itens)
            partes.append('</div></section>')
    else:
        partes.append('<section class="ss-grid" aria-label="Entidades municipais">')
        partes.extend(criar_card(e, termo=termo) for e in lista)
        partes.append('</section>')
    partes.append(
        '<div class="ss-empty ss-hidden" data-fav-empty>'
        'Nenhuma entidade favoritada nesta seleção.</div>'
        '<button type="button" class="ss-back-top" data-action="back-top" '
        'aria-label="Voltar ao topo" aria-hidden="true" tabindex="-1" title="Voltar ao topo">'
        '<span aria-hidden="true">↑</span><span>Topo</span></button>'
        '<div class="ss-toast" role="status" aria-live="polite"></div></div>'
    )
    # st.html não usa iframe; todos os botões ficam acessíveis ao teclado.
    st.html(''.join(partes)+INTERACOES_JS, unsafe_allow_javascript=True)


def limpar_filtros():
    st.session_state["busca"] = ""
    st.session_state["categoria_atual"] = "Todas"
    st.session_state["agrupar"] = False


# ==================================================
# 6. CABEÇALHO E INDICADORES (RENDERIZAÇÃO ESTÁTICA)
# ==================================================
logo_path = PASTA_ASSETS / "veiculosweb.png"
marca, titulo = st.columns([1.75, 4.9], gap="medium", vertical_alignment="center")
with marca:
    if logo_path.is_file():
        st.image(str(logo_path), width=285)
    else:
        st.markdown("**Veículos Web**")
with titulo:
    st.html("""<header class="ss-brand">
      <h1 class="ss-title">Painel de Acessos</h1>
      <p class="ss-description">Localize a entidade e abra seu ambiente de trabalho.</p>
    </header>""")
st.html('<div class="ss-rule" aria-hidden="true"></div>')

registros = catalogo_unico(ENTIDADES + ACESSOS_ADICIONAIS)
alertas_cadastro = diagnosticar(ENTIDADES + ACESSOS_ADICIONAIS)
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
    agrupar_col, limpar_col = st.columns([3, 1], gap="small", vertical_alignment="center")
    with agrupar_col:
        agrupar = st.toggle("Agrupar por município", value=False, key="agrupar")
    with limpar_col:
        st.button("Limpar filtros", icon=":material/refresh:", key="limpar", on_click=limpar_filtros, use_container_width=True)
    lista = filtrar(registros, pesquisa, categoria or "Todas")
    st.html(
        '<div class="ss-section-head"><h2>Entidades e ambientes</h2></div>'
    )
    if not lista:
        st.html('<div class="ss-empty" role="status">Nenhuma entidade encontrada. Tente outro nome ou remova os filtros.</div>')
    # Sempre renderiza o histórico, mesmo que a pesquisa não tenha resultados.
    renderizar_lista(lista, agrupar=agrupar, termo=pesquisa)
    st.html('<p class="ss-accessibility-note">Favoritos e recentes ficam somente nesta aba do navegador.</p>')


painel_pesquisa()

# ==================================================
# 8. CONFERÊNCIA CADASTRAL
# ==================================================
with st.expander(f"Conferência cadastral · {pendentes} registros sem URL / {len(ACESSOS_ADICIONAIS)} acessos adicionais", expanded=False):
    st.caption("Todos os links recebidos estão disponíveis nos cards. A classificação de acessos adicionais foi sugerida a partir do endereço e pode ser corrigida em veiculos_data.py.")
    st.markdown("**Registros sem endereço**")
    for e in registros:
        if not url_valida(e["url"]):
            st.markdown(f"- {e['nome']} ({e['categoria']})")
    st.markdown("**Acessos adicionais já exibidos no painel — classificação a conferir**")
    for e in ACESSOS_ADICIONAIS:
        st.markdown(f"- [{e['nome']}]({e['url']}) · {e['categoria']}")
    if alertas_cadastro:
        st.warning("Foram encontradas inconsistências no cadastro. Verifique antes de publicar novas alterações.")
        st.code("\\n".join(alertas_cadastro), language="text")
    else:
        st.caption("Nenhum nome, categoria ou endereço duplicado/inválido detectado.")

# ==================================================
# 9. RODAPÉ INSTITUCIONAL
# ==================================================
st.html('<footer class="ss-footer">Grupo S&S Informática | Soluções para Gestão Municipal</footer>')
