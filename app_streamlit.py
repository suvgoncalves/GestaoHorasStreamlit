import streamlit as st
import pandas as pd
import pyodbc
from datetime import datetime, date, time, timedelta
import calendar
from decimal import Decimal # Importar Decimal para verificação de tipo
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from io import BytesIO # Para lidar com o PDF em memória

# --- Configurações da Página ---
st.set_page_config(
    page_title="Sistema de Gestão de Horas",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Personalizado ---
st.markdown("""
<style>
    /* Variáveis de cor */
    :root {
        --primary-color: #88A0B2; /* Azul acinzentado suave */
        --secondary-color: #C3D9E8; /* Azul muito claro */
        --accent-color: #5A7C93; /* Azul mais escuro para acentuação */
        --text-color: #333333; /* Cinza escuro para texto */
        --background-color: #F0F2F6; /* Cinza claro para fundo */
        --card-background: #FFFFFF; /* Branco para cartões/elements */
        --neutral-border: #E0E0E0; /* Cinza claro para bordas */
        --shadow: 0 4px 8px rgba(0, 0, 0, 0.08); /* Sombra suave */
        --border-radius: 8px; /* Raio da borda padrão */
    }

    /* Estilo geral da página */
    body {
        font-family: 'Segoe UI', sans-serif;
        color: var(--text-color);
        background-color: var(--background-color);
    }

    /* Sidebar */
    .stSidebar {
        background-color: var(--card-background);
        padding-top: 20px;
        box-shadow: 2px 0 5px rgba(0,0,0,0.1);
    }
    .stSidebar .stButton > button {
        width: 100%;
        margin-bottom: 10px;
        background-color: var(--secondary-color);
        color: var(--text-color);
        border: none;
        border-radius: var(--border-radius);
        padding: 10px;
        transition: all 0.2s ease;
    }
    .stSidebar .stButton > button:hover {
        background-color: var(--primary-color);
        color: white;
    }
    .stSidebar .stButton > button:active {
        background-color: var(--accent-color);
    }

    /* Títulos */
    h1, h2, h3, h4, h5, h6 {
        color: var(--accent-color);
        font-weight: 600;
        margin-top: 0.8em;
        margin-bottom: 0.5em;
    }

    /* Métricas */
    [data-testid="stMetric"] {
        background-color: var(--card-background);
        border: 1px solid var(--neutral-border);
        border-radius: var(--border-radius);
        padding: 20px;
        box-shadow: var(--shadow);
        text-align: center;
        margin-bottom: 20px;
        transition: all 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    [data-testid="stMetric"] > div > div:first-child { /* Label */
        font-size: 1.1em;
        color: var(--text-color);
        font-weight: 500;
    }
    [data-testid="stMetric"] > div > div:nth-child(2) > div { /* Value */
        font-size: 2em;
        font-weight: 700;
        color: var(--primary-color);
        margin-top: 10px;
    }

    /* Expander */
    .stExpander {
        background-color: var(--card-background);
        border: 1px solid var(--neutral-border);
        border-radius: var(--border-radius);
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: var(--shadow);
        transition: all 0.2s ease;
    }
    .stExpander > div > div > p { /* Título do expander */
        font-weight: 600;
        color: var(--primary-color);
    }
    .stExpander:hover {
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: var(--border-radius);
        overflow: hidden; /* Garante que as bordas da tabela sejam arredondadas */
        box-shadow: var(--shadow);
        border: 1px solid var(--neutral-border);
    }
    /* Estilo para cabeçalhos de tabela */
    .stDataFrame thead th {
        background-color: var(--primary-color) !important;
        color: white !important;
        font-weight: 600 !important;
    }

    /* Linhas horizontais */
    hr {
        border-top: 1px solid var(--neutral-border);
        margin-top: 30px;
        margin-bottom: 30px;
    }

    /* Campos de input (text_input, number_input, date_input, selectbox) */
    .stTextInput > label, .stNumberInput > label, .stDateInput > label, .stSelectbox > label, .stTimeInput > label {
        font-weight: 500;
        color: var(--text-color);
    }
    .stTextInput > div > input, .stNumberInput > div > input, .stDateInput > div > div > input, .stSelectbox > div > div, .stTimeInput > div > input {
        border: 1px solid var(--neutral-border);
        border-radius: var(--border-radius);
        padding: 8px 12px;
        color: var(--text-color);
        background-color: var(--card-background);
    }
    .stTextInput > div > input:focus, .stNumberInput > div > input:focus, .stDateInput > div > div > input:focus, .stSelectbox > div > div:focus-within, .stTimeInput > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 1px var(--primary-color);
        outline: none;
    }

    /* Botões */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.2s ease;
        margin-top: 10px; /* Adiciona margem acima dos botões */
    }
    .stButton > button:hover {
        background-color: var(--accent-color);
        transform: translateY(-1px);
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    .stButton > button:active {
        background-color: var(--accent-color);
        transform: translateY(0);
        box-shadow: none;
    }

    /* Mensagens de sucesso/erro/aviso */
    .stAlert {
        border-radius: var(--border-radius);
    }
    .stAlert.success {
        background-color: #e6ffe6; /* Verde claro */
        color: #006600; /* Verde escuro */
        border-left: 5px solid #00cc00;
    }
    .stAlert.error {
        background-color: #ffe6e6; /* Vermelho claro */
        color: #cc0000; /* Vermelho escuro */
        border-left: 5px solid #ff0000;
    }
    .stAlert.info {
        background-color: #e6f7ff; /* Azul claro */
        color: #004d99; /* Azul escuro */
        border-left: 5px solid #0099ff;
    }
    .stAlert.warning {
        background-color: #fffbe6; /* Amarelo claro */
        color: #996600; /* Amarelo escuro */
        border-left: 5px solid #ffcc00;
    }

</style>
""", unsafe_allow_html=True)


# --- Configurações da Base de Dados ---
# Utilizando Streamlit Secrets para gerir as credenciais da base de dados Azure SQL
DB_DRIVER = st.secrets["connections.sql_server"]["driver"]
DB_SERVER = st.secrets["connections.sql_server"]["server"]
DB_DATABASE = st.secrets["connections.sql_server"]["database"]
DB_UID = st.secrets["connections.sql_server"]["uid"]
DB_PWD = st.secrets["connections.sql_server"]["pwd"]

# --- Funções de Conexão à Base de Dados ---
@st.cache_resource
def get_db_connection():
    """
    Estabelece e cacheia a conexão com a base de dados Azure SQL.
    Esta função inclui mensagens de erro detalhadas para ajudar na depuração.
    """
    try:
        conn = pyodbc.connect(
            f'DRIVER={DB_DRIVER};'
            f'SERVER={DB_SERVER};'
            f'DATABASE={DB_DATABASE};'
            f'UID={DB_UID};'
            f'PWD={DB_PWD};'
            f'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;' # Parâmetros para conexão segura com Azure SQL
        )
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        st.error(f"Erro de Conexão à Base de Dados Azure SQL (SQLSTATE: {sqlstate}): {ex}")
        st.info("Por favor, verifique as credenciais da base de dados e as regras de firewall no Portal Azure.")
        return None

# Função genérica para executar queries de escrita (INSERT, UPDATE, DELETE)
def execute_query(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params if params else ())
            conn.commit()
            return True
        except pyodbc.Error as ex:
            st.error(f"Erro ao executar query: {ex}")
            conn.rollback() # Reverte a transação em caso de erro
            return False
    return False

# Função genérica para ler dados
@st.cache_data(ttl=60) # Cache os dados por 60 segundos para melhorar a performance
def fetch_data(query, params=None):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params if params else ())
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            df = pd.DataFrame.from_records(rows, columns=columns)

            # Converter colunas que podem conter Decimal para float
            for col in df.columns:
                # Heurística: se a coluna for do tipo 'object' e tiver pelo menos um valor Decimal, converta.
                # Ou se a coluna já tiver um tipo numérico mas não for float, tente converter para float.
                if not df[col].empty:
                    if isinstance(df[col].iloc[0], Decimal):
                        df[col] = df[col].astype(float)
                    elif pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_float_dtype(df[col]):
                        try:
                            df[col] = df[col].astype(float)
                        except Exception:
                            pass # Ignorar se não for possível converter (e.g., inteiros grandes)

            return df
        except pyodbc.Error as ex:
            st.error(f"Erro ao buscar dados: {ex}")
            return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro
    return pd.DataFrame()

# --- Funções Específicas de CRUD para as Tabelas ---

# Funcionários (ATUALIZADO: Adicionado Departamento e DiasFeriasAnuais)
def get_funcionarios():
    return fetch_data("SELECT FuncionarioID, NomeCompleto, NumeroFuncionario, DataNascimento, NIF, NISS, Telefone, Email, CategoriaProfissional, Departamento, SalarioBaseMensal, ValorSubsidioAlimentacaoDiario, TaxaIRS, TaxaSegurancaSocialFuncionario, HorasTrabalhoMensalPadrao, TaxaHoraExtra50, TaxaHoraExtra100, DiasFeriasAnuais FROM dbo.Funcionarios")

def add_funcionario(data):
    query = """
    INSERT INTO dbo.Funcionarios (NomeCompleto, NumeroFuncionario, DataNascimento, NIF, NISS, Telefone, Email, CategoriaProfissional, Departamento,
                                  SalarioBaseMensal, ValorSubsidioAlimentacaoDiario, TaxaIRS, TaxaSegurancaSocialFuncionario,
                                  HorasTrabalhoMensalPadrao, TaxaHoraExtra50, TaxaHoraExtra100, DiasFeriasAnuais)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        data['NomeCompleto'], data['NumeroFuncionario'], data['DataNascimento'], data['NIF'], data['NISS'],
        data['Telefone'], data['Email'], data['CategoriaProfissional'], data['Departamento'], data['SalarioBaseMensal'],
        data['ValorSubsidioAlimentacaoDiario'], data['TaxaIRS'],
        data['TaxaSegurancaSocialFuncionario'], data['HorasTrabalhoMensalPadrao'],
        data['TaxaHoraExtra50'], data['TaxaHoraExtra100'], data['DiasFeriasAnuais']
    )
    return execute_query(query, params)

def update_funcionario(funcionario_id, data):
    query = """
    UPDATE dbo.Funcionarios
    SET NomeCompleto=?, NumeroFuncionario=?, DataNascimento=?, NIF=?, NISS=?, Telefone=?, Email=?, CategoriaProfissional=?, Departamento=?,
        SalarioBaseMensal=?, ValorSubsidioAlimentacaoDiario=?, TaxaIRS=?, TaxaSegurancaSocialFuncionario=?,
        HorasTrabalhoMensalPadrao=?, TaxaHoraExtra50=?, TaxaHoraExtra100=?, DiasFeriasAnuais=?
    WHERE FuncionarioID=?
    """
    params = (
        data['NomeCompleto'], data['NumeroFuncionario'], data['DataNascimento'], data['NIF'], data['NISS'],
        data['Telefone'], data['Email'], data['CategoriaProfissional'], data['Departamento'], data['SalarioBaseMensal'],
        data['ValorSubsidioAlimentacaoDiario'], data['TaxaIRS'],
        data['TaxaSegurancaSocialFuncionario'], data['HorasTrabalhoMensalPadrao'],
        data['TaxaHoraExtra50'], data['TaxaHoraExtra100'], data['DiasFeriasAnuais'], funcionario_id
    )
    return execute_query(query, params)

def delete_funcionario(funcionario_id):
    queries = [
        "DELETE FROM dbo.RegistosDiarios WHERE FuncionarioID=?",
        "DELETE FROM dbo.Ferias WHERE FuncionarioID=?",
        "DELETE FROM dbo.Faltas WHERE FuncionarioID=?",
        "DELETE FROM dbo.Licencas WHERE FuncionarioID=?",
        "DELETE FROM dbo.AcertosSemestrais WHERE FuncionarioID=?",
        "DELETE FROM dbo.Funcionarios WHERE FuncionarioID=?"
    ]
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            for query in queries:
                cursor.execute(query, (funcionario_id,))
            conn.commit()
            return True
        except pyodbc.Error as ex:
            st.error(f"Erro ao apagar funcionário e dados relacionados: {ex}")
            conn.rollback()
            return False
    return False

# Registos Diários
def get_registos_diarios():
    return fetch_data("SELECT * FROM dbo.RegistosDiarios")

def add_registo_diario(data):
    query = """
    INSERT INTO dbo.RegistosDiarios (FuncionarioID, DataRegisto, TipoOcorrenciaID, HorasTrabalhadas, HorasExtraDiarias, HorasAusencia, Observacoes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        data['FuncionarioID'], data['DataRegisto'], data['TipoOcorrenciaID'],
        data['HorasTrabalhadas'], data['HorasExtraDiarias'], data['HorasAusencia'], data['Observacoes']
    )
    return execute_query(query, params)

def update_registo_diario(registo_id, data):
    query = """
    UPDATE dbo.RegistosDiarios
    SET FuncionarioID=?, DataRegisto=?, TipoOcorrenciaID=?, HorasTrabalhadas=?, HorasExtraDiarias=?, HorasAusencia=?, Observacoes=?
    WHERE RegistoID=?
    """
    params = (
        data['FuncionarioID'], data['DataRegisto'], data['TipoOcorrenciaID'],
        data['HorasTrabalhadas'], data['HorasExtraDiarias'], data['HorasAusencia'], data['Observacoes'], registo_id
    )
    return execute_query(query, params)

def delete_registo_diario(registo_id):
    query = "DELETE FROM dbo.RegistosDiarios WHERE RegistoID=?"
    return execute_query(query, (registo_id,))

# Férias (ATUALIZADO: Com campo Aprovado)
def get_ferias():
    return fetch_data("SELECT * FROM dbo.Ferias")

def add_ferias(data):
    query = "INSERT INTO dbo.Ferias (FuncionarioID, DataInicio, DataFim, Observacoes, Aprovado) VALUES (?, ?, ?, ?, ?)"
    params = (data['FuncionarioID'], data['DataInicio'], data['DataFim'], data['Observacoes'], data['Aprovado'])
    return execute_query(query, params)

def update_ferias(ferias_id, data):
    query = "UPDATE dbo.Ferias SET FuncionarioID=?, DataInicio=?, DataFim=?, Observacoes=?, Aprovado=? WHERE FeriasID=?"
    params = (data['FuncionarioID'], data['DataInicio'], data['DataFim'], data['Observacoes'], data['Aprovado'], ferias_id)
    return execute_query(query, params)

def delete_ferias(ferias_id):
    query = "DELETE FROM dbo.Ferias WHERE FeriasID=?"
    return execute_query(query, (ferias_id,))

# Faltas (ATUALIZADO: Com campo Aprovado)
def get_faltas():
    return fetch_data("SELECT * FROM dbo.Faltas")

def add_falta(data):
    query = "INSERT INTO dbo.Faltas (FuncionarioID, DataFalta, Motivo, Justificada, HorasAusenciaFalta, Aprovado) VALUES (?, ?, ?, ?, ?, ?)"
    params = (data['FuncionarioID'], data['DataFalta'], data['Motivo'], data['Justificada'], data['HorasAusenciaFalta'], data['Aprovado'])
    return execute_query(query, params)

def update_falta(falta_id, data):
    query = "UPDATE dbo.Faltas SET FuncionarioID=?, DataFalta=?, Motivo=?, Justificada=?, HorasAusenciaFalta=?, Aprovado=? WHERE FaltaID=?"
    params = (data['FuncionarioID'], data['DataFalta'], data['Motivo'], data['Justificada'], data['HorasAusenciaFalta'], data['Aprovado'], falta_id)
    return execute_query(query, params)

def delete_falta(falta_id):
    query = "DELETE FROM dbo.Faltas WHERE FaltaID=?"
    return execute_query(query, (falta_id,))

# Licenças (ATUALIZADO: Com campo Aprovado)
def get_licencas():
    return fetch_data("SELECT * FROM dbo.Licencas")

def add_licenca(data):
    query = "INSERT INTO dbo.Licencas (FuncionarioID, DataInicio, DataFim, Motivo, Observacoes, Aprovado) VALUES (?, ?, ?, ?, ?, ?)"
    params = (data['FuncionarioID'], data['DataInicio'], data['DataFim'], data['Motivo'], data['Observacoes'], data['Aprovado'])
    return execute_query(query, params)

def update_licenca(licenca_id, data):
    query = "UPDATE dbo.Licencas SET FuncionarioID=?, DataInicio=?, DataFim=?, Motivo=?, Observacoes=?, Aprovado=? WHERE LicencaID=?"
    params = (data['FuncionarioID'], data['DataInicio'], data['DataFim'], data['Motivo'], data['Observacoes'], data['Aprovado'], licenca_id)
    return execute_query(query, params)

def delete_licenca(licenca_id):
    query = "DELETE FROM dbo.Licencas WHERE LicencaID=?"
    return execute_query(query, (licenca_id,))

# Tipos de Ocorrência (NOVO CRUD)
def get_tipos_ocorrencia():
    return fetch_data("SELECT TipoID, Codigo, Descricao, HorasPadrao, EhTurno, EhHorasExtra, EhAusencia, EhFOTS, EhFolgaCompensatoria, Sigla FROM dbo.TiposOcorrencia")

def add_tipo_ocorrencia(data):
    query = """
    INSERT INTO dbo.TiposOcorrencia (Codigo, Descricao, HorasPadrao, EhTurno, EhHorasExtra, EhAusencia, EhFOTS, EhFolgaCompensatoria, Sigla)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (data['Codigo'], data['Descricao'], data['HorasPadrao'], data['EhTurno'], data['EhHorasExtra'],
              data['EhAusencia'], data['EhFOTS'], data['EhFolgaCompensatoria'], data['Sigla'])
    return execute_query(query, params)

def update_tipo_ocorrencia(tipo_id, data):
    query = """
    UPDATE dbo.TiposOcorrencia
    SET Codigo=?, Descricao=?, HorasPadrao=?, EhTurno=?, EhHorasExtra=?, EhAusencia=?, EhFOTS=?, EhFolgaCompensatoria=?, Sigla=?
    WHERE TipoID=?
    """
    params = (data['Codigo'], data['Descricao'], data['HorasPadrao'], data['EhTurno'], data['EhHorasExtra'],
              data['EhAusencia'], data['EhFOTS'], data['EhFolgaCompensatoria'], data['Sigla'], tipo_id)
    return execute_query(query, params)

def delete_tipo_ocorrencia(tipo_id):
    query = "DELETE FROM dbo.TiposOcorrencia WHERE TipoID=?"
    return execute_query(query, (tipo_id,))


# Função auxiliar para obter a sigla do tipo de ocorrência
def get_sigla_by_tipo_id(tipo_id, tipos_ocorrencia_df_global):
    """Retorna a sigla de um TipoOcorrenciaID usando o DataFrame global."""
    # Corrigido para usar 'TipoOcorrenciaID' que é o nome da coluna após o rename
    if not tipos_ocorrencia_df_global.empty and 'TipoOcorrenciaID' in tipos_ocorrencia_df_global.columns and tipo_id in tipos_ocorrencia_df_global['TipoOcorrenciaID'].values:
        return tipos_ocorrencia_df_global[tipos_ocorrencia_df_global['TipoOcorrenciaID'] == tipo_id]['Sigla'].iloc[0]
    return '-' # Sigla padrão para não encontrado ou sem ocorrência


# Acertos Semestrais
def get_acertos_semestrais():
    return fetch_data("SELECT * FROM dbo.AcertosSemestrais")

def add_acerto_semestral(data):
    query = """
    INSERT INTO dbo.AcertosSemestrais (FuncionarioID, Ano, Semestre, TotalHorasNormais,
                                       TotalHorasExtraAcumuladas, TotalFOTSDisponiveis)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    params = (
        data['FuncionarioID'], data['Ano'], data['Semestre'], data['TotalHorasNormais'],
        data['TotalHorasExtraAcumuladas'], data['TotalFOTSDisponiveis']
    )
    return execute_query(query, params)

def update_acerto_semestral(acerto_id, data):
    query = """
    UPDATE dbo.AcertosSemestrais
    SET FuncionarioID=?, Ano=?, Semestre=?, TotalHorasNormais=?,
        TotalHorasExtraAcumuladas=?, TotalFOTSDisponiveis=?
    WHERE AcertoID=?
    """
    params = (
        data['FuncionarioID'], data['Ano'], data['Semestre'], data['TotalHorasNormais'],
        data['TotalHorasExtraAcumuladas'], data['TotalFOTSDisponiveis'], acerto_id
    )
    return execute_query(query, params)

def delete_acerto_semestral(acerto_id):
    query = "DELETE FROM dbo.AcertosSemestrais WHERE AcertoID=?"
    return execute_query(query, (acerto_id,))


# Função para obter todos os eventos (registos diários, faltas, férias, licenças) para um funcionário num período
def get_all_events_for_employee_and_period(funcionario_id, start_date, end_date):
    registos_diarios_df = fetch_data(
        "SELECT * FROM dbo.RegistosDiarios WHERE FuncionarioID = ? AND DataRegisto BETWEEN ? AND ?",
        (funcionario_id, start_date, end_date)
    )
    faltas_df = fetch_data(
        "SELECT * FROM dbo.Faltas WHERE FuncionarioID = ? AND DataFalta BETWEEN ? AND ?",
        (funcionario_id, start_date, end_date)
    )
    ferias_df = fetch_data(
        "SELECT * FROM dbo.Ferias WHERE FuncionarioID = ? AND DataInicio <= ? AND DataFim >= ?",
        (funcionario_id, end_date, start_date)
    )
    licencas_df = fetch_data(
        "SELECT * FROM dbo.Licencas WHERE FuncionarioID = ? AND DataInicio <= ? AND DataFim >= ?",
        (funcionario_id, end_date, start_date)
    )
    return registos_diarios_df, faltas_df, ferias_df, licencas_df

# Função para exportar DataFrame para CSV
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para exportar DataFrame para Excel (usando BytesIO)
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close() # Use writer.close() instead of writer.save() for newer pandas/xlsxwriter
    processed_data = output.getvalue()
    return processed_data

# --- Função para Gerar PDF do Recibo de Vencimento (Layout Sofisticado e Otimizado) ---
def generate_payslip_pdf(funcionario_info, mes_recibo, ano_recibo,
                          total_horas_trabalhadas_mes, total_horas_extra_mes,
                          salario_base_mensal, valor_horas_extra,
                          subsidio_alimentacao, vencimento_bruto,
                          desconto_irs, taxa_irs, desconto_ss, taxa_seguranca_social_funcionario,
                          total_horas_ausencia_geral, desconto_ausencia, salario_liquido,
                          dias_ferias_mes, dias_licencas_mes):

    buffer = BytesIO()
    # Margens menores para maximizar o espaço na página
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.0*cm, leftMargin=1.0*cm, topMargin=1.0*cm, bottomMargin=1.0*cm) # Margens ainda menores
    styles = getSampleStyleSheet()

    # --- Estilos Aprimorados para um Layout Mais Sofisticado e Otimizado ---
    # Tamanhos de fonte e espaçamentos ajustados para caber numa página
    styles.add(ParagraphStyle(name='HeaderTitle', fontSize=20, leading=24, alignment=TA_CENTER, fontName='Helvetica-Bold', textColor=colors.HexColor('#5A7C93'))) # Tamanho reduzido
    styles.add(ParagraphStyle(name='HeaderSubtitle', fontSize=11, leading=13, alignment=TA_CENTER, fontName='Helvetica-Bold', textColor=colors.HexColor('#88A0B2'), spaceAfter=0.3*cm)) # Tamanho reduzido
    styles.add(ParagraphStyle(name='CompanyInfo', fontSize=6, leading=8, alignment=TA_CENTER, fontName='Helvetica', textColor=colors.HexColor('#666666'))) # Tamanho reduzido

    styles.add(ParagraphStyle(name='SectionHeading', fontSize=10, leading=13, alignment=TA_LEFT, fontName='Helvetica-Bold', textColor=colors.HexColor('#5A7C93'), spaceBefore=0.6*cm, spaceAfter=0.2*cm)) # Tamanho e espaço reduzidos
    styles.add(ParagraphStyle(name='EmployeeDetail', fontSize=7, leading=9, alignment=TA_LEFT, fontName='Helvetica', textColor=colors.HexColor('#333333'))) # Tamanho reduzido
    styles.add(ParagraphStyle(name='EmployeeDetailBold', fontSize=7, leading=9, alignment=TA_LEFT, fontName='Helvetica-Bold', textColor=colors.HexColor('#333333'))) # Tamanho reduzido

    styles.add(ParagraphStyle(name='TableCaption', fontSize=8, leading=10, alignment=TA_LEFT, fontName='Helvetica-Bold', textColor=colors.HexColor('#5A7C93'), spaceBefore=0.3*cm, spaceAfter=0.1*cm)) # Tamanho e espaço reduzidos
    styles.add(ParagraphStyle(name='TableColHeader', fontSize=8, leading=10, alignment=TA_CENTER, fontName='Helvetica-Bold', textColor=colors.HexColor('#333333'))) # Tamanho reduzido
    styles.add(ParagraphStyle(name='TableTextLeft', fontSize=7, leading=9, alignment=TA_LEFT, fontName='Helvetica', textColor=colors.HexColor('#333333'))) # Tamanho reduzido
    styles.add(ParagraphStyle(name='TableTextRight', fontSize=7, leading=9, alignment=TA_RIGHT, fontName='Helvetica', textColor=colors.HexColor('#333333'))) # Tamanho reduzido
    styles.add(ParagraphStyle(name='TableTotalText', fontSize=8, leading=10, alignment=TA_RIGHT, fontName='Helvetica-Bold', textColor=colors.HexColor('#5A7C93'))) # Tamanho reduzido
    styles.add(ParagraphStyle(name='TableTotalValue', fontSize=8, leading=10, alignment=TA_RIGHT, fontName='Helvetica-Bold', textColor=colors.HexColor('#333333'))) # Tamanho reduzido

    styles.add(ParagraphStyle(name='FinalTotalLabel', fontSize=13, leading=15, alignment=TA_RIGHT, fontName='Helvetica-Bold', textColor=colors.HexColor('#5A7C93'), spaceBefore=0.6*cm)) # Tamanho e espaço reduzidos
    styles.add(ParagraphStyle(name='FinalTotalValue', fontSize=15, leading=17, alignment=TA_RIGHT, fontName='Helvetica-Bold', textColor=colors.HexColor('#006600'))) # Tamanho reduzido

    styles.add(ParagraphStyle(name='FooterText', fontSize=5, leading=7, alignment=TA_CENTER, fontName='Helvetica', textColor=colors.HexColor('#888888'), spaceBefore=0.7*cm)) # Tamanho e espaço reduzidos

    story = []

    # --- Cabeçalho da Empresa (Fictício e Otimizado) ---
    story.append(Paragraph("NOME DA EMPRESA", styles['HeaderTitle']))
    story.append(Paragraph("Rua Fictícia, 123, 4700-000 Braga - Portugal", styles['CompanyInfo']))
    story.append(Paragraph("NIF: 987654321", styles['CompanyInfo'])) # NIF fictício
    story.append(Spacer(1, 0.2*cm)) # Espaço reduzido
    story.append(Paragraph(f"RECIBO DE VENCIMENTO - {calendar.month_name[mes_recibo].upper()} / {ano_recibo}", styles['HeaderSubtitle']))
    story.append(Spacer(1, 0.4*cm)) # Espaço reduzido

    # --- Informações do Funcionário ---
    story.append(Paragraph("Informações do Funcionário:", styles['SectionHeading']))
    employee_data = [
        [Paragraph("Nome:", styles['EmployeeDetailBold']), Paragraph(funcionario_info['NomeCompleto'], styles['EmployeeDetail']),
         Paragraph("Categoria:", styles['EmployeeDetailBold']), Paragraph(funcionario_info['CategoriaProfissional'], styles['EmployeeDetail'])],
        [Paragraph("Nº Funcionário:", styles['EmployeeDetailBold']), Paragraph(funcionario_info['NumeroFuncionario'], styles['EmployeeDetail']),
         Paragraph("Salário Base:", styles['EmployeeDetailBold']), Paragraph(f"{salario_base_mensal:.2f} €", styles['EmployeeDetail'])],
        [Paragraph("NIF:", styles['EmployeeDetailBold']), Paragraph(funcionario_info['NIF'], styles['EmployeeDetail']),
         Paragraph("IRS (%):", styles['EmployeeDetailBold']), Paragraph(f"{taxa_irs*100:.2f} %", styles['EmployeeDetail'])],
        [Paragraph("NISS:", styles['EmployeeDetailBold']), Paragraph(funcionario_info['NISS'], styles['EmployeeDetail']),
         Paragraph("Seg. Social (%):", styles['EmployeeDetailBold']), Paragraph(f"{taxa_seguranca_social_funcionario*100:.2f} %", styles['EmployeeDetail'])],
        [Paragraph("Departamento:", styles['EmployeeDetailBold']), Paragraph(funcionario_info['Departamento'] if funcionario_info['Departamento'] else 'N/A', styles['EmployeeDetail']),
         Paragraph("", styles['EmployeeDetailBold']), Paragraph("", styles['EmployeeDetail'])], # Espaço vazio para alinhar
    ]
    employee_table = Table(employee_data, colWidths=[3.5*cm, 6.5*cm, 3.5*cm, 5.5*cm])
    employee_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('GRID', (0,0), (-1,-1), 0.25, colors.HexColor('#E0E0E0')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#C3D9E8')),
    ]))
    story.append(employee_table)
    story.append(Spacer(1, 0.4*cm)) # Espaço reduzido

    # --- Tabela de Rendimentos ---
    story.append(Paragraph("Rendimentos:", styles['SectionHeading']))
    data_rendimentos = [
        [Paragraph("Descrição", styles['TableColHeader']), Paragraph("Valor (€)", styles['TableColHeader'])]
    ]
    data_rendimentos.append([Paragraph("Salário Base Mensal", styles['TableTextLeft']), Paragraph(f"{salario_base_mensal:.2f}", styles['TableTextRight'])])
    if valor_horas_extra > 0:
        data_rendimentos.append([Paragraph(f"Horas Extra ({total_horas_extra_mes:.2f}h)", styles['TableTextLeft']), Paragraph(f"{valor_horas_extra:.2f}", styles['TableTextRight'])])
    data_rendimentos.append([Paragraph("Subsídio de Alimentação", styles['TableTextLeft']), Paragraph(f"{subsidio_alimentacao:.2f}", styles['TableTextRight'])])
    
    # Linha final de Vencimento Bruto
    data_rendimentos.append([
        Paragraph("<b>Vencimento Bruto</b>", styles['TableTotalText']),
        Paragraph(f"<b>{vencimento_bruto + subsidio_alimentacao:.2f}</b>", styles['TableTotalValue'])
    ])

    table_rendimentos = Table(data_rendimentos, colWidths=[13*cm, 5*cm])
    table_rendimentos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#C3D9E8')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#333333')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 3), # Reduzir padding
        ('TOPPADDING', (0,0), (-1,0), 3),    # Reduzir padding
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0E0E0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E0E0E0')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E0E0E0')),
        ('LEFTPADDING', (0,0), (-1,-1), 2),  # Reduzir padding
        ('RIGHTPADDING', (0,0), (-1,-1), 2), # Reduzir padding
    ]))
    story.append(table_rendimentos)
    story.append(Spacer(1, 0.4*cm)) # Espaço reduzido

    # --- Tabela de Descontos ---
    story.append(Paragraph("Descontos:", styles['SectionHeading']))
    data_descontos = [
        [Paragraph("Descrição", styles['TableColHeader']), Paragraph("Valor (€)", styles['TableColHeader'])]
    ]
    data_descontos.append([Paragraph(f"IRS ({taxa_irs*100:.2f}%)", styles['TableTextLeft']), Paragraph(f"{desconto_irs:.2f}", styles['TableTextRight'])])
    data_descontos.append([Paragraph(f"Segurança Social ({taxa_seguranca_social_funcionario*100:.2f}%)", styles['TableTextLeft']), Paragraph(f"{desconto_ss:.2f}", styles['TableTextRight'])])
    if total_horas_ausencia_geral > 0:
        data_descontos.append([Paragraph(f"Ausências ({total_horas_ausencia_geral:.2f}h)", styles['TableTextLeft']), Paragraph(f"{desconto_ausencia:.2f}", styles['TableTextRight'])])
    
    # Linha final de Total Descontos
    data_descontos.append([
        Paragraph("<b>Total Descontos</b>", styles['TableTotalText']),
        Paragraph(f"<b>{(desconto_irs + desconto_ss + desconto_ausencia):.2f}</b>", styles['TableTotalValue'])
    ])

    table_descontos = Table(data_descontos, colWidths=[13*cm, 5*cm])
    table_descontos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#C3D9E8')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#333333')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 3), # Reduzir padding
        ('TOPPADDING', (0,0), (-1,0), 3),    # Reduzir padding
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0E0E0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E0E0E0')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E0E0E0')),
        ('LEFTPADDING', (0,0), (-1,-1), 2),  # Reduzir padding
        ('RIGHTPADDING', (0,0), (-1,-1), 2), # Reduzir padding
    ]))
    story.append(table_descontos)
    story.append(Spacer(1, 0.6*cm)) # Espaço reduzido

    # --- Salário Líquido Final ---
    story.append(Paragraph(f"Salário Líquido a Receber:", styles['FinalTotalLabel']))
    story.append(Paragraph(f"{salario_liquido:.2f} €", styles['FinalTotalValue']))
    story.append(Spacer(1, 0.6*cm)) # Espaço reduzido

    # --- Resumo de Férias e Licenças ---
    story.append(Paragraph("Resumo de Férias e Licenças no Mês:", styles['SectionHeading']))
    summary_data = [
        [Paragraph("Dias de Férias:", styles['EmployeeDetailBold']), Paragraph(f"{dias_ferias_mes} dias", styles['EmployeeDetail'])],
        [Paragraph("Dias de Licença:", styles['EmployeeDetailBold']), Paragraph(f"{dias_licencas_mes} dias", styles['EmployeeDetail'])],
    ]
    summary_table = Table(summary_data, colWidths=[5*cm, 13*cm])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('GRID', (0,0), (-1,-1), 0.25, colors.HexColor('#E0E0E0')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#C3D9E8')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.8*cm)) # Espaço reduzido

    # --- Rodapé ---
    story.append(Paragraph("Documento gerado pelo Sistema de Gestão de Horas", styles['FooterText']))
    story.append(Paragraph(f"Impresso em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['FooterText']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# --- Lógica da Aplicação Streamlit ---

# Inicialização do estado da sessão para controlar a aba ativa
if 'active_tab_index' not in st.session_state:
    st.session_state.active_tab_index = 0 # 0 = Dashboard

# Carregar dados iniciais (se a conexão for bem-sucedida)
# Estas variáveis são definidas no início para serem usadas em todas as abas sem 'NameError'
funcionarios_df = get_funcionarios()
registos_diarios_df = get_registos_diarios()
ferias_df = get_ferias()
faltas_df = get_faltas()
licencas_df = get_licencas()
tipos_ocorrencia_df = get_tipos_ocorrencia() # Usado para mapear IDs para nomes
acertos_semestrais_df = get_acertos_semestrais()

# ATUALIZADO: Renomear a coluna 'TipoID' para 'TipoOcorrenciaID' no DataFrame
if not tipos_ocorrencia_df.empty and 'TipoID' in tipos_ocorrencia_df.columns:
    tipos_ocorrencia_df = tipos_ocorrencia_df.rename(columns={'TipoID': 'TipoOcorrenciaID'})


# Mapeamentos para uso em selects (definidos uma vez após carregar dados)
funcionario_nomes = funcionarios_df['NomeCompleto'].tolist() if not funcionarios_df.empty else []
funcionario_id_map = dict(zip(funcionarios_df['NomeCompleto'], funcionarios_df['FuncionarioID'])) if not funcionarios_df.empty else {}
# Incluir 'N/A' como opção para departamentos que ainda não foram definidos
departamentos_unicos = ['Todos'] + sorted(funcionarios_df['Departamento'].dropna().unique().tolist()) if not funcionarios_df.empty else ['Todos']

tipo_ocorrencia_nomes = tipos_ocorrencia_df['Descricao'].tolist() if not tipos_ocorrencia_df.empty else []
tipo_ocorrencia_id_map = dict(zip(tipos_ocorrencia_df['Descricao'], tipos_ocorrencia_df['TipoOcorrenciaID'])) if not tipos_ocorrencia_df.empty else {}
tipo_ocorrencia_sigla_map = dict(zip(tipos_ocorrencia_df['Descricao'], tipos_ocorrencia_df['Sigla'])) if not tipos_ocorrencia_df.empty else {}


# --- Verifica se a conexão à DB falhou e impede o resto do app de carregar ---
if funcionarios_df.empty and get_db_connection() is None:
    st.stop() # Parar a execução se a conexão falhar e não houver dados


# Sidebar para navegação
st.sidebar.title("Sistema de Gestão de Horas")
st.sidebar.markdown("---")

if st.sidebar.button("📊 Dashboard", key="nav_dashboard"):
    st.session_state.active_tab_index = 0
if st.sidebar.button("👥 Gestão de Funcionários", key="nav_funcionarios"):
    st.session_state.active_tab_index = 1
if st.sidebar.button("📝 Registos de Presença", key="nav_registos"):
    st.session_state.active_tab_index = 2
if st.sidebar.button("💰 Gerar Recibo de Vencimento", key="nav_recibo"):
    st.session_state.active_tab_index = 3
if st.sidebar.button("📈 Acertos Semestrais", key="nav_acertos"):
    st.session_state.active_tab_index = 4
if st.sidebar.button("📋 Relatórios e Análises", key="nav_relatorios_analises"): # Nome da aba atualizado
    st.session_state.active_tab_index = 5


st.sidebar.markdown("---")
st.sidebar.info("Desenvolvido por Susana Gonçalves")

# --- Conteúdo das Abas ---

# Aba: Dashboard
if st.session_state.active_tab_index == 0:
    st.title("📊 Dashboard Geral")
    st.write("Visão geral da gestão de funcionários e registos de horas.")

    # Cartões de métricas
    col1, col2, col3 = st.columns(3)

    num_funcionarios = len(funcionarios_df) if not funcionarios_df.empty else 0
    col1.metric("Total de Funcionários", num_funcionarios)

    # Exemplo: Total de horas trabalhadas no mês atual (agora usando HorasTrabalhadas e HorasExtraDiarias da DB)
    if not registos_diarios_df.empty:
        mes_atual = datetime.now().month
        ano_atual = datetime.now().year
        registos_mes_atual = registos_diarios_df[
            (pd.to_datetime(registos_diarios_df['DataRegisto']).dt.month == mes_atual) &
            (pd.to_datetime(registos_diarios_df['DataRegisto']).dt.year == ano_atual)
        ].copy() # Usar .copy() para evitar SettingWithCopyWarning

        total_horas_trabalhadas = registos_mes_atual['HorasTrabalhadas'].sum()
        total_horas_extra = registos_mes_atual['HorasExtraDiarias'].sum()
    else:
        total_horas_trabalhadas = 0
        total_horas_extra = 0

    col2.metric("Horas Trabalhadas (mês atual)", f"{total_horas_trabalhadas:.2f}h")
    col3.metric("Horas Extra (mês atual)", f"{total_horas_extra:.2f}h")

    st.markdown("---")

    st.subheader("Últimos Registos de Presença")
    if not registos_diarios_df.empty:
        # Combinar com nomes de funcionários para melhor visualização
        registos_com_nomes = pd.merge(registos_diarios_df, funcionarios_df[['FuncionarioID', 'NomeCompleto']],
                                      on='FuncionarioID', how='left')
        # Mapear TipoOcorrenciaID para Descricao
        registos_com_nomes = pd.merge(registos_com_nomes, tipos_ocorrencia_df[['TipoOcorrenciaID', 'Descricao']], # Corrigido para 'TipoOcorrenciaID'
                                      left_on='TipoOcorrenciaID', right_on='TipoOcorrenciaID', how='left') # Corrigido para 'TipoOcorrenciaID'
        registos_com_nomes = registos_com_nomes.rename(columns={'Descricao': 'Tipo de Ocorrência'})
        # Mostra as colunas que realmente existem no DB
        st.dataframe(registos_com_nomes[['NomeCompleto', 'DataRegisto', 'HorasTrabalhadas', 'HorasExtraDiarias', 'HorasAusencia', 'Tipo de Ocorrência', 'Observacoes']]
                     .tail(10).sort_values(by='DataRegisto', ascending=False), use_container_width=True)
    else:
        st.info("Nenhum registo de presença encontrado.")

    st.subheader("Próximas Férias e Licenças")
    if not ferias_df.empty or not licencas_df.empty:
        # Filtrar apenas futuras ou em andamento
        today = date.today()
        
        # Certifique-se de que as colunas de data são do tipo datetime.date para comparação correta
        # Pandas pode carregar 'date' como datetime.datetime, então convertemos para date
        ferias_df['DataInicio'] = pd.to_datetime(ferias_df['DataInicio']).dt.date
        ferias_df['DataFim'] = pd.to_datetime(ferias_df['DataFim']).dt.date
        licencas_df['DataInicio'] = pd.to_datetime(licencas_df['DataInicio']).dt.date
        licencas_df['DataFim'] = pd.to_datetime(licencas_df['DataFim']).dt.date


        proximas_ferias = ferias_df[ferias_df['DataFim'] >= today].sort_values(by='DataInicio').head(5)
        proximas_licencas = licencas_df[licencas_df['DataFim'] >= today].sort_values(by='DataInicio').head(5)

        st.markdown("##### Férias:")
        if not proximas_ferias.empty:
            ferias_com_nomes = pd.merge(proximas_ferias, funcionarios_df[['FuncionarioID', 'NomeCompleto']],
                                        on='FuncionarioID', how='left')
            st.dataframe(ferias_com_nomes[['NomeCompleto', 'DataInicio', 'DataFim', 'Observacoes']], use_container_width=True)
        else:
            st.info("Não há férias futuras registadas.")

        st.markdown("##### Licenças:")
        if not proximas_licencas.empty:
            licencas_com_nomes = pd.merge(proximas_licencas, funcionarios_df[['FuncionarioID', 'NomeCompleto']],
                                          on='FuncionarioID', how='left')
            # Correção para o KeyError: 'Observacoes' not in index na tabela Licenças
            cols_to_display_licenca = ['NomeCompleto', 'Motivo', 'DataInicio', 'DataFim']
            if 'Observacoes' in licencas_com_nomes.columns:
                cols_to_display_licenca.append('Observacoes')
            st.dataframe(licencas_com_nomes[cols_to_display_licenca], use_container_width=True)
        else:
            st.info("Não há licenças futuras registadas.")
    else:
        st.info("Nenhum registo de férias ou licenças futuras encontrado.")


# Aba: Gestão de Funcionários (ATUALIZADO: Adicionado Departamento e DiasFeriasAnuais)
elif st.session_state.active_tab_index == 1:
    st.title("👥 Gestão de Funcionários")
    st.write("Adicione, edite ou remova informações de funcionários.")

    with st.expander("Adicionar/Editar Funcionário"):
        with st.form("funcionario_form", clear_on_submit=True):
            funcionario_id_edit = st.number_input("ID do Funcionário (para editar, deixe 0 para adicionar novo)", min_value=0, value=0, step=1, key="func_id_edit")
            nome_completo = st.text_input("Nome Completo", key="func_nome_completo")
            numero_funcionario = st.text_input("Número de Funcionário", key="func_numero")
            data_nascimento = st.date_input("Data de Nascimento", value=date(2000, 1, 1), key="func_data_nascimento")
            nif = st.text_input("NIF", key="func_nif")
            niss = st.text_input("NISS", key="func_niss")
            telefone = st.text_input("Telefone", key="func_telefone")
            email = st.text_input("Email", key="func_email")
            categoria_profissional = st.text_input("Categoria Profissional", key="func_categoria")
            departamento = st.text_input("Departamento", key="func_departamento") # NOVO CAMPO
            salario_base_mensal = st.number_input("Salário Base Mensal", min_value=0.0, format="%.2f", key="func_salario")
            valor_subsidio_alimentacao_diario = st.number_input("Valor Subsídio Alimentação Diário", min_value=0.0, format="%.2f", key="func_subsidio")
            taxa_irs = st.number_input("Taxa IRS (%)", min_value=0.0, max_value=100.0, format="%.2f", key="func_irs") / 100
            taxa_seguranca_social_funcionario = st.number_input("Taxa Segurança Social Funcionário (%)", min_value=0.0, max_value=100.0, format="%.2f", key="func_ss") / 100
            horas_trabalho_mensal_padrao = st.number_input("Horas Trabalho Mensal Padrão", min_value=0, step=1, key="func_horas_padrao")
            taxa_hora_extra_50 = st.number_input("Taxa Hora Extra 50% (%)", min_value=0.0, max_value=100.0, format="%.2f", key="func_taxa_he50") / 100
            taxa_hora_extra_100 = st.number_input("Taxa Hora Extra 100% (%)", min_value=0.0, max_value=100.0, format="%.2f", key="func_taxa_he100") / 100
            dias_ferias_anuais = st.number_input("Dias de Férias Anuais (Direito)", min_value=0, step=1, value=22, key="func_dias_ferias_anuais") # NOVO CAMPO

            submitted = st.form_submit_button("Guardar Funcionário")

            if submitted:
                funcionario_data = {
                    'NomeCompleto': nome_completo,
                    'NumeroFuncionario': numero_funcionario,
                    'DataNascimento': data_nascimento,
                    'NIF': nif,
                    'NISS': niss,
                    'Telefone': telefone,
                    'Email': email,
                    'CategoriaProfissional': categoria_profissional,
                    'Departamento': departamento, # NOVO CAMPO
                    'SalarioBaseMensal': salario_base_mensal,
                    'ValorSubsidioAlimentacaoDiario': valor_subsidio_alimentacao_diario,
                    'TaxaIRS': taxa_irs,
                    'TaxaSegurancaSocialFuncionario': taxa_seguranca_social_funcionario,
                    'HorasTrabalhoMensalPadrao': horas_trabalho_mensal_padrao,
                    'TaxaHoraExtra50': taxa_hora_extra_50,
                    'TaxaHoraExtra100': taxa_hora_extra_100,
                    'DiasFeriasAnuais': dias_ferias_anuais # NOVO CAMPO
                }
                if funcionario_id_edit == 0:
                    if add_funcionario(funcionario_data):
                        st.success("Funcionário adicionado com sucesso!")
                    else:
                        st.error("Erro ao adicionar funcionário.")
                else:
                    if update_funcionario(funcionario_id_edit, funcionario_data):
                        st.success(f"Funcionário {funcionario_id_edit} atualizado com sucesso!")
                    else:
                        st.error("Erro ao atualizar funcionário.")
                st.session_state.active_tab_index = 1
                st.rerun()

    st.markdown("---")
    st.subheader("Lista de Funcionários")

    if not funcionarios_df.empty:
        st.dataframe(funcionarios_df[['FuncionarioID', 'NomeCompleto', 'Departamento', 'CategoriaProfissional', 'SalarioBaseMensal', 'DiasFeriasAnuais']], use_container_width=True)

        st.markdown("#### Apagar Funcionário")
        funcionario_ids_delete = funcionarios_df['FuncionarioID'].tolist()
        if funcionario_ids_delete:
            funcionario_id_to_delete = st.selectbox(
                "Selecione o ID do funcionário a apagar",
                funcionario_ids_delete,
                key="delete_func_select"
            )
            if st.button("Apagar Funcionário", key="delete_func_button"):
                confirm = st.warning("Apagar um funcionário também apagará todos os registos diários, férias, faltas, licenças e acertos semestrais associados. Tem certeza? **Confirme abaixo.**")
                if st.button("Sim, Apagar Definitivamente", key="confirm_delete_func_button"):
                    if delete_funcionario(funcionario_id_to_delete):
                        st.success(f"Funcionário ID {funcionario_id_to_delete} e todos os seus dados relacionados apagados com sucesso!")
                        st.session_state.active_tab_index = 1
                        st.rerun()
                    else:
                        st.error(f"Erro ao apagar funcionário ID {funcionario_id_to_delete}.")
        else:
            st.info("Não há funcionários para apagar.")


# Aba: Registos de Presença (Diários, Férias, Faltas, Licenças, Tipos de Ocorrência)
elif st.session_state.active_tab_index == 2:
    st.title("📝 Registos de Presença e Ausência")
    st.write("Gerencie os registos diários, férias, faltas e licenças dos funcionários.")

    registro_type = st.radio(
        "Selecione o tipo de registo:",
        ("Registo Diário", "Férias", "Faltas", "Licenças", "Tipos de Ocorrência"),
        key="registro_type_radio",
        horizontal=True
    )

    # --- Formulário de Registo Diário ---
    if registro_type == "Registo Diário":
        st.subheader("Adicionar/Editar Registo Diário")
        st.info("Os campos abaixo permitem registar `HorasTrabalhadas`, `HorasExtraDiarias`, `HorasAusencia` e `Observacoes` diretamente, conforme a sua tabela `RegistosDiarios`.")
        with st.expander("Formulário de Registo Diário"):
            with st.form("registo_diario_form", clear_on_submit=True):
                registo_id_edit = st.number_input("ID do Registo (para editar, deixe 0 para adicionar novo)", min_value=0, value=0, step=1, key="rd_id_edit")
                selected_funcionario_name_rd = st.selectbox("Funcionário", funcionario_nomes, key="rd_funcionario_select")
                selected_funcionario_id_rd = funcionario_id_map.get(selected_funcionario_name_rd)
                data_registo = st.date_input("Data do Registo", value=date.today(), key="rd_data_registo")
                selected_tipo_ocorrencia_name_rd = st.selectbox("Tipo de Ocorrência", tipo_ocorrencia_nomes, key="rd_tipo_ocorrencia_select")
                selected_tipo_ocorrencia_id_rd = tipo_ocorrencia_id_map.get(selected_tipo_ocorrencia_name_rd)
                horas_trabalhadas = st.number_input("Horas Trabalhadas (normais)", min_value=0.0, format="%.2f", key="rd_horas_trabalhadas")
                horas_extra_diarias = st.number_input("Horas Extra Diárias", min_value=0.0, format="%.2f", key="rd_horas_extra_diarias")
                horas_ausencia = st.number_input("Horas de Ausência (não justificadas, se aplicável)", min_value=0.0, format="%.2f", key="rd_horas_ausencia")
                observacoes = st.text_area("Observações", key="rd_observacoes")

                submitted_rd = st.form_submit_button("Guardar Registo Diário")

                if submitted_rd:
                    if selected_funcionario_id_rd and selected_tipo_ocorrencia_id_rd is not None:
                        registo_data = {
                            'FuncionarioID': selected_funcionario_id_rd,
                            'DataRegisto': data_registo,
                            'TipoOcorrenciaID': selected_tipo_ocorrencia_id_rd,
                            'HorasTrabalhadas': horas_trabalhadas,
                            'HorasExtraDiarias': horas_extra_diarias,
                            'HorasAusencia': horas_ausencia,
                            'Observacoes': observacoes
                        }
                        if registo_id_edit == 0:
                            if add_registo_diario(registo_data):
                                st.success("Registo diário adicionado com sucesso!")
                            else:
                                st.error("Erro ao adicionar registo diário.")
                        else:
                            if update_registo_diario(registo_id_edit, registo_data):
                                st.success(f"Registo diário {registo_id_edit} atualizado com sucesso!")
                            else:
                                st.error("Erro ao atualizar registo diário.")
                        st.session_state.active_tab_index = 2
                        st.rerun()
                    else:
                        st.warning("Por favor, selecione um funcionário e um tipo de ocorrência.")

        st.markdown("---")
        st.subheader("Registos Diários Existentes")
        registos_diarios_df = get_registos_diarios() # Recarrega dados
        if not registos_diarios_df.empty:
            registos_diarios_com_nomes = pd.merge(registos_diarios_df, funcionarios_df[['FuncionarioID', 'NomeCompleto']], on='FuncionarioID', how='left')
            registos_diarios_com_nomes = pd.merge(registos_diarios_com_nomes, tipos_ocorrencia_df[['TipoOcorrenciaID', 'Descricao']], left_on='TipoOcorrenciaID', right_on='TipoOcorrenciaID', how='left') # Corrigido aqui
            registos_diarios_com_nomes = registos_diarios_com_nomes.rename(columns={'Descricao': 'Tipo de Ocorrência'})
            st.dataframe(registos_diarios_com_nomes[['RegistoID', 'NomeCompleto', 'DataRegisto', 'Tipo de Ocorrência', 'HorasTrabalhadas', 'HorasExtraDiarias', 'HorasAusencia', 'Observacoes']], use_container_width=True)

            st.markdown("#### Apagar Registo Diário")
            registo_ids_delete = registos_diarios_df['RegistoID'].tolist()
            if registo_ids_delete:
                registo_id_to_delete = st.selectbox("Selecione o ID do registo a apagar", registo_ids_delete, key="delete_rd_select")
                if st.button("Apagar Registo Diário", key="delete_rd_button"):
                    if delete_registo_diario(registo_id_to_delete):
                        st.success(f"Registo diário ID {registo_id_to_delete} apagado com sucesso!")
                        st.session_state.active_tab_index = 2
                        st.rerun()
                    else:
                        st.error(f"Erro ao apagar registo diário ID {registo_id_to_delete}.")
            else:
                st.info("Nenhum registo diário para apagar.")
        else:
            st.info("Nenhum registo diário encontrado.")

    # --- Formulário de Férias (ATUALIZADO: Com campo Aprovado) ---
    elif registro_type == "Férias":
        st.subheader("Adicionar/Editar Registo de Férias")
        with st.expander("Formulário de Férias"):
            with st.form("ferias_form", clear_on_submit=True):
                ferias_id_edit = st.number_input("ID das Férias (para editar, deixe 0 para adicionar novo)", min_value=0, value=0, step=1, key="ferias_id_edit")
                selected_funcionario_name_ferias = st.selectbox("Funcionário", funcionario_nomes, key="ferias_funcionario_select")
                selected_funcionario_id_ferias = funcionario_id_map.get(selected_funcionario_name_ferias)
                data_inicio_ferias = st.date_input("Data de Início", value=date.today(), key="ferias_data_inicio")
                data_fim_ferias = st.date_input("Data de Fim", value=date.today() + timedelta(days=7), key="ferias_data_fim")
                observacoes_ferias = st.text_area("Observações", key="ferias_obs")
                aprovado_ferias = st.checkbox("Aprovado?", key="ferias_aprovado") # NOVO CAMPO

                submitted_ferias = st.form_submit_button("Guardar Férias")

                if submitted_ferias:
                    if selected_funcionario_id_ferias:
                        ferias_data = {
                            'FuncionarioID': selected_funcionario_id_ferias,
                            'DataInicio': data_inicio_ferias,
                            'DataFim': data_fim_ferias,
                            'Observacoes': observacoes_ferias,
                            'Aprovado': aprovado_ferias # NOVO CAMPO
                        }
                        if ferias_id_edit == 0:
                            if add_ferias(ferias_data):
                                st.success("Férias adicionadas com sucesso!")
                            else:
                                st.error("Erro ao adicionar férias.")
                        else:
                            if update_ferias(ferias_id_edit, ferias_data):
                                st.success(f"Férias {ferias_id_edit} atualizadas com sucesso!")
                            else:
                                st.error("Erro ao atualizar férias.")
                        st.session_state.active_tab_index = 2
                        st.rerun()
                    else:
                        st.warning("Por favor, selecione um funcionário.")

        st.markdown("---")
        st.subheader("Registos de Férias Existentes")
        ferias_df = get_ferias()
        if not ferias_df.empty:
            ferias_com_nomes = pd.merge(ferias_df, funcionarios_df[['FuncionarioID', 'NomeCompleto']], on='FuncionarioID', how='left')
            st.dataframe(ferias_com_nomes[['FeriasID', 'NomeCompleto', 'DataInicio', 'DataFim', 'Aprovado', 'Observacoes']], use_container_width=True) # Exibir Aprovado

            st.markdown("#### Apagar Registo de Férias")
            ferias_ids_delete = ferias_df['FeriasID'].tolist()
            if ferias_ids_delete:
                ferias_id_to_delete = st.selectbox("Selecione o ID das férias a apagar", ferias_ids_delete, key="delete_ferias_select")
                if st.button("Apagar Férias", key="delete_ferias_button"):
                    if delete_ferias(ferias_id_to_delete):
                        st.success(f"Férias ID {ferias_id_to_delete} apagadas com sucesso!")
                        st.session_state.active_tab_index = 2
                        st.rerun()
                    else:
                        st.error(f"Erro ao apagar férias ID {ferias_id_to_delete}.")
            else:
                st.info("Nenhum registo de férias para apagar.")
        else:
            st.info("Nenhum registo de férias encontrado.")

    # --- Formulário de Faltas (ATUALIZADO: Com campo Aprovado) ---
    elif registro_type == "Faltas":
        st.subheader("Adicionar/Editar Registo de Falta")
        with st.expander("Formulário de Falta"):
            with st.form("falta_form", clear_on_submit=True):
                falta_id_edit = st.number_input("ID da Falta (para editar, deixe 0 para adicionar novo)", min_value=0, value=0, step=1, key="falta_id_edit")
                selected_funcionario_name_faltas = st.selectbox("Funcionário", funcionario_nomes, key="faltas_funcionario_select")
                selected_funcionario_id_faltas = funcionario_id_map.get(selected_funcionario_name_faltas)
                data_falta = st.date_input("Data da Falta", value=date.today(), key="falta_data_falta")
                motivo_falta = st.text_input("Motivo da Falta", key="falta_motivo")
                justificada_falta = st.checkbox("Falta Justificada?", key="falta_justificada")
                horas_ausencia_falta = st.number_input("Horas de Ausência pela Falta", min_value=0.0, format="%.2f", key="falta_horas_ausencia")
                aprovado_falta = st.checkbox("Aprovado?", key="falta_aprovado") # NOVO CAMPO

                submitted_falta = st.form_submit_button("Guardar Falta")

                if submitted_falta:
                    if selected_funcionario_id_faltas:
                        falta_data = {
                            'FuncionarioID': selected_funcionario_id_faltas,
                            'DataFalta': data_falta,
                            'Motivo': motivo_falta,
                            'Justificada': justificada_falta,
                            'HorasAusenciaFalta': horas_ausencia_falta,
                            'Aprovado': aprovado_falta # NOVO CAMPO
                        }
                        if falta_id_edit == 0:
                            if add_falta(falta_data):
                                st.success("Falta adicionada com sucesso!")
                            else:
                                st.error("Erro ao adicionar falta.")
                        else:
                            if update_falta(falta_id_edit, falta_data):
                                st.success(f"Falta {falta_id_edit} atualizada com sucesso!")
                            else:
                                st.error("Erro ao atualizar falta.")
                        st.session_state.active_tab_index = 2
                        st.rerun()
                    else:
                        st.warning("Por favor, selecione um funcionário.")

        st.markdown("---")
        st.subheader("Registos de Faltas Existentes")
        faltas_df = get_faltas()
        if not faltas_df.empty:
            faltas_com_nomes = pd.merge(faltas_df, funcionarios_df[['FuncionarioID', 'NomeCompleto']], on='FuncionarioID', how='left')
            st.dataframe(faltas_com_nomes[['FaltaID', 'NomeCompleto', 'DataFalta', 'Motivo', 'Justificada', 'HorasAusenciaFalta', 'Aprovado']], use_container_width=True) # Exibir Aprovado

            st.markdown("#### Apagar Registo de Falta")
            falta_ids_delete = faltas_df['FaltaID'].tolist()
            if falta_ids_delete:
                falta_id_to_delete = st.selectbox("Selecione o ID da falta a apagar", falta_ids_delete, key="delete_falta_select")
                if st.button("Apagar Falta", key="delete_falta_button"):
                    if delete_falta(falta_id_to_delete):
                        st.success(f"Falta ID {falta_id_to_delete} apagada com sucesso!")
                        st.session_state.active_tab_index = 2
                        st.rerun()
                    else:
                        st.error(f"Erro ao apagar falta ID {falta_id_to_delete}.")
            else:
                st.info("Nenhum registo de falta para apagar.")
        else:
            st.info("Nenhum registo de falta encontrado.")

    # --- Formulário de Licenças (ATUALIZADO: Com campo Aprovado) ---
    elif registro_type == "Licenças":
        st.subheader("Adicionar/Editar Registo de Licença")
        with st.expander("Formulário de Licença"):
            with st.form("licenca_form", clear_on_submit=True):
                licenca_id_edit = st.number_input("ID da Licença (para editar, deixe 0 para adicionar novo)", min_value=0, value=0, step=1, key="licenca_id_edit")
                selected_funcionario_name_licenca = st.selectbox("Funcionário", funcionario_nomes, key="licenca_funcionario_select")
                selected_funcionario_id_licenca = funcionario_id_map.get(selected_funcionario_name_licenca)
                data_inicio_licenca = st.date_input("Data de Início", value=date.today(), key="licenca_data_inicio")
                data_fim_licenca = st.date_input("Data de Fim", value=date.today() + timedelta(days=7), key="licenca_data_fim")
                motivo_licenca = st.text_input("Motivo da Licença", key="licenca_motivo")
                observacoes_licenca = st.text_area("Observações", key="licenca_obs")
                aprovado_licenca = st.checkbox("Aprovado?", key="licenca_aprovado") # NOVO CAMPO

                submitted_licenca = st.form_submit_button("Guardar Licença")

                if submitted_licenca:
                    if selected_funcionario_id_licenca:
                        licenca_data = {
                            'FuncionarioID': selected_funcionario_id_licenca,
                            'DataInicio': data_inicio_licenca,
                            'DataFim': data_fim_licenca,
                            'Motivo': motivo_licenca,
                            'Observacoes': observacoes_licenca,
                            'Aprovado': aprovado_licenca # NOVO CAMPO
                        }
                        if licenca_id_edit == 0:
                            if add_licenca(licenca_data):
                                st.success("Licença adicionada com sucesso!")
                            else:
                                st.error("Erro ao adicionar licença.")
                        else:
                            if update_licenca(licenca_id_edit, licenca_data):
                                st.success(f"Licença {licenca_id_edit} atualizada com sucesso!")
                            else:
                                st.error("Erro ao atualizar licença.")
                        st.session_state.active_tab_index = 2
                        st.rerun()
                    else:
                        st.warning("Por favor, selecione um funcionário.")

        st.markdown("---")
        st.subheader("Registos de Licenças Existentes")
        licencas_df = get_licencas()
        if not licencas_df.empty:
            licencas_com_nomes = pd.merge(licencas_df, funcionarios_df[['FuncionarioID', 'NomeCompleto']], on='FuncionarioID', how='left')
            cols_to_display_licenca = ['LicencaID', 'NomeCompleto', 'Motivo', 'DataInicio', 'DataFim', 'Aprovado'] # Exibir Aprovado
            if 'Observacoes' in licencas_com_nomes.columns:
                cols_to_display_licenca.append('Observacoes')
            
            st.dataframe(licencas_com_nomes[cols_to_display_licenca], use_container_width=True)

            st.markdown("#### Apagar Registo de Licença")
            licenca_ids_delete = licencas_df['LicencaID'].tolist()
            if licenca_ids_delete:
                licenca_id_to_delete = st.selectbox("Selecione o ID da licença a apagar", licenca_ids_delete, key="delete_licenca_select")
                if st.button("Apagar Licença", key="delete_licenca_button"):
                    if delete_licenca(licenca_id_to_delete): 
                        st.success(f"Licença ID {licenca_id_to_delete} apagada com sucesso!")
                        st.session_state.active_tab_index = 2
                        st.rerun()
                    else:
                        st.error(f"Erro ao apagar licença ID {licenca_id_to_delete}.")
            else:
                st.info("Nenhum registo de licença para apagar.")
        else:
            st.info("Nenhum registo de licença encontrado.")

    # --- Gestão de Tipos de Ocorrência (NOVA SEÇÃO CRUD) ---
    elif registro_type == "Tipos de Ocorrência":
        st.subheader("Gestão de Tipos de Ocorrência")
        st.info("Adicione, edite ou apague os tipos de ocorrência utilizados no sistema.")
        
        with st.expander("Adicionar/Editar Tipo de Ocorrência"):
            with st.form("tipo_ocorrencia_form", clear_on_submit=True):
                tipo_id_edit = st.number_input("ID do Tipo (para editar, deixe 0 para adicionar novo)", min_value=0, value=0, step=1, key="to_id_edit")
                codigo = st.text_input("Código (Sigla Curta)", key="to_codigo")
                descricao = st.text_input("Descrição Completa", key="to_descricao")
                horas_padrao = st.number_input("Horas Padrão (se aplicável, e.g., 8h para dia de trabalho)", min_value=0.0, format="%.2f", key="to_horas_padrao")
                eh_turno = st.checkbox("É um Tipo de Turno?", key="to_eh_turno")
                eh_horas_extra = st.checkbox("Implica Horas Extra?", key="to_eh_horas_extra")
                eh_ausencia = st.checkbox("É uma Ausência?", key="to_eh_ausencia")
                eh_fots = st.checkbox("Conta para FOTS (Folgas por Horas Extra)?", key="to_eh_fots")
                eh_folga_compensatoria = st.checkbox("É uma Folga Compensatória?", key="to_eh_folga_comp")
                sigla = st.text_input("Sigla para Relatórios (ex: 'D' para Diurno, 'F' para Férias)", max_chars=5, key="to_sigla")

                submitted_to = st.form_submit_button("Guardar Tipo de Ocorrência")

                if submitted_to:
                    if not codigo or not descricao or not sigla:
                        st.error("Código, Descrição e Sigla são campos obrigatórios.")
                    else:
                        to_data = {
                            'Codigo': codigo,
                            'Descricao': descricao,
                            'HorasPadrao': horas_padrao,
                            'EhTurno': eh_turno,
                            'EhHorasExtra': eh_horas_extra,
                            'EhAusencia': eh_ausencia,
                            'EhFOTS': eh_fots,
                            'EhFolgaCompensatoria': eh_folga_compensatoria,
                            'Sigla': sigla
                        }
                        if tipo_id_edit == 0:
                            if add_tipo_ocorrencia(to_data):
                                st.success("Tipo de Ocorrência adicionado com sucesso!")
                            else:
                                st.error("Erro ao adicionar tipo de ocorrência.")
                        else:
                            if update_tipo_ocorrencia(tipo_id_edit, to_data):
                                st.success(f"Tipo de Ocorrência {tipo_id_edit} atualizado com sucesso!")
                            else:
                                st.error("Erro ao atualizar tipo de ocorrência.")
                        st.session_state.active_tab_index = 2
                        st.rerun()

        st.markdown("---")
        st.subheader("Tipos de Ocorrência Existentes")
        tipos_ocorrencia_df = get_tipos_ocorrencia() # Recarrega dados
        if not tipos_ocorrencia_df.empty:
            st.dataframe(tipos_ocorrencia_df, use_container_width=True)

            st.markdown("#### Apagar Tipo de Ocorrência")
            tipo_ids_delete = tipos_ocorrencia_df['TipoOcorrenciaID'].tolist() # Corrigido aqui
            if tipo_ids_delete:
                tipo_id_to_delete = st.selectbox("Selecione o ID do tipo a apagar", tipo_ids_delete, key="delete_to_select")
                if st.button("Apagar Tipo de Ocorrência", key="delete_to_button"):
                    # Aviso importante antes de apagar um tipo de ocorrência
                    st.warning("Apagar um Tipo de Ocorrência pode afetar registos diários existentes que o utilizam. Prossiga com cautela.")
                    if st.button("Confirmo que quero apagar este tipo", key="confirm_delete_to_button"):
                        if delete_tipo_ocorrencia(tipo_id_to_delete):
                            st.success(f"Tipo de Ocorrência ID {tipo_id_to_delete} apagado com sucesso!")
                            st.session_state.active_tab_index = 2
                            st.rerun()
                        else:
                            st.error(f"Erro ao apagar tipo de ocorrência ID {tipo_id_to_delete}. Pode haver registos dependentes.")
            else:
                st.info("Nenhum tipo de ocorrência para apagar.")
        else:
            st.info("Nenhum tipo de ocorrência encontrado.")


# Aba: Gerar Recibo de Vencimento
elif st.session_state.active_tab_index == 3:
    st.title("💰 Gerar Recibo de Vencimento")
    st.write("Selecione um funcionário e um mês/ano para gerar o recibo de vencimento.")

    if not funcionarios_df.empty:
        selected_funcionario_name_recibo = st.selectbox(
            "Selecione o Funcionário",
            funcionario_nomes,
            key="recibo_funcionario_select"
        )
        selected_funcionario_id_recibo = funcionario_id_map.get(selected_funcionario_name_recibo)
    else:
        st.warning("Não há funcionários registados para gerar recibos. Por favor, adicione funcionários na aba 'Gestão de Funcionários'.")
        selected_funcionario_id_recibo = None

    col_mes, col_ano = st.columns(2)
    mes_recibo = col_mes.number_input("Mês", min_value=1, max_value=12, value=datetime.now().month, step=1, key="mes_recibo_input")
    ano_recibo = col_ano.number_input("Ano", min_value=2000, value=datetime.now().year, step=1, key="ano_recibo_input")

    if st.button("Gerar Recibo de Vencimento", key="gerar_recibo_button"):
        if selected_funcionario_id_recibo:
            funcionario_info = funcionarios_df[funcionarios_df['FuncionarioID'] == selected_funcionario_id_recibo].iloc[0]

            num_days_in_month = calendar.monthrange(ano_recibo, mes_recibo)[1]
            start_date = date(ano_recibo, mes_recibo, 1)
            end_date = date(ano_recibo, mes_recibo, num_days_in_month)

            registos_diarios_mes, faltas_mes, ferias_mes, licencas_mes = \
                get_all_events_for_employee_and_period(selected_funcionario_id_recibo, start_date, end_date)

            # --- Cálculos do Recibo de Vencimento ---
            salario_base_mensal = float(funcionario_info['SalarioBaseMensal'])
            valor_subsidio_alimentacao_diario = float(funcionario_info['ValorSubsidioAlimentacaoDiario'])
            taxa_irs = float(funcionario_info['TaxaIRS'])
            taxa_seguranca_social_funcionario = float(funcionario_info['TaxaSegurancaSocialFuncionario'])
            horas_trabalho_mensal_padrao = float(funcionario_info['HorasTrabalhoMensalPadrao'])
            taxa_hora_extra_50 = float(funcionario_info['TaxaHoraExtra50'])
            taxa_hora_extra_100 = float(funcionario_info['TaxaHoraExtra100'])

            total_horas_trabalhadas_mes = registos_diarios_mes['HorasTrabalhadas'].sum() if not registos_diarios_mes.empty else 0.0
            total_horas_extra_mes = registos_diarios_mes['HorasExtraDiarias'].sum() if not registos_diarios_mes.empty else 0.0

            total_horas_ausencia_registo_diario = registos_diarios_mes['HorasAusencia'].sum() if not registos_diarios_mes.empty else 0.0
            total_horas_ausencia_faltas = faltas_mes['HorasAusenciaFalta'].sum() if not faltas_mes.empty else 0.0
            total_horas_ausencia_geral = total_horas_ausencia_registo_diario + total_horas_ausencia_faltas

            dias_ferias_mes = 0
            if not ferias_mes.empty:
                for _, row in ferias_mes.iterrows():
                    start_event = row['DataInicio'].date() if isinstance(row['DataInicio'], datetime) else row['DataInicio']
                    end_event = row['DataFim'].date() if isinstance(row['DataFim'], datetime) else row['DataFim']
                    start = max(start_event, start_date)
                    end = min(end_event, end_date)
                    if start <= end:
                        dias_ferias_mes += (end - start).days + 1

            dias_licencas_mes = 0
            if not licencas_mes.empty:
                for _, row in licencas_mes.iterrows():
                    start_event = row['DataInicio'].date() if isinstance(row['DataInicio'], datetime) else row['DataInicio']
                    end_event = row['DataFim'].date() if isinstance(row['DataFim'], datetime) else row['DataFim']
                    start = max(start_event, start_date)
                    end = min(end_event, end_date)
                    if start <= end:
                        dias_licencas_mes += (end - start).days + 1

            custo_hora_padrao = salario_base_mensal / horas_trabalho_mensal_padrao if horas_trabalho_mensal_padrao > 0 else 0

            vencimento_bruto = salario_base_mensal
            valor_horas_extra = (total_horas_extra_mes * (1 + taxa_hora_extra_50) * custo_hora_padrao) # Assumindo 50%
            vencimento_bruto += valor_horas_extra

            desconto_irs = vencimento_bruto * taxa_irs
            desconto_ss = vencimento_bruto * taxa_seguranca_social_funcionario
            desconto_ausencia = total_horas_ausencia_geral * custo_hora_padrao

            dias_trabalhados_efetivos = registos_diarios_mes['DataRegisto'].nunique() if not registos_diarios_mes.empty else 0
            subsidio_alimentacao = dias_trabalhados_efetivos * valor_subsidio_alimentacao_diario

            salario_liquido = vencimento_bruto - desconto_irs - desconto_ss - desconto_ausencia + subsidio_alimentacao

            st.subheader(f"Recibo de Vencimento para {funcionario_info['NomeCompleto']} - {mes_recibo:02d}/{ano_recibo}")
            st.markdown("---")

            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown("#### Rendimentos")
                st.write(f"**Salário Base Mensal:** {salario_base_mensal:.2f} €")
                st.write(f"**Horas Trabalhadas (mês):** {total_horas_trabalhadas_mes:.2f}h")
                st.write(f"**Horas Extra (mês):** {total_horas_extra_mes:.2f}h")
                st.write(f"**Valor Horas Extra:** {valor_horas_extra:.2f} €")
                st.write(f"**Subsídio de Alimentação:** {subsidio_alimentacao:.2f} €")
                st.markdown(f"**Vencimento Bruto:** **{vencimento_bruto + subsidio_alimentacao:.2f} €**")

            with col_right:
                st.markdown("#### Descontos")
                st.write(f"**IRS ({taxa_irs*100:.2f}%):** {desconto_irs:.2f} €")
                st.write(f"**Segurança Social ({taxa_seguranca_social_funcionario*100:.2f}%):** {desconto_ss:.2f} €")
                st.write(f"**Ausências (Horas):** {total_horas_ausencia_geral:.2f}h")
                st.write(f"**Desconto por Ausência:** {desconto_ausencia:.2f} €")
                st.markdown(f"**Total Descontos:** **{(desconto_irs + desconto_ss + desconto_ausencia):.2f} €**")

            st.markdown("---")
            st.subheader(f"Salário Líquido a Receber: **{salario_liquido:.2f} €**")

            st.markdown("#### Resumo de Férias e Licenças no Mês")
            st.write(f"**Dias de Férias:** {dias_ferias_mes} dias")
            st.write(f"**Dias de Licença:** {dias_licencas_mes} dias")

            pdf_content = generate_payslip_pdf(
                funcionario_info, mes_recibo, ano_recibo,
                total_horas_trabalhadas_mes, total_horas_extra_mes,
                salario_base_mensal, valor_horas_extra,
                subsidio_alimentacao, vencimento_bruto,
                desconto_irs, taxa_irs, desconto_ss, taxa_seguranca_social_funcionario,
                total_horas_ausencia_geral, desconto_ausencia, salario_liquido,
                dias_ferias_mes, dias_licencas_mes
            )
            st.download_button(
                label="Baixar Recibo em PDF",
                data=pdf_content,
                file_name=f"recibo_vencimento_{funcionario_info['NomeCompleto'].replace(' ', '_')}_{ano_recibo}_{mes_recibo:02d}.pdf",
                mime="application/pdf",
                key="download_pdf_button"
            )

        else:
            st.warning("Por favor, selecione um funcionário para gerar o recibo de vencimento.")


# Aba: Acertos Semestrais
elif st.session_state.active_tab_index == 4:
    st.title("📈 Gestão de Acertos Semestrais")
    st.write("Registe e visualize os acertos semestrais de horas e FOTS dos funcionários.")

    with st.expander("Adicionar/Editar Acerto Semestral"):
        with st.form("acerto_semestral_form", clear_on_submit=True):
            acerto_id_edit = st.number_input("ID do Acerto (para editar, deixe 0 para adicionar novo)", min_value=0, value=0, step=1, key="acerto_id_edit")
            selected_funcionario_name_acerto = st.selectbox("Funcionário", funcionario_nomes, key="acerto_funcionario_select")
            selected_funcionario_id_acerto = funcionario_id_map.get(selected_funcionario_name_acerto)
            ano_acerto = st.number_input("Ano do Acerto", min_value=2000, value=datetime.now().year, step=1, key="acerto_ano")
            semestre_acerto = st.selectbox("Semestre", [1, 2], key="acerto_semestre")
            total_horas_normais = st.number_input("Total Horas Normais", min_value=0.0, format="%.2f", key="acerto_horas_normais")
            total_horas_extra_acumuladas = st.number_input("Total Horas Extra Acumuladas", min_value=0.0, format="%.2f", key="acerto_horas_extra_acumuladas")
            total_fots_disponiveis = st.number_input("Total FOTS Disponíveis", min_value=0, step=1, key="acerto_fots")

            submitted_acerto = st.form_submit_button("Guardar Acerto Semestral")

            if submitted_acerto:
                if selected_funcionario_id_acerto:
                    acerto_data = {
                        'FuncionarioID': selected_funcionario_id_acerto,
                        'Ano': ano_acerto,
                        'Semestre': semestre_acerto,
                        'TotalHorasNormais': total_horas_normais,
                        'TotalHorasExtraAcumuladas': total_horas_extra_acumuladas,
                        'TotalFOTSDisponiveis': total_fots_disponiveis
                    }
                    if acerto_id_edit == 0:
                        if add_acerto_semestral(acerto_data):
                            st.success("Acerto semestral adicionado com sucesso!")
                        else:
                            st.error("Erro ao adicionar acerto semestral.")
                    else:
                        if update_acerto_semestral(acerto_id_edit, acerto_data):
                            st.success(f"Acerto semestral {acerto_id_edit} atualizado com sucesso!")
                            st.session_state.active_tab_index = 4
                            st.rerun()
                        else:
                            st.error("Erro ao atualizar acerto semestral.")
                else:
                    st.warning("Por favor, selecione um funcionário.")

    st.markdown("---")
    st.subheader("Acertos Semestrais Existentes")
    acertos_semestrais_df = get_acertos_semestrais()
    if not acertos_semestrais_df.empty:
        acertos_com_nomes = pd.merge(acertos_semestrais_df, funcionarios_df[['FuncionarioID', 'NomeCompleto']], on='FuncionarioID', how='left')
        st.dataframe(acertos_com_nomes[['AcertoID', 'NomeCompleto', 'Ano', 'Semestre', 'TotalHorasNormais', 'TotalHorasExtraAcumuladas', 'TotalFOTSDisponiveis']],
                     use_container_width=True)

        st.markdown("#### Apagar Acerto Semestral")
        acerto_ids_delete = acertos_semestrais_df['AcertoID'].tolist()
        if acerto_ids_delete:
            acerto_id_to_delete = st.selectbox("Selecione o ID do acerto a apagar", acerto_ids_delete, key="delete_acerto_select")
            if st.button("Apagar Acerto Semestral", key="delete_acerto_button"):
                if delete_acerto_semestral(acerto_id_to_delete):
                    st.success(f"Acerto semestral ID {acerto_id_to_delete} apagado com sucesso!")
                    st.session_state.active_tab_index = 4
                    st.rerun()
                else:
                    st.error(f"Erro ao apagar acerto semestral ID {acerto_id_to_delete}.")
        else:
            st.info("Nenhum acerto semestral para apagar.")
    else:
        st.info("Nenhum acerto semestral encontrado.")

# Aba: Relatórios e Análises (ATUALIZADO E MELHORADO)
elif st.session_state.active_tab_index == 5:
    st.title("📋 Relatórios e Análises")
    st.write("Visualize relatórios detalhados e saldos de horas para uma gestão eficiente.")

    st.subheader("Filtros Globais de Relatório")
    col_filter_mes, col_filter_ano, col_filter_depto = st.columns(3)
    mes_relatorio_global = col_filter_mes.number_input("Mês", min_value=1, max_value=12, value=datetime.now().month, step=1, key="rel_mes_global")
    ano_relatorio_global = col_filter_ano.number_input("Ano", min_value=2000, value=datetime.now().year, step=1, key="rel_ano_global")
    selected_departamento = col_filter_depto.selectbox("Filtrar por Departamento", departamentos_unicos, key="rel_depto_global")

    # Filtrar funcionários com base no departamento selecionado
    funcionarios_filtrados_df = funcionarios_df.copy()
    if selected_departamento != 'Todos':
        funcionarios_filtrados_df = funcionarios_filtrados_df[funcionarios_filtrados_df['Departamento'] == selected_departamento]

    st.markdown("---")

    # --- Saldo de Horas Extra e Dias de Férias/Faltas/Licenças por Funcionário (para o ano atual) ---
    st.subheader(f"Saldos de Horas e Dias (Ano: {ano_relatorio_global})")
    if not funcionarios_filtrados_df.empty:
        saldos_data = []
        for index, func_row in funcionarios_filtrados_df.iterrows():
            funcionario_id = func_row['FuncionarioID']
            nome_completo = func_row['NomeCompleto']
            
            # ATUALIZADO: Garantir que DiasFeriasAnuais é um int, mesmo se for None/NaN na DB
            dias_ferias_anuais = int(func_row['DiasFeriasAnuais']) if pd.notna(func_row['DiasFeriasAnuais']) else 22 

            # Calcular Horas Extra Acumuladas
            horas_extra_acumuladas = acertos_semestrais_df[
                (acertos_semestrais_df['FuncionarioID'] == funcionario_id) &
                (acertos_semestrais_df['Ano'] == ano_relatorio_global)
            ]['TotalHorasExtraAcumuladas'].sum() if not acertos_semestrais_df.empty else 0.0

            # Contar dias de férias tirados no ano
            ferias_do_ano = ferias_df[
                (ferias_df['FuncionarioID'] == funcionario_id) &
                (pd.to_datetime(ferias_df['DataInicio']).dt.year == ano_relatorio_global)
            ]
            dias_ferias_tirados = 0
            if not ferias_do_ano.empty:
                for _, ferias_row in ferias_do_ano.iterrows():
                    # Garante que as colunas são objetos date
                    start_event = ferias_row['DataInicio'].date() if isinstance(ferias_row['DataInicio'], datetime) else ferias_row['DataInicio']
                    end_event = ferias_row['DataFim'].date() if isinstance(ferias_row['DataFim'], datetime) else ferias_row['DataFim']
                    dias_ferias_tirados += (end_event - start_event).days + 1

            dias_ferias_disponiveis = dias_ferias_anuais - dias_ferias_tirados

            # Contar dias de faltas tirados no ano (justificadas e injustificadas)
            faltas_do_ano = faltas_df[
                (faltas_df['FuncionarioID'] == funcionario_id) &
                (pd.to_datetime(faltas_df['DataFalta']).dt.year == ano_relatorio_global)
            ]
            dias_faltas_total = faltas_do_ano['DataFalta'].nunique() if not faltas_do_ano.empty else 0

            # Contar dias de licenças tiradas no ano
            licencas_do_ano = licencas_df[
                (licencas_df['FuncionarioID'] == funcionario_id) &
                (pd.to_datetime(licencas_df['DataInicio']).dt.year == ano_relatorio_global)
            ]
            dias_licencas_total = 0
            if not licencas_do_ano.empty:
                for _, licenca_row in licencas_do_ano.iterrows():
                    # Garante que as colunas são objetos date
                    start_event = licenca_row['DataInicio'].date() if isinstance(licenca_row['DataInicio'], datetime) else licenca_row['DataInicio']
                    end_event = licenca_row['DataFim'].date() if isinstance(licenca_row['DataFim'], datetime) else licenca_row['DataFim']
                    dias_licencas_total += (end_event - start_event).days + 1

            saldos_data.append({
                'Funcionário': nome_completo,
                'Departamento': func_row['Departamento'],
                'Horas Extra Acumuladas': f"{horas_extra_acumuladas:.2f}h",
                'Dias Férias Anuais (Direito)': dias_ferias_anuais,
                'Dias Férias Tirados': dias_ferias_tirados,
                'Dias Férias Disponíveis': dias_ferias_disponiveis,
                'Dias Faltas (Ano)': dias_faltas_total,
                'Dias Licença (Ano)': dias_licencas_total
            })
        saldos_df = pd.DataFrame(saldos_data)
        st.dataframe(saldos_df, use_container_width=True)

        st.download_button(
            label="Exportar Saldos (CSV)",
            data=convert_df_to_csv(saldos_df),
            file_name=f"saldos_horas_dias_{ano_relatorio_global}.csv",
            mime="text/csv",
            key="export_saldos_csv"
        )
        st.download_button(
            label="Exportar Saldos (Excel)",
            data=to_excel(saldos_df),
            file_name=f"saldos_horas_dias_{ano_relatorio_global}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="export_saldos_excel"
        )
    else:
        st.info("Nenhum funcionário encontrado para o departamento selecionado ou na base de dados.")

    st.markdown("---")

    # --- Quadro Mensal de Ocorrências (Assiduidade) ---
    st.subheader(f"Quadro Mensal de Ocorrências: {mes_relatorio_global:02d}/{ano_relatorio_global}")
    
    if st.button("Gerar Quadro Mensal", key="gerar_quadro_mensal_button"):
        if not funcionarios_filtrados_df.empty and not tipos_ocorrencia_df.empty:
            num_days_in_month = calendar.monthrange(ano_relatorio_global, mes_relatorio_global)[1]
            start_of_month = date(ano_relatorio_global, mes_relatorio_global, 1)
            end_of_month = date(ano_relatorio_global, mes_relatorio_global, num_days_in_month)

            columns_quadro = ['Funcionário'] + [f'Dia {d}' for d in range(1, num_days_in_month + 1)]
            columns_quadro.extend(['Total Horas Normais', 'Total Horas Extra', 'Total Dias Férias', 'Total Dias Faltas', 'Total Dias Licença'])
            report_data_quadro = []

            for index, func_row in funcionarios_filtrados_df.iterrows():
                funcionario_id = func_row['FuncionarioID']
                nome_completo = func_row['NomeCompleto']
                row_values = {'Funcionário': nome_completo}
                
                total_horas_normais_func = 0.0
                total_horas_extra_func = 0.0
                total_dias_ferias_func = 0
                total_dias_faltas_func = 0
                total_dias_licenca_func = 0

                registos_diarios_func, faltas_func, ferias_func, licencas_func = \
                    get_all_events_for_employee_and_period(funcionario_id, start_of_month, end_of_month)

                if not registos_diarios_func.empty: registos_diarios_func['DataRegisto'] = pd.to_datetime(registos_diarios_func['DataRegisto']).dt.date
                if not faltas_func.empty: faltas_func['DataFalta'] = pd.to_datetime(faltas_func['DataFalta']).dt.date
                if not ferias_func.empty: 
                    ferias_func['DataInicio'] = pd.to_datetime(ferias_func['DataInicio']).dt.date
                    ferias_func['DataFim'] = pd.to_datetime(ferias_func['DataFim']).dt.date
                if not licencas_func.empty: 
                    licencas_func['DataInicio'] = pd.to_datetime(licencas_func['DataInicio']).dt.date
                    licencas_func['DataFim'] = pd.to_datetime(licencas_func['DataFim']).dt.date

                for day in range(1, num_days_in_month + 1):
                    current_day_date = date(ano_relatorio_global, mes_relatorio_global, day)
                    sigla = '-'

                    is_ferias = ferias_func[(ferias_func['DataInicio'] <= current_day_date) & (ferias_func['DataFim'] >= current_day_date) & (ferias_func['Aprovado'] == True)] # Apenas aprovadas
                    if not is_ferias.empty:
                        sigla = 'F'
                        total_dias_ferias_func += 1
                    else:
                        is_licenca = licencas_func[(licencas_func['DataInicio'] <= current_day_date) & (licencas_func['DataFim'] >= current_day_date) & (licencas_func['Aprovado'] == True)] # Apenas aprovadas
                        if not is_licenca.empty:
                            sigla = 'L'
                            total_dias_licenca_func += 1
                        else:
                            is_falta = faltas_func[(faltas_func['DataFalta'] == current_day_date) & (faltas_func['Aprovado'] == True)] # Apenas aprovadas
                            if not is_falta.empty:
                                sigla = 'FJ' if is_falta['Justificada'].iloc[0] else 'FI'
                                total_dias_faltas_func += 1
                            else:
                                registo_do_dia = registos_diarios_func[registos_diarios_func['DataRegisto'] == current_day_date]
                                if not registo_do_dia.empty:
                                    reg_info = registo_do_dia.iloc[0]
                                    tipo_ocorrencia_id = reg_info['TipoOcorrenciaID']
                                    sigla = get_sigla_by_tipo_id(tipo_ocorrencia_id, tipos_ocorrencia_df)
                                    
                                    total_horas_normais_func += reg_info['HorasTrabalhadas']
                                    total_horas_extra_func += reg_info['HorasExtraDiarias']
                                    
                    row_values[f'Dia {day}'] = sigla

                row_values['Total Horas Normais'] = f"{total_horas_normais_func:.2f}"
                row_values['Total Horas Extra'] = f"{total_horas_extra_func:.2f}"
                row_values['Total Dias Férias'] = total_dias_ferias_func
                row_values['Total Dias Faltas'] = total_dias_faltas_func
                row_values['Total Dias Licença'] = total_dias_licenca_func

                report_data_quadro.append(row_values)

            report_df_quadro = pd.DataFrame(report_data_quadro, columns=columns_quadro)

            def highlight_siglas(val):
                color_map = {
                    'D': '#228B22', 'N': '#228B22', 'DT': '#90EE90', 'NT': '#90EE90', 'T': '#90EE90', 'HE': '#90EE90',
                    'DTS': '#DDA0DD', 'NTS': '#DDA0DD',
                    'F': '#FFA500', 'L': '#FFA500', 'B': '#FF0000', 'FI': '#FF0000', 'FJ': '#FF0000',
                    'FOTS': '#FFFF00', 'DDTS5': '#D2B48C', 'NDTS5': '#D2B48C', '-': ''
                }
                if isinstance(val, str) and val in color_map:
                    return f'background-color: {color_map[val]}'
                return ''

            day_columns_to_style = [col for col in report_df_quadro.columns if col.startswith('Dia')]
            styled_report_df_quadro = report_df_quadro.style.applymap(highlight_siglas, subset=day_columns_to_style)

            st.dataframe(styled_report_df_quadro, use_container_width=True)

            st.download_button(
                label="Exportar Quadro Mensal (CSV)",
                data=convert_df_to_csv(report_df_quadro),
                file_name=f"quadro_mensal_ocorrencias_{mes_relatorio_global:02d}_{ano_relatorio_global}.csv",
                mime="text/csv",
                key="export_quadro_csv"
            )
            st.download_button(
                label="Exportar Quadro Mensal (Excel)",
                data=to_excel(report_df_quadro),
                file_name=f"quadro_mensal_ocorrencias_{mes_relatorio_global:02d}_{ano_relatorio_global}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="export_quadro_excel"
            )
        else:
            st.info("Nenhum funcionário encontrado para o departamento selecionado ou na base de dados para gerar o relatório de quadro mensal.")

    st.markdown("---")

    # --- Relatórios por Tipo de Ocorrência ---
    st.subheader(f"Análise de Horas por Tipo de Ocorrência (Mês: {mes_relatorio_global:02d}/{ano_relatorio_global})")
    
    if st.button("Gerar Análise por Ocorrência", key="gerar_analise_ocorrencia_button"):
        if not funcionarios_filtrados_df.empty and not registos_diarios_df.empty and not tipos_ocorrencia_df.empty:
            start_of_month = date(ano_relatorio_global, mes_relatorio_global, 1)
            end_of_month = date(ano_relatorio_global, mes_relatorio_global, calendar.monthrange(ano_relatorio_global, mes_relatorio_global)[1])

            # Filtrar registos diários pelo período e pelos funcionários filtrados
            registos_periodo = registos_diarios_df[
                (pd.to_datetime(registos_diarios_df['DataRegisto']).dt.date >= start_of_month) &
                (pd.to_datetime(registos_diarios_df['DataRegisto']).dt.date <= end_of_month) &
                (registos_diarios_df['FuncionarioID'].isin(funcionarios_filtrados_df['FuncionarioID']))
            ]

            if not registos_periodo.empty:
                # Merge com tipos de ocorrência para obter a descrição
                registos_com_tipo = pd.merge(registos_periodo, tipos_ocorrencia_df[['TipoOcorrenciaID', 'Descricao', 'EhHorasExtra', 'EhAusencia']], # Corrigido aqui
                                             on='TipoOcorrenciaID', how='left')
                
                # Agrupar por descrição do tipo de ocorrência e somar horas
                horas_por_tipo = registos_com_tipo.groupby('Descricao').agg(
                    TotalHorasTrabalhadas=('HorasTrabalhadas', 'sum'),
                    TotalHorasExtraDiarias=('HorasExtraDiarias', 'sum'),
                    TotalHorasAusencia=('HorasAusencia', 'sum')
                ).reset_index()

                # Adicionar colunas para facilitar a leitura
                horas_por_tipo['Tipo'] = horas_por_tipo['Descricao']
                horas_por_tipo['Horas Normais'] = horas_por_tipo['TotalHorasTrabalhadas'].apply(lambda x: f"{x:.2f}")
                horas_por_tipo['Horas Extra'] = horas_por_tipo['TotalHorasExtraDiarias'].apply(lambda x: f"{x:.2f}")
                horas_por_tipo['Horas Ausência'] = horas_por_tipo['TotalHorasAusencia'].apply(lambda x: f"{x:.2f}")

                horas_por_tipo = horas_por_tipo[['Tipo', 'Horas Normais', 'Horas Extra', 'Horas Ausência']]
                st.dataframe(horas_por_tipo, use_container_width=True)

                st.download_button(
                    label="Exportar Análise por Ocorrência (CSV)",
                    data=convert_df_to_csv(horas_por_tipo),
                    file_name=f"analise_ocorrencias_{mes_relatorio_global:02d}_{ano_relatorio_global}.csv",
                    mime="text/csv",
                    key="export_ocorrencia_csv"
                )
                st.download_button(
                    label="Exportar Análise por Ocorrência (Excel)",
                    data=to_excel(horas_por_tipo),
                    file_name=f"analise_ocorrencias_{mes_relatorio_global:02d}_{ano_relatorio_global}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="export_ocorrencia_excel"
                )
            else:
                st.info("Nenhum registo diário encontrado para o período e filtros selecionados.")
        else:
            st.info("Nenhum funcionário ou registo de ocorrência encontrado para gerar esta análise.")