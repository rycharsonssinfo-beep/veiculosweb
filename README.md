# Painel de Acessos — Sistema de Veículos

Central de navegação do **Grupo S&S Informática**, desenvolvida em Python e Streamlit para localizar entidades municipais e abrir seus ambientes do Sistema de Veículos.

## Funcionalidades

- Pesquisa por nome, município ou categoria, ignorando maiúsculas e acentos, com atualização após 250 ms sem digitar.
- Pesquisa e filtros isolados em um `st.fragment`, mantendo o cabeçalho e os indicadores sem reconstrução desnecessária.
- Filtros de **Prefeituras, Câmaras, Consórcios, Institutos e SAAEs**; opção **Somente com link**.
- Ordenação priorizando correspondências exatas, seguidas de prefixos e correspondências parciais.
- Visualização individual ou **agrupada por município**.
- Cards compactos com botões para abrir o endereço original em outra aba, copiar o link e marcar favoritos.
- **Favoritos** e **abertos recentemente** restritos à aba do navegador. Utilizam `sessionStorage`, sem banco de dados nem compartilhamento entre usuários. Ao encerrar a aba, os dados poderão ser descartados pelo navegador.
- Atalho **Ctrl+K** (ou **Cmd+K**, onde o navegador permitir) para focar a pesquisa.
- Tema corporativo nas aparências clara e escura, com contraste e layout responsivo.
- Seção de conferência de entidades sem URL e endereços ainda não associados.

## Estrutura

- `main.py` — cadastro, validações, interface e interações; **único arquivo que precisa ser editado para acrescentar municípios**.
- `Grupo-SS.png` — logomarca oficial.
- `requirements.txt` — versão do Streamlit.
- `app.py` — compatibilidade com a implantação inicial do Streamlit Community Cloud; executa `main.py` em cada interação.
- `.github/workflows/validar.yml` — verificação automatizada de sintaxe e integridade dos cadastros. Não é utilizado em execução normal do painel.

## Atualizar ou incluir município

Abra `main.py` e localize a lista `ENTIDADES`:

```python
{
    "nome": "Prefeitura Municipal de Maranguape",
    "municipio": "Maranguape",
    "categoria": "Prefeituras",
    "url": "https://ssveiculos.ssinformatica.net/Maranguape"
},
```

As categorias aceitas são **Prefeituras**, **Câmaras**, **Consórcios**, **Institutos** e **SAAEs**. Cada URL precisa ser confirmada e transcrita exatamente como fornecida. Não invente endereço: use `"url": ""` quando ainda não houver link conhecido.

Ao salvar, a pesquisa, os filtros e os indicadores serão atualizados automaticamente. Não adicione senhas ou tokens neste arquivo; o repositório é público.

Endereços ainda sem vínculo confirmado ficam na lista `URLS_EM_CONFERENCIA`. Revise esses registros antes de associar uma URL a uma entidade.

## Executar localmente

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Se preferir, `streamlit run main.py` também executa a aplicação. Para a implantação atual em [Streamlit Community Cloud](https://share.streamlit.io/), mantenha o arquivo de entrada **`app.py`**, até optar por reconfigurar o deploy para `main.py`.

## Segurança e funcionamento

O painel contém **somente nomes, categorias, municípios e URLs**. Ele não executa login nos sistemas de destino e não armazena credenciais. A contagem **Com link** representa endereços cadastrados em formato válido, **não** uma verificação de disponibilidade dos servidores externos.

A cópia de link usa a API de área de transferência do navegador, que pode solicitar permissão; quando indisponível, é exibido o endereço para cópia manual.

Se o painel precisar ser exclusivo para a equipe de suporte, configure autenticação/autorização adequada antes de compartilhar endereços internos ou informações adicionais. A aplicação, por si só, não bloqueia visitantes.

## Validação

Os commits verificam automaticamente sintaxe, duplicidade de nomes ou endereços, categorias válidas e URLs HTTPS no domínio oficial. Além disso, é importante testar após mudanças no Streamlit: busca, troca de categorias, favoritos, link em nova aba e apresentação em dispositivos móveis e tema escuro.
