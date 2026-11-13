# Veículos Web — Painel de Acessos

Central de navegação do **Grupo S&S Informática**, desenvolvida em Python e Streamlit para localizar entidades municipais e abrir seus ambientes do Sistema de Veículos.

## Funcionalidades

- Pesquisa por nome, município ou categoria, ignorando maiúsculas e acentos, com atualização após 250 ms sem digitar.
- Pesquisa e filtros isolados em um `st.fragment`, mantendo o cabeçalho sem reconstrução desnecessária.
- Filtros de **Prefeituras, Câmaras, Consórcios, Institutos, SAAEs e Ambientes especiais**, centralizados por um contêiner horizontal nativo do Streamlit, com quantidades discretas e quebra de linhas em telas menores.
- Ordenação alfabética por município, ignorando acentos, e depois por entidade; a pesquisa preserva a priorização das melhores correspondências.
- Visualização individual ou **agrupada por município** em grade fluida: grupos com 1 ou 2 acessos dividem a mesma linha com outros municípios, preservando os cards lado a lado e a ordem alfabética. Layout adaptável a celulares e favoritos, mantendo o botão para limpar os filtros.
- Cards compactos (cinco colunas em telas largas), com município destacado na pesquisa e sem repetir a cidade no nome; a classificação provisória aparece apenas na Conferência cadastral.
- **Favoritos** e **acessos recentes** em faixa horizontal compacta, restritos à aba do navegador por `sessionStorage`, sem banco de dados ou compartilhamento.
- Atalho **Ctrl+K** (ou **Cmd+K**, onde o navegador permitir) para focar a pesquisa.
- Botão **Voltar ao topo** após rolagem e transições curtas nos filtros e resultados, respeitando a preferência por movimento reduzido.
- Tema claro/escuro com marca mais legível no escuro, filtros ativos verde-petróleo, controles próximos e espaçamento vertical reduzido.
- Seção de conferência dos 7 registros sem link e das classificações sugeridas para os 26 acessos adicionais; os endereços são sempre pesquisáveis e abertos em nova aba.

## Quantidades iniciais (novembro de 2026)

- 89 entidades na planilha de origem (82 com link, 7 sem URL).
- 25 links adicionais do TXT incorporados à lista principal.
- 1 novo link `https://ssveiculos.ssinformatica.net/IPMparaipaba`, classificado provisoriamente como Instituto.
- **108 URLs únicas** disponíveis nos cards, **115 registros** no painel incluindo os 7 sem URL.

## Estrutura

- `main.py` — ponto central da interface, pesquisas e funcionalidades.
- `veiculos_data.py` — cadastro de entidades, URLs e categorias; edite este arquivo para incluir municípios.
- `assets/painel.css` e `assets/painel_dark.css` — identidade visual e ajustes de tema.
- `assets/interacoes.js` — favoritos, histórico, cópia de endereços e atalhos.
- `assets/veiculosweb.png` — nova logomarca VeículosWeb em PNG transparente.
- `Grupo-SS.png` — arquivo histórico da logomarca anterior, mantido como referência (não utilizado no cabeçalho).
- `requirements.txt` — versão do Streamlit.
- `app.py` — compatibilidade com a implantação inicial do Streamlit Community Cloud; executa `main.py` em cada interação.
- `.github/workflows/validar.yml` — verificação automatizada de sintaxe e integridade dos cadastros. Não é utilizado em execução normal do painel.

## Atualizar ou incluir município

Abra `veiculos_data.py` e localize a lista `ENTIDADES`:

```python
{
    "nome": "Prefeitura Municipal de Maranguape",
    "municipio": "Maranguape",
    "categoria": "Prefeituras",
    "url": "https://ssveiculos.ssinformatica.net/Maranguape"
},
```

As categorias aceitas são **Prefeituras**, **Câmaras**, **Consórcios**, **Institutos**, **SAAEs** e **Ambientes especiais**. Cada URL precisa ser confirmada e transcrita exatamente como fornecida. Não invente endereço: use `"url": ""` quando ainda não houver link conhecido.

Ao salvar, a pesquisa, os filtros e a contagem de resultados serão atualizados automaticamente. Não adicione senhas ou tokens neste arquivo; o repositório é público.

Os links adicionais fornecidos apenas por URL ficam em `ACESSOS_ADICIONAIS` e **já aparecem nos cards e na pesquisa**. Seus nomes e categorias são rótulos operacionais, marcados como "Classificação a conferir". O cadastro mantém também as entidades sem endereço, com botão desabilitado.

## Executar localmente

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Se preferir, `streamlit run main.py` também executa a aplicação. Para a implantação atual em [Streamlit Community Cloud](https://share.streamlit.io/), mantenha o arquivo de entrada **`app.py`**, até optar por reconfigurar o deploy para `main.py`.

## Segurança e funcionamento

O painel contém **somente nomes, categorias, municípios e URLs**. Ele não executa login nos sistemas de destino e não armazena credenciais. A interface principal não exibe cartões de indicadores cadastrais: as quantidades aparecem discretamente nos filtros e na listagem, enquanto as pendências ficam na seção expansível de conferência. A existência de um link cadastrado **não** confirma a disponibilidade do servidor externo.

A cópia de link usa a API de área de transferência do navegador, que pode solicitar permissão; quando indisponível, é exibido o endereço para cópia manual.

Se o painel precisar ser exclusivo para a equipe de suporte, configure autenticação/autorização adequada antes de compartilhar endereços internos ou informações adicionais. A aplicação, por si só, não bloqueia visitantes.

## Validação

Os commits verificam automaticamente sintaxe, duplicidade de nomes ou endereços, categorias válidas e URLs HTTPS no domínio oficial. Além disso, é importante testar após mudanças no Streamlit: busca, troca de categorias, favoritos, link em nova aba e apresentação em dispositivos móveis e tema escuro.

## Identidade visual e navegadores

O cabeçalho usa a marca transparente **VeículosWeb**, o título **Painel de Acessos** e uma descrição curta sem repetir o nome da marca. As cores dos controles nativos são padronizadas por CSS para reduzir discrepâncias entre Firefox e Chrome, inclusive quando cada navegador usa configuração de tema diferente. O modo escuro do Streamlit continua disponível.
