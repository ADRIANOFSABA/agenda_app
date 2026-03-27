import streamlit as st
import sqlite3
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from io import BytesIO
import hashlib
import qrcode
from PIL import Image

st.set_page_config(page_title="Agenda Pro Premium", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# ==============================
# ESTILO VISUAL PREMIUM
# ==============================
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #f8fafc 0%, #eef4ff 45%, #f8fafc 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0b1220 0%, #16233b 100%); border-right: 1px solid rgba(255,255,255,0.08); }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1500px; }
    .premium-topbar { background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 35%, #0ea5e9 100%); padding: 24px 26px; border-radius: 24px; color: white; box-shadow: 0 18px 40px rgba(37,99,235,0.22); margin-bottom: 18px; }
    .premium-topbar h1 { margin: 0; font-size: 30px; font-weight: 900; }
    .premium-topbar p { margin: 8px 0 0 0; opacity: 0.94; font-size: 14px; max-width: 760px; }
    .section-title { font-size: 21px; font-weight: 800; color: #0f172a; margin: 10px 0 14px 0; }
    .glass-card { background: rgba(255,255,255,0.95); backdrop-filter: blur(6px); border: 1px solid #e5e7eb; border-radius: 22px; padding: 18px 20px; box-shadow: 0 12px 28px rgba(15,23,42,0.06); margin-bottom: 14px; }
    .metric-premium { background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%); border: 1px solid #e5e7eb; border-radius: 22px; padding: 18px 20px; box-shadow: 0 12px 28px rgba(15,23,42,0.06); min-height: 118px; }
    .metric-premium .label { font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: #64748b; font-weight: 800; }
    .metric-premium .value { font-size: 30px; font-weight: 900; color: #0f172a; margin-top: 6px; }
    .metric-premium .sub { font-size: 12px; color: #94a3b8; margin-top: 6px; }
    .schedule-premium { background: linear-gradient(180deg, #ffffff 0%, #fcfdff 100%); border: 1px solid #e5e7eb; border-left: 6px solid #2563eb; border-radius: 22px; padding: 16px 18px; margin-bottom: 12px; box-shadow: 0 12px 24px rgba(15,23,42,0.05); }
    .schedule-premium .time { font-size: 24px; font-weight: 900; color: #0f172a; }
    .schedule-premium .client { font-size: 16px; font-weight: 800; color: #1e293b; margin-top: 2px; }
    .schedule-premium .meta { font-size: 13px; color: #64748b; margin-top: 3px; }
    .badge { display: inline-block; padding: 6px 10px; border-radius: 999px; font-size: 12px; font-weight: 800; margin-right: 6px; margin-top: 8px; }
    .b-ag { background: #dbeafe; color: #1d4ed8; }
    .b-co { background: #ede9fe; color: #6d28d9; }
    .b-em { background: #fef3c7; color: #b45309; }
    .b-ok { background: #dcfce7; color: #15803d; }
    .b-ca { background: #fee2e2; color: #b91c1c; }
    .mini-chip { display: inline-block; padding: 7px 10px; border-radius: 12px; background: #eff6ff; color: #1d4ed8; font-size: 12px; font-weight: 700; margin-right: 6px; margin-top: 6px; }
    .week-grid { display: grid; grid-template-columns: repeat(7, minmax(0,1fr)); gap: 12px; }
    .day-col { background: rgba(255,255,255,0.95); border: 1px solid #e5e7eb; border-radius: 20px; padding: 12px; box-shadow: 0 12px 24px rgba(15,23,42,0.05); min-height: 220px; }
    .day-title { font-size: 13px; font-weight: 900; color: #0f172a; margin-bottom: 10px; text-transform: uppercase; }
    .slot { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 8px 10px; margin-bottom: 8px; }
    .slot-time { font-size: 12px; font-weight: 900; color: #1d4ed8; }
    .slot-text { font-size: 12px; color: #334155; margin-top: 2px; }
    .login-box { max-width: 460px; margin: 40px auto; background: white; border: 1px solid #e5e7eb; border-radius: 24px; padding: 26px; box-shadow: 0 18px 40px rgba(15,23,42,0.08); }
    .pix-box { background: linear-gradient(180deg,#ffffff 0%,#f7fbff 100%); border:1px solid #dbeafe; border-radius:20px; padding:18px; text-align:center; }
    div[data-testid="stDataFrame"] { background: white; border-radius: 20px; border: 1px solid #e5e7eb; padding: 6px; box-shadow: 0 10px 24px rgba(15,23,42,0.05); }
    .stButton > button { border-radius: 14px; border: none; padding: 0.65rem 1rem; font-weight: 800; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; box-shadow: 0 10px 18px rgba(37,99,235,0.18); }
    .stButton > button:hover { background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%); color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================
# BANCO DE DADOS
# ==============================
conn = sqlite3.connect("agenda.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS empresas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_fantasia TEXT NOT NULL,
    razao_social TEXT,
    documento TEXT,
    telefone TEXT,
    email TEXT,
    pix_chave TEXT,
    pix_beneficiario TEXT,
    pix_cidade TEXT,
    ativa INTEGER DEFAULT 1
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    perfil TEXT NOT NULL,
    ativo INTEGER DEFAULT 1,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
)
''')

for ddl in [
'''CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    nome TEXT NOT NULL,
    telefone TEXT,
    observacao TEXT,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
)''',
'''CREATE TABLE IF NOT EXISTS profissionais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    nome TEXT NOT NULL,
    especialidade TEXT,
    telefone TEXT,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
)''',
'''CREATE TABLE IF NOT EXISTS servicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    nome TEXT NOT NULL,
    valor REAL,
    duracao INTEGER,
    descricao TEXT,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
)''',
'''CREATE TABLE IF NOT EXISTS agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    cliente TEXT NOT NULL,
    profissional TEXT NOT NULL,
    servico TEXT NOT NULL,
    data TEXT NOT NULL,
    hora TEXT NOT NULL,
    status TEXT NOT NULL,
    observacao TEXT,
    forma_pagamento TEXT,
    conta_financeira TEXT,
    valor_total REAL DEFAULT 0,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
)''',
'''CREATE TABLE IF NOT EXISTS agendamento_servicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    agendamento_id INTEGER NOT NULL,
    servico TEXT NOT NULL,
    valor REAL DEFAULT 0,
    duracao INTEGER DEFAULT 0,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id),
    FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id)
)''',
'''CREATE TABLE IF NOT EXISTS contas_financeiras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL,
    saldo_inicial REAL DEFAULT 0,
    observacao TEXT,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
)''',
'''CREATE TABLE IF NOT EXISTS movimentacoes_financeiras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    data TEXT NOT NULL,
    tipo TEXT NOT NULL,
    categoria TEXT NOT NULL,
    descricao TEXT,
    valor REAL NOT NULL,
    forma_pagamento TEXT,
    conta_nome TEXT,
    origem TEXT,
    agendamento_id INTEGER,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id),
    FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id)
)''',
'''CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL,
    unidade TEXT,
    estoque_atual REAL DEFAULT 0,
    estoque_minimo REAL DEFAULT 0,
    custo_unitario REAL DEFAULT 0,
    preco_venda REAL DEFAULT 0,
    observacao TEXT,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
)''',
'''CREATE TABLE IF NOT EXISTS estoque_movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,
    data TEXT NOT NULL,
    produto_id INTEGER NOT NULL,
    produto_nome TEXT NOT NULL,
    tipo_movimentacao TEXT NOT NULL,
    quantidade REAL NOT NULL,
    valor_unitario REAL DEFAULT 0,
    origem TEXT,
    observacao TEXT,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
)'''
]:
    c.execute(ddl)
conn.commit()


def garantir_coluna(tabela, coluna, definicao):
    info = c.execute(f"PRAGMA table_info({tabela})").fetchall()
    colunas = [item[1] for item in info]
    if coluna not in colunas:
        c.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")
        conn.commit()

for tabela in ["clientes", "profissionais", "servicos", "agendamentos", "agendamento_servicos", "contas_financeiras", "movimentacoes_financeiras", "produtos", "estoque_movimentacoes"]:
    garantir_coluna(tabela, "empresa_id", "INTEGER")
for col, defin in [("pix_chave", "TEXT"), ("pix_beneficiario", "TEXT"), ("pix_cidade", "TEXT")]:
    garantir_coluna("empresas", col, defin)
for col, defin in [("observacao", "TEXT"), ("forma_pagamento", "TEXT"), ("conta_financeira", "TEXT"), ("valor_total", "REAL DEFAULT 0")]:
    garantir_coluna("agendamentos", col, defin)
garantir_coluna("profissionais", "especialidade", "TEXT")
garantir_coluna("profissionais", "telefone", "TEXT")
garantir_coluna("servicos", "descricao", "TEXT")
garantir_coluna("clientes", "observacao", "TEXT")

# ==============================
# AUTENTICAÇÃO
# ==============================
def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def criar_admin_inicial():
    existe = c.execute("SELECT COUNT(*) as qtd FROM usuarios").fetchone()[0]
    if existe == 0:
        c.execute(
            "INSERT INTO usuarios (empresa_id, nome, email, senha_hash, perfil, ativo) VALUES (?, ?, ?, ?, ?, ?)",
            (None, "Administrador Master", "admin@agendapro.com", hash_senha("123456"), "master", 1),
        )
        conn.commit()


criar_admin_inicial()

for key, default in [("usuario_logado", None), ("empresa_id_logada", None), ("perfil_logado", None), ("empresa_nome_logada", None), ("usuario_id_logado", None)]:
    if key not in st.session_state:
        st.session_state[key] = default


def autenticar(email: str, senha: str):
    row = c.execute(
        "SELECT u.*, e.nome_fantasia as empresa_nome FROM usuarios u LEFT JOIN empresas e ON e.id = u.empresa_id WHERE u.email = ? AND u.ativo = 1",
        (email.strip().lower(),),
    ).fetchone()
    if not row:
        return None
    if row["senha_hash"] != hash_senha(senha):
        return None
    return row


def logout():
    for key in ["usuario_logado", "empresa_id_logada", "perfil_logado", "empresa_nome_logada", "usuario_id_logado"]:
        st.session_state[key] = None


def precisa_empresa_id() -> int:
    return st.session_state.empresa_id_logada


def filtro_empresa_master_ou_usuario(alias: str = ""):
    prefixo = f"{alias}." if alias else ""
    if st.session_state.perfil_logado == "master":
        return "1=1", ()
    return f"{prefixo}empresa_id = ?", (precisa_empresa_id(),)

# ==============================
# FUNÇÕES GERAIS
# ==============================
def executar(query, params=()):
    c.execute(query, params)
    conn.commit()
    return c


def consultar_df(query, params=()):
    return pd.read_sql_query(query, conn, params=params)


def moeda_br(valor):
    return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def caixa_busca(label, key):
    return st.text_input(label, key=key, placeholder="Digite para pesquisar...")


def topo(titulo, subtitulo):
    st.markdown(f"<div class='premium-topbar'><h1>{titulo}</h1><p>{subtitulo}</p></div>", unsafe_allow_html=True)


def card_metrica(rotulo, valor, sub=""):
    st.markdown(f"<div class='metric-premium'><div class='label'>{rotulo}</div><div class='value'>{valor}</div><div class='sub'>{sub}</div></div>", unsafe_allow_html=True)


def badge_status(status):
    mapa = {"Agendado":"b-ag", "Confirmado":"b-co", "Em atendimento":"b-em", "Concluído":"b-ok", "Cancelado":"b-ca"}
    return f"<span class='badge {mapa.get(status,'b-ag')}'>{status}</span>"


def obter_detalhes_servico(nome_servico):
    cond, params = filtro_empresa_master_ou_usuario()
    df = consultar_df(f"SELECT nome, valor, duracao FROM servicos WHERE {cond} AND nome = ? LIMIT 1", params + (nome_servico,))
    if df.empty:
        return {"nome": nome_servico, "valor": 0.0, "duracao": 0}
    linha = df.iloc[0]
    return {"nome": linha["nome"], "valor": float(linha["valor"] if linha["valor"] else 0), "duracao": int(linha["duracao"] if linha["duracao"] else 0)}


def listar_servicos_agendamento(agendamento_id):
    cond, params = filtro_empresa_master_ou_usuario()
    return consultar_df(f"SELECT id, servico, valor, duracao FROM agendamento_servicos WHERE {cond} AND agendamento_id = ? ORDER BY id", params + (int(agendamento_id),))


def total_agendamento(agendamento_id):
    df = listar_servicos_agendamento(agendamento_id)
    if df.empty:
        return 0.0, 0
    return float(df["valor"].sum()), int(df["duracao"].sum())


def obter_saldo_conta(conta_nome):
    cond, params = filtro_empresa_master_ou_usuario()
    df_conta = consultar_df(f"SELECT saldo_inicial FROM contas_financeiras WHERE {cond} AND nome = ? LIMIT 1", params + (conta_nome,))
    saldo_inicial = float(df_conta.iloc[0]["saldo_inicial"]) if not df_conta.empty else 0.0
    df_mov = consultar_df(f"SELECT tipo, valor FROM movimentacoes_financeiras WHERE {cond} AND conta_nome = ?", params + (conta_nome,))
    entradas = float(df_mov[df_mov["tipo"] == "Entrada"]["valor"].sum()) if not df_mov.empty else 0.0
    saidas = float(df_mov[df_mov["tipo"] == "Saída"]["valor"].sum()) if not df_mov.empty else 0.0
    return saldo_inicial + entradas - saidas


def registrar_movimentacao_financeira(data, tipo, categoria, descricao, valor, forma_pagamento, conta_nome, origem, agendamento_id=None):
    executar(
        "INSERT INTO movimentacoes_financeiras (empresa_id, data, tipo, categoria, descricao, valor, forma_pagamento, conta_nome, origem, agendamento_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (precisa_empresa_id(), str(data), tipo, categoria, descricao, float(valor), forma_pagamento, conta_nome, origem, agendamento_id),
    )


def atualizar_estoque(produto_id, quantidade, operacao):
    cond, params = filtro_empresa_master_ou_usuario()
    df = consultar_df(f"SELECT estoque_atual FROM produtos WHERE {cond} AND id = ?", params + (int(produto_id),))
    if df.empty:
        return
    estoque_atual = float(df.iloc[0]["estoque_atual"] if df.iloc[0]["estoque_atual"] else 0)
    novo = estoque_atual + float(quantidade) if operacao == "somar" else estoque_atual - float(quantidade)
    executar("UPDATE produtos SET estoque_atual = ? WHERE id = ?", (novo, int(produto_id)))


def registrar_movimentacao_estoque(data, produto_id, produto_nome, tipo_movimentacao, quantidade, valor_unitario, origem, observacao):
    executar(
        "INSERT INTO estoque_movimentacoes (empresa_id, data, produto_id, produto_nome, tipo_movimentacao, quantidade, valor_unitario, origem, observacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (precisa_empresa_id(), str(data), int(produto_id), produto_nome, tipo_movimentacao, float(quantidade), float(valor_unitario), origem, observacao),
    )
    if tipo_movimentacao == "Entrada mercadoria":
        atualizar_estoque(produto_id, quantidade, "somar")
    else:
        atualizar_estoque(produto_id, quantidade, "subtrair")


def buscar_produto_por_nome(nome_produto):
    cond, params = filtro_empresa_master_ou_usuario()
    return consultar_df(f"SELECT * FROM produtos WHERE {cond} AND UPPER(nome) = UPPER(?) LIMIT 1", params + (nome_produto.strip(),))


def cadastrar_produto_automatico(nome, unidade, custo_unitario, origem_obs="Importado por XML"):
    executar(
        "INSERT INTO produtos (empresa_id, nome, tipo, unidade, estoque_atual, estoque_minimo, custo_unitario, preco_venda, observacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (precisa_empresa_id(), nome.strip(), "Mercadoria", unidade.strip(), 0.0, 0.0, float(custo_unitario), 0.0, origem_obs),
    )
    return c.lastrowid


def detectar_namespace_xml(root):
    if root.tag.startswith("{"):
        return {"ns": root.tag.split("}")[0].strip("{")}
    return {"ns": ""}


def buscar_texto(node, caminhos, ns):
    for caminho in caminhos:
        achado = node.find(caminho, ns) if ns.get("ns") else node.find(caminho.replace("ns:", ""))
        if achado is not None and achado.text is not None:
            return achado.text.strip()
    return ""


def importar_xml_nfe_bytes(xml_bytes):
    tree = ET.parse(BytesIO(xml_bytes))
    root = tree.getroot()
    ns = detectar_namespace_xml(root)
    emitente = buscar_texto(root, [".//ns:emit/ns:xNome", ".//emit/xNome"], ns)
    numero_nota = buscar_texto(root, [".//ns:ide/ns:nNF", ".//ide/nNF"], ns)
    data_emissao = buscar_texto(root, [".//ns:ide/ns:dhEmi", ".//ns:ide/ns:dEmi", ".//ide/dhEmi", ".//ide/dEmi"], ns)
    detalhes = root.findall(".//ns:det", ns) if ns.get("ns") else root.findall(".//det")
    itens = []
    for det in detalhes:
        nome = buscar_texto(det, [".//ns:prod/ns:xProd", ".//prod/xProd"], ns)
        quantidade = buscar_texto(det, [".//ns:prod/ns:qCom", ".//prod/qCom"], ns)
        valor_unitario = buscar_texto(det, [".//ns:prod/ns:vUnCom", ".//prod/vUnCom"], ns)
        unidade = buscar_texto(det, [".//ns:prod/ns:uCom", ".//prod/uCom"], ns)
        if nome:
            itens.append({"nome": nome, "quantidade": float(quantidade.replace(",", ".")) if quantidade else 0.0, "valor_unitario": float(valor_unitario.replace(",", ".")) if valor_unitario else 0.0, "unidade": unidade})
    data_tratada = str(datetime.now().date())
    if data_emissao:
        try:
            data_tratada = pd.to_datetime(data_emissao).date().isoformat()
        except Exception:
            pass
    return {"emitente": emitente, "numero_nota": numero_nota, "data_emissao": data_tratada, "itens": itens}


def processar_importacao_xml(dados_xml, origem_texto):
    itens_importados = []
    for item in dados_xml["itens"]:
        nome = item["nome"].strip()
        quantidade = float(item["quantidade"])
        valor_unitario = float(item["valor_unitario"])
        unidade = item["unidade"].strip() if item["unidade"] else "un"
        df_prod = buscar_produto_por_nome(nome)
        if df_prod.empty:
            produto_id = cadastrar_produto_automatico(nome, unidade, valor_unitario, f"Produto criado automaticamente via XML - {origem_texto}")
            produto_nome = nome
        else:
            produto_id = int(df_prod.iloc[0]["id"])
            produto_nome = df_prod.iloc[0]["nome"]
            executar("UPDATE produtos SET custo_unitario = ?, unidade = ? WHERE id = ?", (valor_unitario, unidade, produto_id))
        registrar_movimentacao_estoque(dados_xml["data_emissao"], int(produto_id), produto_nome, "Entrada mercadoria", quantidade, valor_unitario, origem_texto, f"Importação XML NF-e {dados_xml['numero_nota']} - {dados_xml['emitente']}")
        itens_importados.append({"Produto": produto_nome, "Quantidade": quantidade, "Valor unitário": valor_unitario, "Total": quantidade * valor_unitario, "Unidade": unidade})
    return pd.DataFrame(itens_importados)


def render_agenda_cards(df):
    if df.empty:
        st.info("Nenhum agendamento encontrado para este filtro.")
        return
    for _, row in df.iterrows():
        total, dur = total_agendamento(row["id"])
        st.markdown(f"""
        <div class='schedule-premium'>
            <div class='time'>{str(row['hora'])[:5]}</div>
            <div class='client'>{row['cliente']}</div>
            <div class='meta'>{row['profissional']} • {row['servico'] if row['servico'] else 'Sem serviço'}</div>
            <div class='meta'>Total: {moeda_br(total)} • Duração: {dur} min</div>
            <div class='meta'>Pagamento: {row['forma_pagamento'] if pd.notna(row['forma_pagamento']) and row['forma_pagamento'] else '-'}</div>
            {badge_status(row['status'])}
        </div>
        """, unsafe_allow_html=True)


def semana_datas(base_date):
    start = pd.to_datetime(base_date) - pd.to_timedelta(pd.to_datetime(base_date).weekday(), unit="D")
    dias = [start + pd.to_timedelta(i, unit="D") for i in range(7)]
    nomes = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    return list(zip(nomes, dias))


def render_semana(df, base_date):
    blocos = []
    for nome, dia in semana_datas(base_date):
        chave = dia.date().isoformat()
        itens = df[df["data"] == chave].sort_values(["hora", "profissional"]) if not df.empty else pd.DataFrame()
        conteudo = "<div class='slot'><div class='slot-text'>Sem horários</div></div>" if itens.empty else ""
        for _, row in itens.iterrows():
            conteudo += f"<div class='slot'><div class='slot-time'>{str(row['hora'])[:5]}</div><div class='slot-text'><b>{row['cliente']}</b><br>{row['profissional']}<br>{row['servico']}</div></div>"
        blocos.append(f"<div class='day-col'><div class='day-title'>{nome}<br>{dia.strftime('%d/%m')}</div>{conteudo}</div>")
    st.markdown(f"<div class='week-grid'>{''.join(blocos)}</div>", unsafe_allow_html=True)


def crc16(payload):
    polinomio = 0x1021
    resultado = 0xFFFF
    for char in payload:
        resultado ^= ord(char) << 8
        for _ in range(8):
            if resultado & 0x8000:
                resultado = (resultado << 1) ^ polinomio
            else:
                resultado <<= 1
            resultado &= 0xFFFF
    return format(resultado, '04X')


def campo_pix(id_campo, valor):
    valor = str(valor)
    return f"{id_campo}{len(valor):02d}{valor}"


def gerar_payload_pix(chave, beneficiario, cidade, valor, txid="AGENDA01"):
    beneficiario = (beneficiario or "RECEBEDOR")[:25]
    cidade = (cidade or "SALVADOR")[:15]
    gui = campo_pix("00", "br.gov.bcb.pix")
    chave_campo = campo_pix("01", chave)
    merchant_account = campo_pix("26", gui + chave_campo)
    payload = ""
    payload += campo_pix("00", "01")
    payload += merchant_account
    payload += campo_pix("52", "0000")
    payload += campo_pix("53", "986")
    payload += campo_pix("54", f"{float(valor):.2f}")
    payload += campo_pix("58", "BR")
    payload += campo_pix("59", beneficiario)
    payload += campo_pix("60", cidade)
    payload += campo_pix("62", campo_pix("05", txid[:25]))
    payload += "6304"
    payload += crc16(payload)
    return payload


def gerar_qrcode_pix(payload):
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img


def empresa_atual_info():
    if st.session_state.perfil_logado == "master":
        return None
    row = c.execute("SELECT * FROM empresas WHERE id = ?", (st.session_state.empresa_id_logada,)).fetchone()
    return row

# ==============================
# LOGIN
# ==============================
if st.session_state.usuario_logado is None:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    topo("Agenda Pro Premium", "Login multiempresa com perfil master e perfil do terceiro. Usuário inicial: admin@agendapro.com | senha: 123456")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar no sistema"):
        usuario = autenticar(email, senha)
        if usuario:
            st.session_state.usuario_logado = usuario["nome"]
            st.session_state.usuario_id_logado = usuario["id"]
            st.session_state.empresa_id_logada = usuario["empresa_id"]
            st.session_state.perfil_logado = usuario["perfil"]
            st.session_state.empresa_nome_logada = usuario["empresa_nome"]
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==============================
# SIDEBAR
# ==============================
st.sidebar.markdown("## ✨ Agenda Pro Premium")
st.sidebar.caption(f"Usuário: {st.session_state.usuario_logado}")
st.sidebar.caption(f"Perfil: {st.session_state.perfil_logado}")
if st.session_state.perfil_logado == "master":
    st.sidebar.caption("Acesso global")
else:
    st.sidebar.caption(f"Empresa: {st.session_state.empresa_nome_logada}")
menu_opcoes = ["🏠 Dashboard", "🛎️ Recepção", "📅 Agenda", "👥 Clientes", "💼 Profissionais", "✂️ Serviços", "🗓️ Agendamentos", "💰 Financeiro", "📦 Produtos e Estoque", "🔐 Minha Conta"]
if st.session_state.perfil_logado == "master":
    menu_opcoes = ["⚙️ Administração"] + menu_opcoes
menu = st.sidebar.radio("Módulos", menu_opcoes)
if st.sidebar.button("Sair"):
    logout()
    st.rerun()

# ==============================
# ADMINISTRAÇÃO MASTER
# ==============================
if menu == "⚙️ Administração" and st.session_state.perfil_logado == "master":
    topo("Administração master", "Controle de empresas, usuários e parâmetros PIX para repasse do sistema a terceiros.")
    aba1, aba2 = st.tabs(["Empresas", "Usuários"])
    with aba1:
        st.markdown("<div class='section-title'>Cadastro de empresas</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            nome_fantasia = st.text_input("Nome fantasia")
            documento = st.text_input("Documento")
            telefone = st.text_input("Telefone")
        with c2:
            razao_social = st.text_input("Razão social")
            email = st.text_input("E-mail")
            ativa = st.selectbox("Situação", [1, 0], format_func=lambda x: "Ativa" if x == 1 else "Inativa")
        with c3:
            pix_chave = st.text_input("Chave PIX")
            pix_beneficiario = st.text_input("Beneficiário PIX")
            pix_cidade = st.text_input("Cidade PIX")
        if st.button("Salvar empresa"):
            if nome_fantasia.strip():
                executar(
                    "INSERT INTO empresas (nome_fantasia, razao_social, documento, telefone, email, pix_chave, pix_beneficiario, pix_cidade, ativa) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (nome_fantasia.strip(), razao_social.strip(), documento.strip(), telefone.strip(), email.strip(), pix_chave.strip(), pix_beneficiario.strip(), pix_cidade.strip(), int(ativa)),
                )
                st.success("Empresa cadastrada com sucesso!")
            else:
                st.warning("Informe o nome fantasia.")
        df_empresas = consultar_df("SELECT * FROM empresas ORDER BY nome_fantasia")
        if not df_empresas.empty:
            st.dataframe(df_empresas, use_container_width=True, hide_index=True)
    with aba2:
        st.markdown("<div class='section-title'>Cadastro de usuários</div>", unsafe_allow_html=True)
        df_empresas = consultar_df("SELECT id, nome_fantasia FROM empresas WHERE ativa = 1 ORDER BY nome_fantasia")
        if df_empresas.empty:
            st.warning("Cadastre uma empresa antes de criar usuários de terceiro.")
        else:
            empresa_map = {f"{row['id']} - {row['nome_fantasia']}": row['id'] for _, row in df_empresas.iterrows()}
            empresa_escolhida = st.selectbox("Empresa do usuário", list(empresa_map.keys()))
            nome = st.text_input("Nome do usuário")
            email = st.text_input("E-mail do usuário")
            senha = st.text_input("Senha inicial", type="password")
            perfil = st.selectbox("Perfil", ["empresa", "master"])
            ativo = st.selectbox("Situação", [1, 0], format_func=lambda x: "Ativo" if x == 1 else "Inativo")
            if st.button("Salvar usuário"):
                if nome.strip() and email.strip() and senha.strip():
                    emp_id = None if perfil == "master" else empresa_map[empresa_escolhida]
                    try:
                        executar(
                            "INSERT INTO usuarios (empresa_id, nome, email, senha_hash, perfil, ativo) VALUES (?, ?, ?, ?, ?, ?)",
                            (emp_id, nome.strip(), email.strip().lower(), hash_senha(senha), perfil, int(ativo)),
                        )
                        st.success("Usuário cadastrado com sucesso!")
                    except sqlite3.IntegrityError:
                        st.error("Já existe um usuário com esse e-mail.")
                else:
                    st.warning("Preencha nome, e-mail e senha.")
        df_usuarios = consultar_df("SELECT u.id, u.nome, u.email, u.perfil, u.ativo, e.nome_fantasia as empresa FROM usuarios u LEFT JOIN empresas e ON e.id = u.empresa_id ORDER BY u.nome")
        if not df_usuarios.empty:
            st.dataframe(df_usuarios, use_container_width=True, hide_index=True)

# ==============================
# MINHA CONTA
# ==============================
if menu == "🔐 Minha Conta":
    topo("Minha conta", "Troca de senha e visualização do acesso atual.")
    st.markdown(f"<div class='glass-card'><b>Usuário:</b> {st.session_state.usuario_logado}<br><b>Perfil:</b> {st.session_state.perfil_logado}<br><b>Empresa:</b> {st.session_state.empresa_nome_logada or 'Acesso global master'}</div>", unsafe_allow_html=True)
    senha_atual = st.text_input("Senha atual", type="password")
    nova_senha = st.text_input("Nova senha", type="password")
    confirmar_senha = st.text_input("Confirmar nova senha", type="password")
    if st.button("Atualizar senha"):
        row = c.execute("SELECT senha_hash FROM usuarios WHERE id = ?", (st.session_state.usuario_id_logado,)).fetchone()
        if not row or row["senha_hash"] != hash_senha(senha_atual):
            st.error("Senha atual inválida.")
        elif not nova_senha.strip() or nova_senha != confirmar_senha:
            st.error("A nova senha está vazia ou não confere.")
        else:
            executar("UPDATE usuarios SET senha_hash = ? WHERE id = ?", (hash_senha(nova_senha), st.session_state.usuario_id_logado))
            st.success("Senha atualizada com sucesso!")

# ==============================
# RECEPÇÃO
# ==============================
if menu == "🛎️ Recepção":
    topo("Recepção / Balcão", "Tela rápida para atendimento do dia, ações imediatas e consulta de histórico de agendamentos.")
    cond, params = filtro_empresa_master_ou_usuario()

    col_r1, col_r2, col_r3 = st.columns([1, 1, 1])
    with col_r1:
        data_recepcao = st.date_input("Data da recepção", value=datetime.now().date(), key="rec_data")
    with col_r2:
        termo_recepcao = st.text_input("Buscar cliente / profissional / serviço", key="rec_busca", placeholder="Filtro automático")
    with col_r3:
        status_recepcao = st.selectbox("Status", ["Todos", "Agendado", "Confirmado", "Em atendimento", "Concluído", "Cancelado"], key="rec_status")

    query_rec = f"SELECT id, data, hora, cliente, profissional, servico, status, forma_pagamento, valor_total FROM agendamentos WHERE {cond} AND data = ?"
    params_rec = params + (str(data_recepcao),)
    if termo_recepcao.strip():
        like = f"%{termo_recepcao.strip()}%"
        query_rec += " AND (cliente LIKE ? OR profissional LIKE ? OR servico LIKE ?)"
        params_rec += (like, like, like)
    if status_recepcao != "Todos":
        query_rec += " AND status = ?"
        params_rec += (status_recepcao,)
    query_rec += " ORDER BY hora"

    df_recepcao = consultar_df(query_rec, params_rec)
    st.markdown("<div class='section-title'>Atendimentos do dia</div>", unsafe_allow_html=True)
    if df_recepcao.empty:
        st.info("Nenhum atendimento encontrado com esses filtros.")
    else:
        render_agenda_cards(df_recepcao)
        st.dataframe(df_recepcao, width='stretch', hide_index=True)
        atendimento_id = st.selectbox("Selecione o ID para ação rápida", df_recepcao["id"].tolist(), key="rec_id")
        total_at, _ = total_agendamento(atendimento_id)
        cta1, cta2, cta3, cta4 = st.columns(4)
        with cta1:
            if st.button("Confirmar chegada"):
                executar("UPDATE agendamentos SET status = ? WHERE id = ?", ("Confirmado", int(atendimento_id)))
                st.success("Cliente confirmado na recepção.")
        with cta2:
            if st.button("Iniciar atendimento"):
                executar("UPDATE agendamentos SET status = ? WHERE id = ?", ("Em atendimento", int(atendimento_id)))
                st.success("Atendimento iniciado.")
        with cta3:
            if st.button("Finalizar da recepção"):
                executar("UPDATE agendamentos SET status = ?, valor_total = ? WHERE id = ?", ("Concluído", float(total_at), int(atendimento_id)))
                st.success("Atendimento finalizado.")
        with cta4:
            if st.button("Cancelar da recepção"):
                executar("UPDATE agendamentos SET status = ? WHERE id = ?", ("Cancelado", int(atendimento_id)))
                st.success("Atendimento cancelado.")

    st.markdown("<div class='section-title'>Histórico de agendamentos</div>", unsafe_allow_html=True)
    col_h1, col_h2, col_h3 = st.columns([1, 1, 1])
    with col_h1:
        dt_ini = st.date_input("De", value=datetime.now().date(), key="hist_ini")
    with col_h2:
        dt_fim = st.date_input("Até", value=datetime.now().date(), key="hist_fim")
    with col_h3:
        termo_hist = st.text_input("Buscar no histórico", key="hist_busca", placeholder="Cliente, profissional, serviço...")

    query_hist = f"SELECT id, data, hora, cliente, profissional, servico, status, forma_pagamento, conta_financeira, valor_total, observacao FROM agendamentos WHERE {cond} AND data >= ? AND data <= ?"
    params_hist = params + (str(dt_ini), str(dt_fim))
    if termo_hist.strip():
        likeh = f"%{termo_hist.strip()}%"
        query_hist += " AND (cliente LIKE ? OR profissional LIKE ? OR servico LIKE ? OR status LIKE ?)"
        params_hist += (likeh, likeh, likeh, likeh)
    query_hist += " ORDER BY data DESC, hora DESC"
    df_hist = consultar_df(query_hist, params_hist)
    if df_hist.empty:
        st.info("Nenhum histórico encontrado nesse período.")
    else:
        st.dataframe(df_hist, width='stretch', hide_index=True)

# ==============================
# DASHBOARD
# ==============================
if menu == "🏠 Dashboard":
    topo("Dashboard premium", "Ambiente filtrado pelo seu acesso. O terceiro vê apenas os próprios dados; você, como master, pode ver tudo.")
    hoje = datetime.now().strftime("%Y-%m-%d")
    cond, params = filtro_empresa_master_ou_usuario()
    df_hoje = consultar_df(f"SELECT id, data, hora, cliente, profissional, servico, status, forma_pagamento, conta_financeira, valor_total FROM agendamentos WHERE {cond} AND data = ? ORDER BY hora", params + (hoje,))
    receita_hoje = float(df_hoje[df_hoje["status"] == "Concluído"]["valor_total"].sum()) if not df_hoje.empty else 0.0
    concluidos = len(df_hoje[df_hoje["status"] == "Concluído"]) if not df_hoje.empty else 0
    cancelados = len(df_hoje[df_hoje["status"] == "Cancelado"]) if not df_hoje.empty else 0
    pendentes = len(df_hoje[df_hoje["status"].isin(["Agendado", "Confirmado", "Em atendimento"])]) if not df_hoje.empty else 0
    c1, c2, c3, c4 = st.columns(4)
    with c1: card_metrica("Agenda do dia", len(df_hoje), "Horários registrados")
    with c2: card_metrica("Pendentes", pendentes, "Ainda em aberto")
    with c3: card_metrica("Concluídos", concluidos, "Finalizados com sucesso")
    with c4: card_metrica("Receita", moeda_br(receita_hoje), "Movimento concluído")
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown("<div class='section-title'>Agenda premium de hoje</div>", unsafe_allow_html=True)
        render_agenda_cards(df_hoje)
    with col2:
        st.markdown("<div class='section-title'>Indicadores rápidos</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='glass-card'><span class='mini-chip'>Cancelados: {cancelados}</span><span class='mini-chip'>Profissionais ativos: {df_hoje['profissional'].nunique() if not df_hoje.empty else 0}</span><span class='mini-chip'>Clientes do dia: {df_hoje['cliente'].nunique() if not df_hoje.empty else 0}</span></div>", unsafe_allow_html=True)

# ==============================
# AGENDA
# ==============================
if menu == "📅 Agenda":
    topo("Agenda premium", "Visual semanal e diária, com filtro respeitando o acesso do usuário logado.")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1: data_base = st.date_input("Semana base", value=datetime.now().date(), key="agenda_premium_base")
    with c2: modo = st.selectbox("Modo de visualização", ["Semanal", "Diário"], key="agenda_modo")
    cond_prof, params_prof = filtro_empresa_master_ou_usuario()
    df_prof = consultar_df(f"SELECT nome FROM profissionais WHERE {cond_prof} ORDER BY nome", params_prof)
    with c3:
        profs = ["Todos"] + (df_prof["nome"].tolist() if not df_prof.empty else [])
        profissional_filtro = st.selectbox("Profissional", profs, key="agenda_prof_premium")
    cond, params = filtro_empresa_master_ou_usuario()
    if modo == "Semanal":
        inicio = pd.to_datetime(data_base) - pd.to_timedelta(pd.to_datetime(data_base).weekday(), unit="D")
        fim = inicio + pd.to_timedelta(6, unit="D")
        if profissional_filtro == "Todos":
            df_semana = consultar_df(f"SELECT id, data, hora, cliente, profissional, servico, status, forma_pagamento, conta_financeira, valor_total FROM agendamentos WHERE {cond} AND data >= ? AND data <= ? ORDER BY data, hora", params + (inicio.date().isoformat(), fim.date().isoformat()))
        else:
            df_semana = consultar_df(f"SELECT id, data, hora, cliente, profissional, servico, status, forma_pagamento, conta_financeira, valor_total FROM agendamentos WHERE {cond} AND data >= ? AND data <= ? AND profissional = ? ORDER BY data, hora", params + (inicio.date().isoformat(), fim.date().isoformat(), profissional_filtro))
        render_semana(df_semana, data_base)
    else:
        if profissional_filtro == "Todos":
            df_dia = consultar_df(f"SELECT id, data, hora, cliente, profissional, servico, status, forma_pagamento, conta_financeira, valor_total FROM agendamentos WHERE {cond} AND data = ? ORDER BY profissional, hora", params + (str(data_base),))
        else:
            df_dia = consultar_df(f"SELECT id, data, hora, cliente, profissional, servico, status, forma_pagamento, conta_financeira, valor_total FROM agendamentos WHERE {cond} AND data = ? AND profissional = ? ORDER BY hora", params + (str(data_base), profissional_filtro))
        if profissional_filtro == "Todos" and not df_dia.empty:
            for profissional, grupo in df_dia.groupby("profissional"):
                st.markdown(f"<div class='section-title'>{profissional}</div>", unsafe_allow_html=True)
                render_agenda_cards(grupo)
        else:
            render_agenda_cards(df_dia)

# ==============================
# CLIENTES
# ==============================
if menu == "👥 Clientes":
    topo("Clientes", "Cadastro e manutenção de clientes dentro da empresa logada.")
    aba1, aba2, aba3 = st.tabs(["Cadastrar", "Pesquisar / Alterar", "Excluir"])
    with aba1:
        col1, col2 = st.columns(2)
        with col1: nome = st.text_input("Nome do cliente", key="cli_nome")
        with col2: telefone = st.text_input("Telefone", key="cli_tel")
        observacao = st.text_area("Observação", key="cli_obs")
        if st.button("Salvar cliente"):
            if nome.strip():
                executar("INSERT INTO clientes (empresa_id, nome, telefone, observacao) VALUES (?, ?, ?, ?)", (precisa_empresa_id(), nome.strip(), telefone.strip(), observacao.strip()))
                st.success("Cliente cadastrado com sucesso!")
            else:
                st.warning("Informe o nome do cliente.")
    with aba2:
        termo = caixa_busca("Pesquisar cliente", "busca_cliente")
        cond, params = filtro_empresa_master_ou_usuario()
        df_clientes = consultar_df(f"SELECT * FROM clientes WHERE {cond} AND (nome LIKE ? OR telefone LIKE ?) ORDER BY nome", params + (f"%{termo}%", f"%{termo}%")) if termo.strip() else consultar_df(f"SELECT * FROM clientes WHERE {cond} ORDER BY nome", params)
        if df_clientes.empty:
            st.info("Nenhum cliente encontrado.")
        else:
            st.dataframe(df_clientes, use_container_width=True, hide_index=True)
            cliente_id = st.selectbox("Selecione o ID do cliente para alterar", df_clientes["id"].tolist(), key="cliente_id_editar")
            dados = consultar_df("SELECT * FROM clientes WHERE id = ?", (int(cliente_id),)).iloc[0]
            novo_nome = st.text_input("Nome", value=dados["nome"], key="ed_cli_nome")
            novo_telefone = st.text_input("Telefone", value=dados["telefone"] if dados["telefone"] else "", key="ed_cli_tel")
            nova_obs = st.text_area("Observação", value=dados["observacao"] if dados["observacao"] else "", key="ed_cli_obs")
            if st.button("Atualizar cliente"):
                executar("UPDATE clientes SET nome = ?, telefone = ?, observacao = ? WHERE id = ?", (novo_nome.strip(), novo_telefone.strip(), nova_obs.strip(), int(cliente_id)))
                st.success("Cliente atualizado com sucesso!")
    with aba3:
        cond, params = filtro_empresa_master_ou_usuario()
        df_clientes_exc = consultar_df(f"SELECT * FROM clientes WHERE {cond} ORDER BY nome", params)
        if df_clientes_exc.empty:
            st.info("Nenhum cliente para excluir.")
        else:
            st.dataframe(df_clientes_exc, use_container_width=True, hide_index=True)
            cliente_exc = st.selectbox("Selecione o ID do cliente para excluir", df_clientes_exc["id"].tolist(), key="cliente_exc")
            if st.button("Excluir cliente"):
                executar("DELETE FROM clientes WHERE id = ?", (int(cliente_exc),))
                st.success("Cliente excluído com sucesso!")

# ==============================
# PROFISSIONAIS
# ==============================
if menu == "💼 Profissionais":
    topo("Profissionais", "Equipe, especialidades e organização operacional por empresa.")
    aba1, aba2, aba3 = st.tabs(["Cadastrar", "Pesquisar / Alterar", "Excluir"])
    with aba1:
        c1, c2, c3 = st.columns(3)
        with c1: nome = st.text_input("Nome do profissional", key="prof_nome")
        with c2: especialidade = st.text_input("Especialidade", key="prof_esp")
        with c3: telefone = st.text_input("Telefone", key="prof_tel")
        if st.button("Salvar profissional"):
            if nome.strip():
                executar("INSERT INTO profissionais (empresa_id, nome, especialidade, telefone) VALUES (?, ?, ?, ?)", (precisa_empresa_id(), nome.strip(), especialidade.strip(), telefone.strip()))
                st.success("Profissional cadastrado com sucesso!")
            else:
                st.warning("Informe o nome do profissional.")
    with aba2:
        termo = caixa_busca("Pesquisar profissional", "busca_prof")
        cond, params = filtro_empresa_master_ou_usuario()
        df_prof = consultar_df(f"SELECT * FROM profissionais WHERE {cond} AND (nome LIKE ? OR especialidade LIKE ? OR telefone LIKE ?) ORDER BY nome", params + (f"%{termo}%", f"%{termo}%", f"%{termo}%")) if termo.strip() else consultar_df(f"SELECT * FROM profissionais WHERE {cond} ORDER BY nome", params)
        if df_prof.empty:
            st.info("Nenhum profissional encontrado.")
        else:
            st.dataframe(df_prof, use_container_width=True, hide_index=True)
            prof_id = st.selectbox("Selecione o ID do profissional para alterar", df_prof["id"].tolist(), key="prof_id_editar")
            dados = consultar_df("SELECT * FROM profissionais WHERE id = ?", (int(prof_id),)).iloc[0]
            novo_nome = st.text_input("Nome", value=dados["nome"], key="ed_prof_nome")
            nova_esp = st.text_input("Especialidade", value=dados["especialidade"] if dados["especialidade"] else "", key="ed_prof_esp")
            novo_tel = st.text_input("Telefone", value=dados["telefone"] if dados["telefone"] else "", key="ed_prof_tel")
            if st.button("Atualizar profissional"):
                executar("UPDATE profissionais SET nome = ?, especialidade = ?, telefone = ? WHERE id = ?", (novo_nome.strip(), nova_esp.strip(), novo_tel.strip(), int(prof_id)))
                st.success("Profissional atualizado com sucesso!")
    with aba3:
        cond, params = filtro_empresa_master_ou_usuario()
        df_prof_exc = consultar_df(f"SELECT * FROM profissionais WHERE {cond} ORDER BY nome", params)
        if df_prof_exc.empty:
            st.info("Nenhum profissional para excluir.")
        else:
            st.dataframe(df_prof_exc, use_container_width=True, hide_index=True)
            prof_exc = st.selectbox("Selecione o ID do profissional para excluir", df_prof_exc["id"].tolist(), key="prof_exc")
            if st.button("Excluir profissional"):
                executar("DELETE FROM profissionais WHERE id = ?", (int(prof_exc),))
                st.success("Profissional excluído com sucesso!")

# ==============================
# SERVIÇOS
# ==============================
if menu == "✂️ Serviços":
    topo("Serviços", "Preço, duração e catálogo de atendimentos da empresa logada.")
    aba1, aba2, aba3 = st.tabs(["Cadastrar", "Pesquisar / Alterar", "Excluir"])
    with aba1:
        c1, c2, c3 = st.columns(3)
        with c1: nome = st.text_input("Nome do serviço", key="serv_nome")
        with c2: valor = st.number_input("Valor", min_value=0.0, step=1.0, key="serv_valor")
        with c3: duracao = st.number_input("Duração (min)", min_value=0, step=5, key="serv_dur")
        descricao = st.text_area("Descrição", key="serv_desc")
        if st.button("Salvar serviço"):
            if nome.strip():
                executar("INSERT INTO servicos (empresa_id, nome, valor, duracao, descricao) VALUES (?, ?, ?, ?, ?)", (precisa_empresa_id(), nome.strip(), float(valor), int(duracao), descricao.strip()))
                st.success("Serviço cadastrado com sucesso!")
            else:
                st.warning("Informe o nome do serviço.")
    with aba2:
        termo = caixa_busca("Pesquisar serviço", "busca_serv")
        cond, params = filtro_empresa_master_ou_usuario()
        df_serv = consultar_df(f"SELECT * FROM servicos WHERE {cond} AND (nome LIKE ? OR descricao LIKE ?) ORDER BY nome", params + (f"%{termo}%", f"%{termo}%")) if termo.strip() else consultar_df(f"SELECT * FROM servicos WHERE {cond} ORDER BY nome", params)
        if df_serv.empty:
            st.info("Nenhum serviço encontrado.")
        else:
            st.dataframe(df_serv, use_container_width=True, hide_index=True)
            serv_id = st.selectbox("Selecione o ID do serviço para alterar", df_serv["id"].tolist(), key="serv_id_editar")
            dados = consultar_df("SELECT * FROM servicos WHERE id = ?", (int(serv_id),)).iloc[0]
            novo_nome = st.text_input("Nome", value=dados["nome"], key="ed_serv_nome")
            novo_valor = st.number_input("Valor", min_value=0.0, step=1.0, value=float(dados["valor"] if dados["valor"] else 0), key="ed_serv_valor")
            nova_duracao = st.number_input("Duração (min)", min_value=0, step=5, value=int(dados["duracao"] if dados["duracao"] else 0), key="ed_serv_dur")
            nova_desc = st.text_area("Descrição", value=dados["descricao"] if dados["descricao"] else "", key="ed_serv_desc")
            if st.button("Atualizar serviço"):
                executar("UPDATE servicos SET nome = ?, valor = ?, duracao = ?, descricao = ? WHERE id = ?", (novo_nome.strip(), float(novo_valor), int(nova_duracao), nova_desc.strip(), int(serv_id)))
                st.success("Serviço atualizado com sucesso!")
    with aba3:
        cond, params = filtro_empresa_master_ou_usuario()
        df_serv_exc = consultar_df(f"SELECT * FROM servicos WHERE {cond} ORDER BY nome", params)
        if df_serv_exc.empty:
            st.info("Nenhum serviço para excluir.")
        else:
            st.dataframe(df_serv_exc, use_container_width=True, hide_index=True)
            serv_exc = st.selectbox("Selecione o ID do serviço para excluir", df_serv_exc["id"].tolist(), key="serv_exc")
            if st.button("Excluir serviço"):
                executar("DELETE FROM servicos WHERE id = ?", (int(serv_exc),))
                st.success("Serviço excluído com sucesso!")

# ==============================
# AGENDAMENTOS + PIX
# ==============================
if menu == "🗓️ Agendamentos":
    topo("Agendamentos", "Fluxo completo do atendimento com dados separados por empresa e QR Code PIX para recebimento.")
    aba1, aba2, aba3 = st.tabs(["Novo agendamento", "Pesquisar / Alterar", "Excluir"])
    with aba1:
        cond, params = filtro_empresa_master_ou_usuario()
        df_clientes = consultar_df(f"SELECT nome FROM clientes WHERE {cond} ORDER BY nome", params)
        df_profissionais = consultar_df(f"SELECT nome FROM profissionais WHERE {cond} ORDER BY nome", params)
        df_servicos = consultar_df(f"SELECT nome FROM servicos WHERE {cond} ORDER BY nome", params)
        df_contas = consultar_df(f"SELECT nome FROM contas_financeiras WHERE {cond} ORDER BY nome", params)
        clientes = df_clientes["nome"].tolist() if not df_clientes.empty else []
        profissionais = df_profissionais["nome"].tolist() if not df_profissionais.empty else []
        servicos = df_servicos["nome"].tolist() if not df_servicos.empty else []
        contas = df_contas["nome"].tolist() if not df_contas.empty else []
        if not clientes or not profissionais or not servicos:
            st.warning("Cadastre pelo menos 1 cliente, 1 profissional e 1 serviço antes de agendar.")
        else:
            c1, c2, c3, c4 = st.columns(4)
            with c1: cliente = st.selectbox("Cliente", clientes, key="ag_cliente")
            with c2: profissional = st.selectbox("Profissional", profissionais, key="ag_prof")
            with c3: data = st.date_input("Data", key="ag_data")
            with c4: hora = st.time_input("Hora", key="ag_hora")
            c5, c6, c7 = st.columns(3)
            with c5: status = st.selectbox("Status", ["Agendado", "Confirmado", "Em atendimento", "Concluído", "Cancelado"], key="ag_status")
            with c6: forma_pagamento = st.selectbox("Forma de pagamento", ["Dinheiro", "PIX", "Cartão de Débito", "Cartão de Crédito", "Transferência", "Fiado"], key="ag_fp")
            with c7: conta_financeira = st.selectbox("Banco / Caixa", contas if contas else ["Sem conta cadastrada"], key="ag_conta")
            observacao = st.text_area("Observação", key="ag_obs")
            st.markdown("<div class='section-title'>Serviços do atendimento</div>", unsafe_allow_html=True)
            qtd_servicos = st.number_input("Quantidade de serviços", min_value=1, max_value=10, value=1, step=1, key="qtd_servicos")
            servicos_escolhidos = [st.selectbox(f"Serviço {i+1}", servicos, key=f"ag_serv_{i}") for i in range(int(qtd_servicos))]
            detalhes = [obter_detalhes_servico(nome) for nome in servicos_escolhidos] if servicos_escolhidos else []
            valor_total = sum(item["valor"] for item in detalhes)
            duracao_total = sum(item["duracao"] for item in detalhes)
            st.markdown(f"<div class='glass-card'><span class='mini-chip'>Valor previsto: {moeda_br(valor_total)}</span><span class='mini-chip'>Duração: {duracao_total} min</span></div>", unsafe_allow_html=True)
            if st.button("Salvar agendamento"):
                servico_principal = servicos_escolhidos[0] if servicos_escolhidos else ""
                cur = executar("INSERT INTO agendamentos (empresa_id, cliente, profissional, servico, data, hora, status, observacao, forma_pagamento, conta_financeira, valor_total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (precisa_empresa_id(), cliente, profissional, servico_principal, str(data), str(hora), status, observacao.strip(), forma_pagamento, conta_financeira, float(valor_total)))
                agendamento_id = cur.lastrowid
                for nome_servico in servicos_escolhidos:
                    d = obter_detalhes_servico(nome_servico)
                    executar("INSERT INTO agendamento_servicos (empresa_id, agendamento_id, servico, valor, duracao) VALUES (?, ?, ?, ?, ?)", (precisa_empresa_id(), int(agendamento_id), d["nome"], d["valor"], d["duracao"]))
                if status == "Concluído" and conta_financeira != "Sem conta cadastrada":
                    registrar_movimentacao_financeira(data, "Entrada", "Recebimento de serviço", f"Atendimento - {cliente}", valor_total, forma_pagamento, conta_financeira, "Agendamento", int(agendamento_id))
                st.success("Agendamento salvo com sucesso!")
    with aba2:
        termo = caixa_busca("Pesquisar agendamento", "busca_agendamento_modulo")
        cond, params = filtro_empresa_master_ou_usuario()
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1:
            termo = caixa_busca("Pesquisar agendamento", "busca_agendamento_lista")
        with col_f2:
            filtro_status = st.selectbox("Filtrar status", ["Todos", "Agendado", "Confirmado", "Em atendimento", "Concluído", "Cancelado"], key="agendamento_filtro_status")
        with col_f3:
            filtro_data = st.text_input("Filtrar data", key="agendamento_filtro_data", placeholder="AAAA-MM-DD")
        query_ag = f"SELECT * FROM agendamentos WHERE {cond}"
        params_ag = params
        if termo.strip():
            like = f"%{termo.strip()}%"
            query_ag += " AND (cliente LIKE ? OR profissional LIKE ? OR servico LIKE ? OR data LIKE ? OR status LIKE ?)"
            params_ag += (like, like, like, like, like)
        if filtro_status != "Todos":
            query_ag += " AND status = ?"
            params_ag += (filtro_status,)
        if filtro_data.strip():
            query_ag += " AND data LIKE ?"
            params_ag += (f"%{filtro_data.strip()}%",)
        query_ag += " ORDER BY data DESC, hora DESC"
        df_ag = consultar_df(query_ag, params_ag)
        if df_ag.empty:
            st.info("Nenhum agendamento encontrado.")
        else:
            st.dataframe(df_ag, use_container_width=True, hide_index=True)
            ag_id = st.selectbox("Selecione o ID do agendamento para alterar", df_ag["id"].tolist(), key="ag_id_editar")
            dados = consultar_df("SELECT * FROM agendamentos WHERE id = ?", (int(ag_id),)).iloc[0]
            df_clientes = consultar_df(f"SELECT nome FROM clientes WHERE {cond} ORDER BY nome", params)
            df_profissionais = consultar_df(f"SELECT nome FROM profissionais WHERE {cond} ORDER BY nome", params)
            df_servicos = consultar_df(f"SELECT nome FROM servicos WHERE {cond} ORDER BY nome", params)
            df_contas = consultar_df(f"SELECT nome FROM contas_financeiras WHERE {cond} ORDER BY nome", params)
            clientes = df_clientes["nome"].tolist()
            profissionais = df_profissionais["nome"].tolist()
            servicos_cadastrados = df_servicos["nome"].tolist()
            contas = df_contas["nome"].tolist()
            servicos_vinculados = listar_servicos_agendamento(ag_id)
            cliente_idx = clientes.index(dados["cliente"]) if dados["cliente"] in clientes else 0
            prof_idx = profissionais.index(dados["profissional"]) if dados["profissional"] in profissionais else 0
            status_opcoes = ["Agendado", "Confirmado", "Em atendimento", "Concluído", "Cancelado"]
            status_idx = status_opcoes.index(dados["status"]) if dados["status"] in status_opcoes else 0
            fp_opcoes = ["Dinheiro", "PIX", "Cartão de Débito", "Cartão de Crédito", "Transferência", "Fiado"]
            fp_idx = fp_opcoes.index(dados["forma_pagamento"]) if dados["forma_pagamento"] in fp_opcoes else 0
            contas_opcoes = contas if contas else ["Sem conta cadastrada"]
            conta_idx = contas_opcoes.index(dados["conta_financeira"]) if dados["conta_financeira"] in contas_opcoes else 0
            c1, c2, c3, c4 = st.columns(4)
            with c1: novo_cliente = st.selectbox("Cliente", clientes, index=cliente_idx, key="ed_ag_cliente")
            with c2: novo_prof = st.selectbox("Profissional", profissionais, index=prof_idx, key="ed_ag_prof")
            with c3: nova_data = st.date_input("Data", value=pd.to_datetime(dados["data"]).date(), key="ed_ag_data")
            with c4: nova_hora = st.time_input("Hora", value=pd.to_datetime(dados["hora"]).time(), key="ed_ag_hora")
            c5, c6, c7 = st.columns(3)
            with c5: novo_status = st.selectbox("Status", status_opcoes, index=status_idx, key="ed_ag_status")
            with c6: nova_fp = st.selectbox("Forma de pagamento", fp_opcoes, index=fp_idx, key="ed_ag_fp")
            with c7: nova_conta = st.selectbox("Banco / Caixa", contas_opcoes, index=conta_idx, key="ed_ag_conta")
            nova_obs = st.text_area("Observação", value=dados["observacao"] if dados["observacao"] else "", key="ed_ag_obs")
            if servicos_vinculados.empty:
                quantidade_existente = 1
                nomes_existentes = [servicos_cadastrados[0]] if servicos_cadastrados else []
                st.warning("Este agendamento ainda não possui serviços vinculados.")
            else:
                quantidade_existente = len(servicos_vinculados)
                nomes_existentes = servicos_vinculados["servico"].tolist()
                st.dataframe(servicos_vinculados, use_container_width=True, hide_index=True)
            novos_servicos = []
            if servicos_cadastrados:
                qtd_edicao = st.number_input("Quantidade de serviços deste agendamento", min_value=1, max_value=10, value=max(1, quantidade_existente), step=1, key="qtd_servicos_edit")
                for i in range(int(qtd_edicao)):
                    valor_padrao = nomes_existentes[i] if i < len(nomes_existentes) and nomes_existentes[i] in servicos_cadastrados else servicos_cadastrados[0]
                    idx = servicos_cadastrados.index(valor_padrao) if valor_padrao in servicos_cadastrados else 0
                    novos_servicos.append(st.selectbox(f"Serviço {i+1}", servicos_cadastrados, index=idx, key=f"ed_ag_serv_{i}"))
            total_edit = sum(obter_detalhes_servico(nome)["valor"] for nome in novos_servicos)
            duracao_edit = sum(obter_detalhes_servico(nome)["duracao"] for nome in novos_servicos)
            st.markdown(f"<div class='glass-card'><span class='mini-chip'>Valor previsto: {moeda_br(total_edit)}</span><span class='mini-chip'>Duração: {duracao_edit} min</span>{badge_status(novo_status)}</div>", unsafe_allow_html=True)
            empresa_info = empresa_atual_info()
            if nova_fp == "PIX" and empresa_info and empresa_info["pix_chave"] and total_edit > 0:
                try:
                    payload = gerar_payload_pix(
                        empresa_info["pix_chave"],
                        empresa_info["pix_beneficiario"] or empresa_info["nome_fantasia"],
                        empresa_info["pix_cidade"] or "SALVADOR",
                        total_edit,
                        txid=f"AG{int(ag_id)}"
                    )
                    img = gerar_qrcode_pix(payload)
                    colpix1, colpix2 = st.columns([1, 1.2])
                    with colpix1:
                        st.markdown("<div class='pix-box'>", unsafe_allow_html=True)
                        st.image(img, caption="QR Code PIX", width=230)
                        st.markdown("</div>", unsafe_allow_html=True)
                    with colpix2:
                        st.markdown("<div class='section-title'>Recebimento PIX</div>", unsafe_allow_html=True)
                        st.write(f"**Beneficiário:** {empresa_info['pix_beneficiario'] or empresa_info['nome_fantasia']}")
                        st.write(f"**Chave PIX:** {empresa_info['pix_chave']}")
                        st.write(f"**Valor:** {moeda_br(total_edit)}")
                        st.text_area("PIX copia e cola", payload, height=180)
                except Exception as e:
                    st.warning(f"Não foi possível gerar o QR Code PIX: {e}")
            elif nova_fp == "PIX":
                st.info("Cadastre a chave PIX da empresa na Administração para gerar QR Code.")
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("Atualizar agendamento"):
                    servico_principal = novos_servicos[0] if novos_servicos else dados["servico"]
                    executar("UPDATE agendamentos SET cliente = ?, profissional = ?, servico = ?, data = ?, hora = ?, status = ?, observacao = ?, forma_pagamento = ?, conta_financeira = ?, valor_total = ? WHERE id = ?", (novo_cliente, novo_prof, servico_principal, str(nova_data), str(nova_hora), novo_status, nova_obs.strip(), nova_fp, nova_conta, float(total_edit), int(ag_id)))
                    executar("DELETE FROM agendamento_servicos WHERE agendamento_id = ?", (int(ag_id),))
                    for nome_servico in novos_servicos:
                        det = obter_detalhes_servico(nome_servico)
                        executar("INSERT INTO agendamento_servicos (empresa_id, agendamento_id, servico, valor, duracao) VALUES (?, ?, ?, ?, ?)", (precisa_empresa_id(), int(ag_id), det["nome"], det["valor"], det["duracao"]))
                    st.success("Agendamento atualizado com sucesso!")
            with b2:
                if st.button("Finalizar atendimento"):
                    executar("UPDATE agendamentos SET status = ?, forma_pagamento = ?, conta_financeira = ?, valor_total = ? WHERE id = ?", ("Concluído", nova_fp, nova_conta, float(total_edit), int(ag_id)))
                    if nova_conta != "Sem conta cadastrada":
                        ja_lancado = consultar_df("SELECT * FROM movimentacoes_financeiras WHERE empresa_id = ? AND agendamento_id = ? AND tipo = 'Entrada'", (precisa_empresa_id(), int(ag_id)))
                        if ja_lancado.empty:
                            registrar_movimentacao_financeira(nova_data, "Entrada", "Recebimento de serviço", f"Atendimento - {novo_cliente}", total_edit, nova_fp, nova_conta, "Agendamento", int(ag_id))
                    st.success("Atendimento finalizado com sucesso!")
            with b3:
                if st.button("Cancelar atendimento"):
                    executar("UPDATE agendamentos SET status = ? WHERE id = ?", ("Cancelado", int(ag_id)))
                    st.success("Atendimento cancelado com sucesso!")
    with aba3:
        cond, params = filtro_empresa_master_ou_usuario()
        df_ag_exc = consultar_df(f"SELECT * FROM agendamentos WHERE {cond} ORDER BY data, hora", params)
        if df_ag_exc.empty:
            st.info("Nenhum agendamento para excluir.")
        else:
            st.dataframe(df_ag_exc, use_container_width=True, hide_index=True)
            ag_exc = st.selectbox("Selecione o ID do agendamento para excluir", df_ag_exc["id"].tolist(), key="ag_exc")
            if st.button("Excluir agendamento"):
                executar("DELETE FROM movimentacoes_financeiras WHERE agendamento_id = ?", (int(ag_exc),))
                executar("DELETE FROM agendamento_servicos WHERE agendamento_id = ?", (int(ag_exc),))
                executar("DELETE FROM agendamentos WHERE id = ?", (int(ag_exc),))
                st.success("Agendamento excluído com sucesso!")

# ==============================
# FINANCEIRO
# ==============================
if menu == "💰 Financeiro":
    topo("Financeiro", "Contas, lançamentos e extratos filtrados por empresa.")
    aba1, aba2, aba3 = st.tabs(["Contas financeiras", "Lançamentos", "Extrato / Saldos"])
    with aba1:
        c1, c2, c3 = st.columns(3)
        with c1: nome = st.text_input("Nome da conta", key="fin_nome")
        with c2: tipo = st.selectbox("Tipo", ["Banco", "Caixa"], key="fin_tipo")
        with c3: saldo_inicial = st.number_input("Saldo inicial", min_value=0.0, step=1.0, key="fin_saldo")
        observacao = st.text_area("Observação", key="fin_obs")
        if st.button("Salvar conta financeira"):
            if nome.strip():
                executar("INSERT INTO contas_financeiras (empresa_id, nome, tipo, saldo_inicial, observacao) VALUES (?, ?, ?, ?, ?)", (precisa_empresa_id(), nome.strip(), tipo, float(saldo_inicial), observacao.strip()))
                st.success("Conta financeira cadastrada com sucesso!")
            else:
                st.warning("Informe o nome da conta.")
        cond, params = filtro_empresa_master_ou_usuario()
        df_contas = consultar_df(f"SELECT * FROM contas_financeiras WHERE {cond} ORDER BY nome", params)
        if not df_contas.empty:
            df_contas["saldo_atual"] = df_contas["nome"].apply(obter_saldo_conta)
            st.dataframe(df_contas, use_container_width=True, hide_index=True)
    with aba2:
        cond, params = filtro_empresa_master_ou_usuario()
        df_contas = consultar_df(f"SELECT nome FROM contas_financeiras WHERE {cond} ORDER BY nome", params)
        contas = df_contas["nome"].tolist() if not df_contas.empty else []
        if not contas:
            st.warning("Cadastre um banco ou caixa antes de lançar movimentações.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1: data = st.date_input("Data do lançamento", key="mov_data")
            with c2: tipo = st.selectbox("Tipo de movimentação", ["Entrada", "Saída"], key="mov_tipo")
            with c3: valor = st.number_input("Valor", min_value=0.0, step=1.0, key="mov_valor")
            categoria = st.text_input("Categoria", key="mov_cat")
            descricao = st.text_input("Descrição", key="mov_desc")
            c4, c5 = st.columns(2)
            with c4: forma_pagamento = st.selectbox("Forma de pagamento", ["Dinheiro", "PIX", "Cartão de Débito", "Cartão de Crédito", "Transferência", "Boleto", "Outro"], key="mov_fp")
            with c5: conta = st.selectbox("Banco / Caixa", contas, key="mov_conta")
            if st.button("Salvar lançamento financeiro"):
                registrar_movimentacao_financeira(data, tipo, categoria.strip() if categoria.strip() else "Sem categoria", descricao.strip(), valor, forma_pagamento, conta, "Manual")
                st.success("Lançamento financeiro salvo com sucesso!")
    with aba3:
        cond, params = filtro_empresa_master_ou_usuario()
        df_mov = consultar_df(f"SELECT * FROM movimentacoes_financeiras WHERE {cond} ORDER BY data DESC, id DESC", params)
        if df_mov.empty:
            st.info("Nenhuma movimentação financeira encontrada.")
        else:
            st.dataframe(df_mov, use_container_width=True, hide_index=True)
        df_contas = consultar_df(f"SELECT * FROM contas_financeiras WHERE {cond} ORDER BY nome", params)
        if not df_contas.empty:
            resumo = []
            for _, linha in df_contas.iterrows():
                resumo.append({"Conta": linha["nome"], "Tipo": linha["tipo"], "Saldo inicial": linha["saldo_inicial"], "Saldo atual": obter_saldo_conta(linha["nome"])})
            st.dataframe(pd.DataFrame(resumo), use_container_width=True, hide_index=True)

# ==============================
# PRODUTOS E ESTOQUE
# ==============================
if menu == "📦 Produtos e Estoque":
    topo("Produtos e estoque", "Mercadorias, insumos, saídas e importação XML em uma interface premium por empresa.")
    aba1, aba2, aba3, aba4 = st.tabs(["Cadastro de itens", "Entrada / Saída", "Importar XML", "Posição de estoque"])
    with aba1:
        c1, c2, c3, c4 = st.columns(4)
        with c1: nome = st.text_input("Nome do item", key="prod_nome")
        with c2: tipo = st.selectbox("Tipo do item", ["Mercadoria", "Produto para revenda", "Insumo de serviço"], key="prod_tipo")
        with c3: unidade = st.text_input("Unidade", key="prod_unid", placeholder="Ex: un, kg, ml, caixa")
        with c4: estoque_atual = st.number_input("Estoque inicial", min_value=0.0, step=1.0, key="prod_est")
        c5, c6, c7 = st.columns(3)
        with c5: estoque_minimo = st.number_input("Estoque mínimo", min_value=0.0, step=1.0, key="prod_min")
        with c6: custo_unitario = st.number_input("Custo unitário", min_value=0.0, step=1.0, key="prod_custo")
        with c7: preco_venda = st.number_input("Preço de venda", min_value=0.0, step=1.0, key="prod_preco")
        observacao = st.text_area("Observação", key="prod_obs")
        if st.button("Salvar item"):
            if nome.strip():
                executar("INSERT INTO produtos (empresa_id, nome, tipo, unidade, estoque_atual, estoque_minimo, custo_unitario, preco_venda, observacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (precisa_empresa_id(), nome.strip(), tipo, unidade.strip(), float(estoque_atual), float(estoque_minimo), float(custo_unitario), float(preco_venda), observacao.strip()))
                st.success("Item cadastrado com sucesso!")
            else:
                st.warning("Informe o nome do item.")
        cond, params = filtro_empresa_master_ou_usuario()
        df_prod = consultar_df(f"SELECT * FROM produtos WHERE {cond} ORDER BY nome", params)
        if not df_prod.empty:
            st.dataframe(df_prod, use_container_width=True, hide_index=True)
    with aba2:
        cond, params = filtro_empresa_master_ou_usuario()
        df_prod = consultar_df(f"SELECT id, nome, custo_unitario FROM produtos WHERE {cond} ORDER BY nome", params)
        if df_prod.empty:
            st.warning("Cadastre um item antes de movimentar o estoque.")
        else:
            produto_id = st.selectbox("Produto", df_prod["id"].tolist(), key="estoque_prod")
            dados_prod = consultar_df("SELECT * FROM produtos WHERE id = ?", (int(produto_id),)).iloc[0]
            st.markdown(f"<div class='glass-card'><b>Item selecionado:</b> {dados_prod['nome']} &nbsp;&nbsp; <b>Estoque atual:</b> {dados_prod['estoque_atual']}</div>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: data = st.date_input("Data da movimentação", key="est_data")
            with c2: tipo_mov = st.selectbox("Tipo de movimentação", ["Entrada mercadoria", "Saída mercadoria", "Saída serviço"], key="est_tipo")
            with c3: quantidade = st.number_input("Quantidade", min_value=0.0, step=1.0, key="est_qtd")
            c4, c5 = st.columns(2)
            with c4: valor_unitario = st.number_input("Valor unitário", min_value=0.0, step=1.0, value=float(dados_prod["custo_unitario"] if dados_prod["custo_unitario"] else 0), key="est_valor")
            with c5: origem = st.text_input("Origem", key="est_origem", placeholder="Ex: Compra fornecedor, Venda balcão, Uso em serviço")
            observacao = st.text_area("Observação", key="est_obs")
            if st.button("Salvar movimentação de estoque"):
                if tipo_mov in ["Saída mercadoria", "Saída serviço"] and float(quantidade) > float(dados_prod["estoque_atual"]):
                    st.error("Quantidade maior que o estoque atual.")
                else:
                    registrar_movimentacao_estoque(data, int(produto_id), dados_prod["nome"], tipo_mov, quantidade, valor_unitario, origem.strip(), observacao.strip())
                    st.success("Movimentação de estoque salva com sucesso!")
        df_hist = consultar_df(f"SELECT * FROM estoque_movimentacoes WHERE {cond} ORDER BY data DESC, id DESC", params)
        if not df_hist.empty:
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
    with aba3:
        st.markdown("<div class='glass-card'>Importe o XML para cadastrar produtos automaticamente e lançar a entrada de mercadorias no estoque.</div>", unsafe_allow_html=True)
        arquivo_xml = st.file_uploader("Selecione o arquivo XML da NF-e", type=["xml"], key="xml_nfe")
        if arquivo_xml is not None:
            try:
                dados_xml = importar_xml_nfe_bytes(arquivo_xml.getvalue())
                st.success("XML lido com sucesso!")
                st.markdown(f"<div class='glass-card'><b>Emitente:</b> {dados_xml['emitente'] or 'Não identificado'}<br><b>Número da nota:</b> {dados_xml['numero_nota'] or 'Não identificado'}<br><b>Data de emissão:</b> {dados_xml['data_emissao']}</div>", unsafe_allow_html=True)
                if dados_xml["itens"]:
                    df_preview = pd.DataFrame(dados_xml["itens"])
                    df_preview["total"] = df_preview["quantidade"] * df_preview["valor_unitario"]
                    st.dataframe(df_preview, use_container_width=True, hide_index=True)
                    origem_texto = f"XML NF-e {dados_xml['numero_nota']} - {dados_xml['emitente']}"
                    if st.button("Confirmar importação do XML"):
                        df_importado = processar_importacao_xml(dados_xml, origem_texto)
                        st.success("Importação concluída com sucesso!")
                        st.dataframe(df_importado, use_container_width=True, hide_index=True)
                        st.write(f"**Total importado:** {moeda_br(df_importado['Total'].sum())}")
                else:
                    st.warning("Nenhum item de produto foi encontrado no XML.")
            except Exception as e:
                st.error(f"Não foi possível importar este XML. Detalhe: {e}")
    with aba4:
        cond, params = filtro_empresa_master_ou_usuario()
        df_pos = consultar_df(f"SELECT * FROM produtos WHERE {cond} ORDER BY nome", params)
        if df_pos.empty:
            st.info("Nenhum item cadastrado.")
        else:
            df_pos["Abaixo do mínimo"] = df_pos.apply(lambda x: "Sim" if float(x["estoque_atual"]) <= float(x["estoque_minimo"]) else "Não", axis=1)
            st.dataframe(df_pos, use_container_width=True, hide_index=True)
