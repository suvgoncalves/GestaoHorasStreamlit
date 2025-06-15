import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
import io # Para to_excel

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
# ISSO DEVE ESTAR AQUI, NO INÍCIO, ANTES DE QUALQUER LEITURA DE st.session_state
if 'active_tab_index' not in st.session_state:
    st.session_state.active_tab_index = 0 # Define a aba Dashboard (índice 0) como padrão


# --- Funções de Banco de Dados e Helpers (Assumindo que estas estão definidas em outro lugar ou aqui) ---
# SUBSTITUA ESTES PLACEHOLDERS PELAS SUAS FUNÇÕES REAIS DE INTERAÇÃO COM A BASE DE DADOS!

def get_db_connection():
    # Exemplo de lógica de conexão (substitua pela sua implementação real)
    try:
        # Certifique-se de que você tem a biblioteca pyodbc instalada para SQL Server
        import pyodbc
        conn_str = (
            f"DRIVER={st.secrets['connections.sql_server']['driver']};"
            f"SERVER={st.secrets['connections.sql_server']['server']};"
            f"DATABASE={st.secrets['connections.sql_server']['database']};"
            f"UID={st.secrets['connections.sql_server']['uid']};"
            f"PWD={st.secrets['connections.sql_server']['pwd']}"
        )
        return pyodbc.connect(conn_str)
    except KeyError as e:
        st.error(f"Erro de configuração no secrets.toml: Chave '{e}' não encontrada para conexão ao DB. Verifique seu arquivo .streamlit/secrets.toml.")
        return None
    except Exception as e:
        st.error(f"Erro ao conectar à base de dados: {e}. Verifique as suas credenciais e a conectividade.")
        return None

# Funções CRUD para Funcionários (exemplos - **VOCÊ PRECISA DA SUA IMPLEMENTAÇÃO REAL**)
def get_funcionarios():
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql_query("SELECT * FROM Funcionarios", conn)
            return df
        except Exception as e:
            st.error(f"Erro ao carregar funcionários: {e}")
        finally:
            conn.close()
    return pd.DataFrame()

def add_funcionario(data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            query = f"INSERT INTO Funcionarios ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar funcionário: {e}")
            return False
        finally:
            conn.close()
    return False

def update_funcionario(id, data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            query = f"UPDATE Funcionarios SET {set_clause} WHERE FuncionarioID = ?"
            values = tuple(data.values()) + (id,)
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao atualizar funcionário: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_funcionario(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Funcionarios WHERE FuncionarioID = ?", (id,))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao apagar funcionário: {e}")
            return False
        finally:
            conn.close()
    return False

# Funções CRUD para Registos Diários (exemplos - **VOCÊ PRECISA DA SUA IMPLEMENTAÇÃO REAL**)
def get_registos_diarios():
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql_query("SELECT * FROM RegistosDiarios", conn)
            if 'DataRegisto' in df.columns:
                df['DataRegisto'] = pd.to_datetime(df['DataRegisto']).dt.date
            return df
        except Exception as e:
            st.error(f"Erro ao carregar registos diários: {e}")
        finally:
            conn.close()
    return pd.DataFrame()

def add_registo_diario(data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            query = f"INSERT INTO RegistosDiarios ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar registo diário: {e}")
            return False
        finally:
            conn.close()
    return False

def update_registo_diario(id, data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            query = f"UPDATE RegistosDiarios SET {set_clause} WHERE RegistoID = ?"
            values = tuple(data.values()) + (id,)
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao atualizar registo diário: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_registo_diario(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM RegistosDiarios WHERE RegistoID = ?", (id,))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao apagar registo diário: {e}")
            return False
        finally:
            conn.close()
    return False

# Funções CRUD para Férias (exemplos - **VOCÊ PRECISA DA SUA IMPLEMENTAÇÃO REAL**)
def get_ferias():
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql_query("SELECT * FROM Ferias", conn)
            if 'DataInicio' in df.columns: df['DataInicio'] = pd.to_datetime(df['DataInicio']).dt.date
            if 'DataFim' in df.columns: df['DataFim'] = pd.to_datetime(df['DataFim']).dt.date
            return df
        except Exception as e:
            st.error(f"Erro ao carregar férias: {e}")
        finally:
            conn.close()
    return pd.DataFrame()

def add_ferias(data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            query = f"INSERT INTO Ferias ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar férias: {e}")
            return False
        finally:
            conn.close()
    return False

def update_ferias(id, data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            query = f"UPDATE Ferias SET {set_clause} WHERE FeriasID = ?"
            values = tuple(data.values()) + (id,)
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao atualizar férias: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_ferias(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Ferias WHERE FeriasID = ?", (id,))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao apagar férias: {e}")
            return False
        finally:
            conn.close()
    return False

# Funções CRUD para Faltas (exemplos - **VOCÊ PRECISA DA SUA IMPLEMENTAÇÃO REAL**)
def get_faltas():
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql_query("SELECT * FROM Faltas", conn)
            if 'DataFalta' in df.columns: df['DataFalta'] = pd.to_datetime(df['DataFalta']).dt.date
            return df
        except Exception as e:
            st.error(f"Erro ao carregar faltas: {e}")
        finally:
            conn.close()
    return pd.DataFrame()

def add_falta(data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            query = f"INSERT INTO Faltas ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar falta: {e}")
            return False
        finally:
            conn.close()
    return False

def update_falta(id, data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            query = f"UPDATE Faltas SET {set_clause} WHERE FaltaID = ?"
            values = tuple(data.values()) + (id,)
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao atualizar falta: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_falta(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Faltas WHERE FaltaID = ?", (id,))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao apagar falta: {e}")
            return False
        finally:
            conn.close()
    return False

# Funções CRUD para Licenças (exemplos - **VOCÊ PRECISA DA SUA IMPLEMENTAÇÃO REAL**)
def get_licencas():
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql_query("SELECT * FROM Licencas", conn)
            if 'DataInicio' in df.columns: df['DataInicio'] = pd.to_datetime(df['DataInicio']).dt.date
            if 'DataFim' in df.columns: df['DataFim'] = pd.to_datetime(df['DataFim']).dt.date
            return df
        except Exception as e:
            st.error(f"Erro ao carregar licenças: {e}")
        finally:
            conn.close()
    return pd.DataFrame()

def add_licenca(data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            query = f"INSERT INTO Licencas ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar licença: {e}")
            return False
        finally:
            conn.close()
    return False

def update_licenca(id, data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            query = f"UPDATE Licencas SET {set_clause} WHERE LicencaID = ?"
            values = tuple(data.values()) + (id,)
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao atualizar licença: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_licenca(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Licencas WHERE LicencaID = ?", (id,))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao apagar licença: {e}")
            return False
        finally:
            conn.close()
    return False

# Funções CRUD para Tipos de Ocorrência (exemplos - **VOCÊ PRECISA DA SUA IMPLEMENTAÇÃO REAL**)
def get_tipos_ocorrencia():
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql_query("SELECT * FROM TiposOcorrencia", conn)
            return df
        except Exception as e:
            st.error(f"Erro ao carregar tipos de ocorrência: {e}")
        finally:
            conn.close()
    return pd.DataFrame()

def add_tipo_ocorrencia(data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            query = f"INSERT INTO TiposOcorrencia ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar tipo de ocorrência: {e}")
            return False
        finally:
            conn.close()
    return False

def update_tipo_ocorrencia(id, data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            query = f"UPDATE TiposOcorrencia SET {set_clause} WHERE TipoOcorrenciaID = ?"
            values = tuple(data.values()) + (id,)
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao atualizar tipo de ocorrência: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_tipo_ocorrencia(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM TiposOcorrencia WHERE TipoOcorrenciaID = ?", (id,))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao apagar tipo de ocorrência: {e}")
            return False
        finally:
            conn.close()
    return False

def get_sigla_by_tipo_id(tipo_id, tipos_ocorrencia_df):
    if not tipos_ocorrencia_df.empty and tipo_id in tipos_ocorrencia_df['TipoOcorrenciaID'].values:
        return tipos_ocorrencia_df[tipos_ocorrencia_df['TipoOcorrenciaID'] == tipo_id]['Sigla'].iloc[0]
    return '?' # Sigla padrão se não encontrar

# Funções CRUD para Acertos Semestrais (exemplos - **VOCÊ PRECISA DA SUA IMPLEMENTAÇÃO REAL**)
def get_acertos_semestrais():
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql_query("SELECT * FROM AcertosSemestrais", conn)
            return df
        except Exception as e:
            st.error(f"Erro ao carregar acertos semestrais: {e}")
        finally:
            conn.close()
    return pd.DataFrame()

def add_acerto_semestral(data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            query = f"INSERT INTO AcertosSemestrais ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao adicionar acerto semestral: {e}")
            return False
        finally:
            conn.close()
    return False

def update_acerto_semestral(id, data):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            query = f"UPDATE AcertosSemestrais SET {set_clause} WHERE AcertoID = ?"
            values = tuple(data.values()) + (id,)
            cursor.execute(query, values)
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao atualizar acerto semestral: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_acerto_semestral(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM AcertosSemestrais WHERE AcertoID = ?", (id,))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Erro ao apagar acerto semestral: {e}")
            return False
        finally:
            conn.close()
    return False


# Função para buscar todos os eventos para um funcionário e período
def get_all_events_for_employee_and_period(funcionario_id, start_date, end_date):
    registos_diarios_df = get_registos_diarios()
    faltas_df = get_faltas()
    ferias_df = get_ferias()
    licencas_df = get_licencas()

    registos_diarios_mes = registos_diarios_df[
        (registos_diarios_df['FuncionarioID'] == funcionario_id) &
        (pd.to_datetime(registos_diarios_df['DataRegisto']).dt.date >= start_date) &
        (pd.to_datetime(registos_diarios_df['DataRegisto']).dt.date <= end_date)
    ]
    faltas_mes = faltas_df[
        (faltas_df['FuncionarioID'] == funcionario_id) &
        (pd.to_datetime(faltas_df['DataFalta']).dt.date >= start_date) &
        (pd.to_datetime(faltas_df['DataFalta']).dt.date <= end_date)
    ]
    ferias_mes = ferias_df[
        (ferias_df['FuncionarioID'] == funcionario_id) &
        (pd.to_datetime(ferias_df['DataInicio']).dt.date <= end_date) &
        (pd.to_datetime(ferias_df['DataFim']).dt.date >= start_date) &
        (ferias_df['Aprovado'] == True)
    ]
    licencas_mes = licencas_df[
        (licencas_df['FuncionarioID'] == funcionario_id) &
        (pd.to_datetime(licencas_df['DataInicio']).dt.date <= end_date) &
        (pd.to_datetime(licencas_df['DataFim']).dt.date >= start_date) &
        (licencas_df['Aprovado'] == True)
    ]
    return registos_diarios_mes, faltas_mes, ferias_mes, licencas_mes

# Função para gerar PDF (Exemplo, você precisa da implementação real do ReportLab)
def generate_payslip_pdf(funcionario_info, mes_recibo, ano_recibo,
                          total_horas_trabalhadas_mes, total_horas_extra_mes,
                          salario_base_mensal, valor_horas_extra,
                          subsidio_alimentacao, vencimento_bruto,
                          desconto_irs, taxa_irs, desconto_ss, taxa_seguranca_social_funcionario,
                          total_horas_ausencia_geral, desconto_ausencia, salario_liquido,
                          dias_ferias_mes, dias_licencas_mes):
    st.error("Placeholder: generate_payslip_pdf precisa ser implementada com ReportLab!")
    # Retorna um objeto BytesIO vazio para evitar erro, na implementação real seria o PDF
    return io.BytesIO(b"PDF Content Placeholder")

# Funções de conversão para download
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

@st.cache_data
def to_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data


# --- Configuração da Página Streamlit ---
st.set_page_config(layout="wide", page_title="Gestão de RH e Assiduidade")

# --- Carregar Dados Iniciais (com tratamento de erro) ---
# Tenta carregar dados; se falhar, retorna DataFrame vazio
funcionarios_df = get_funcionarios()
registos_diarios_df = get_registos_diarios()
ferias_df = get_ferias()
faltas_df = get_faltas()
licencas_df = get_licencas()
tipos_ocorrencia_df = get_tipos_ocorrencia()
acertos_semestrais_df = get_acertos_semestrais()

# Gerar listas para selectbox e maps
funcionario_nomes = ['Selecione um Funcionário']
funcionario_id_map = {}
if not funcionarios_df.empty:
    funcionario_nomes.extend(funcionarios_df['NomeCompleto'].tolist())
    funcionario_id_map = pd.Series(funcionarios_df.FuncionarioID.values, index=funcionarios_df.NomeCompleto).to_dict()

departamentos_unicos = ['Todos']
if not funcionarios_df.empty:
    departamentos_unicos.extend(funcionarios_df['Departamento'].dropna().unique().tolist())


# --- Sidebar para Navegação ---
st.sidebar.title("Navegação")
tabs = ["Dashboard", "Gestão de Funcionários", "Registos de Presença", "Gerar Recibo de Vencimento", "Acertos Semestrais", "Relatórios e Análises", "Configurações"]
selected_tab = st.sidebar.radio("Ir para", tabs, index=st.session_state.active_tab_index, key="main_navigation")

# Atualiza o índice da aba na sessão (isso deve vir depois do radio, globalmente)
st.session_state.active_tab_index = tabs.index(selected_tab)

# --- Conteúdo Principal ---

# Aba: Dashboard
if st.session_state.active_tab_index == 0:
    st.title("📊 Dashboard")
    st.write("Bem-vindo ao sistema de Gestão de RH e Assiduidade!")

    st.markdown("---")
    st.subheader("Resumo Geral")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Funcionários", funcionarios_df.shape[0] if not funcionarios_df.empty else 0)

    funcionarios_com_registos = registos_diarios_df['FuncionarioID'].nunique() if not registos_diarios_df.empty else 0
    col2.metric("Funcionários com Registos (Este Mês)", funcionarios_com_registos)

    ferias_pendentes = ferias_df[(ferias_df['Aprovado'] == False)].shape[0] if not ferias_df.empty else 0
    col3.metric("Férias Pendentes de Aprovação", ferias_pendentes)

    st.markdown("---")
    st.subheader("Atividade Recente (Últimos 7 dias)")
    end_date_recent = date.today()
    start_date_recent = end_date_recent - pd.Timedelta(days=7).date()

    recent_registos = registos_diarios_df[
        (registos_diarios_df['DataRegisto'] >= start_date_recent) &
        (registos_diarios_df['DataRegisto'] <= end_date_recent)
    ]
    if not recent_registos.empty:
        st.write(f"**Registos Diários de {start_date_recent} a {end_date_recent}:**")
        st.dataframe(recent_registos[['DataRegisto', 'FuncionarioID', 'HorasTrabalhadas', 'HorasExtraDiarias', 'Observacoes']], use_container_width=True)
    else:
        st.info("Nenhum registo diário nos últimos 7 dias.")

    recent_faltas = faltas_df[
        (faltas_df['DataFalta'] >= start_date_recent) &
        (faltas_df['DataFalta'] <= end_date_recent)
    ]
    if not recent_faltas.empty:
        st.write(f"**Faltas de {start_date_recent} a {end_date_recent}:**")
        st.dataframe(recent_faltas[['DataFalta', 'FuncionarioID', 'Motivo', 'Justificada', 'Aprovado']], use_container_width=True)
    else:
        st.info("Nenhuma falta registada nos últimos 7 dias.")


# Aba: Gestão de Funcionários
elif st.session_state.active_tab_index == 1:
    st.title("👥 Gestão de Funcionários")
    st.write("Adicione, edite ou apague informações dos funcionários.")

    with st.expander("Adicionar/Editar Funcionário"):
        with st.form("funcionario_form", clear_on_submit=True):
            funcionario_id_edit = st.number_input("ID do Funcionário (para editar, deixe 0 para adicionar novo)", min_value=0, value=0, step=1, key="func_id_edit")
            nome_completo = st.text_input("Nome Completo", key="func_nome")
            data_nascimento = st.date_input("Data de Nascimento", datetime.now(), key="func_data_nasc")
            genero = st.selectbox("Género", ["Masculino", "Feminino", "Outro"], key="func_genero")
            nacionalidade = st.text_input("Nacionalidade", key="func_nacionalidade")
            morada = st.text_area("Morada", key="func_morada")
            contacto_telefonico = st.text_input("Contacto Telefónico", key="func_contacto")
            email = st.text_input("Email", key="func_email")
            nif = st.text_input("NIF", max_chars=9, key="func_nif")
            niss = st.text_input("NISS", max_chars=11, key="func_niss")
            data_contratacao = st.date_input("Data de Contratação", datetime.now(), key="func_data_cont")
            cargo = st.text_input("Cargo", key="func_cargo")
            departamento = st.text_input("Departamento", key="func_depto")
            salario_base_mensal = st.number_input("Salário Base Mensal (€)", min_value=0.0, format="%.2f", key="func_salario")
            valor_subsidio_alimentacao_diario = st.number_input("Valor Subsídio Alimentação Diário (€)", min_value=0.0, format="%.2f", key="func_sub_ali")
            dias_ferias_anuais = st.number_input("Dias de Férias Anuais (Direito)", min_value=0, step=1, key="func_dias_ferias")
            taxa_irs = st.number_input("Taxa IRS (%)", min_value=0.0, max_value=100.0, format="%.2f", key="func_irs") / 100
            taxa_seguranca_social_funcionario = st.number_input("Taxa Segurança Social Funcionário (%)", min_value=0.0, max_value=100.0, format="%.2f", key="func_ss") / 100
            horas_trabalho_mensal_padrao = st.number_input("Horas de Trabalho Mensal Padrão", min_value=0.0, format="%.2f", key="func_horas_padrao")

            submitted_func = st.form_submit_button("Guardar Funcionário")

            if submitted_func:
                if not nome_completo or not cargo or not departamento:
                    st.error("Nome, Cargo e Departamento são campos obrigatórios.")
                else:
                    func_data = {
                        'NomeCompleto': nome_completo,
                        'DataNascimento': data_nascimento,
                        'Genero': genero,
                        'Nacionalidade': nacionalidade,
                        'Morada': morada,
                        'ContactoTelefonico': contacto_telefonico,
                        'Email': email,
                        'NIF': nif,
                        'NISS': niss,
                        'DataContratacao': data_contratacao,
                        'Cargo': cargo,
                        'Departamento': departamento,
                        'SalarioBaseMensal': salario_base_mensal,
                        'ValorSubsidioAlimentacaoDiario': valor_subsidio_alimentacao_diario,
                        'DiasFeriasAnuais': int(dias_ferias_anuais),
                        'TaxaIRS': taxa_irs,
                        'TaxaSegurancaSocialFuncionario': taxa_seguranca_social_funcionario,
                        'HorasTrabalhoMensalPadrao': horas_trabalho_mensal_padrao
                    }
                    if funcionario_id_edit == 0:
                        if add_funcionario(func_data):
                            st.success("Funcionário adicionado com sucesso!")
                        else:
                            st.error("Erro ao adicionar funcionário.")
                    else:
                        if update_funcionario(funcionario_id_edit, func_data):
                            st.success(f"Funcionário {funcionario_id_edit} atualizado com sucesso!")
                        else:
                            st.error("Erro ao atualizar funcionário.")
                    st.session_state.active_tab_index = 1 # Manter na aba de funcionários
                    st.rerun()

    st.markdown("---")
    st.subheader("Funcionários Existentes")
    funcionarios_df = get_funcionarios() # Recarrega dados
    if not funcionarios_df.empty:
        st.dataframe(funcionarios_df[['FuncionarioID', 'NomeCompleto', 'Cargo', 'Departamento', 'Email', 'ContactoTelefonico']], use_container_width=True)

        st.markdown("#### Apagar Funcionário")
        funcionario_ids_delete = funcionarios_df['FuncionarioID'].tolist()
        if funcionario_ids_delete:
            funcionario_id_to_delete = st.selectbox("Selecione o ID do funcionário a apagar", funcionario_ids_delete, key="delete_func_select")
            if st.button("Apagar Funcionário", key="delete_func_button"):
                if delete_funcionario(funcionario_id_to_delete):
                    st.success(f"Funcionário ID {funcionario_id_to_delete} apagado com sucesso!")
                    st.session_state.active_tab_index = 1
                    st.rerun()
                else:
                    st.error(f"Erro ao apagar funcionário ID {funcionario_id_to_delete}. Pode haver registos dependentes.")
        else:
            st.info("Nenhum funcionário para apagar.")
    else:
        st.info("Nenhum funcionário registado.")

# Aba: Registos de Presença
elif st.session_state.active_tab_index == 2:
    st.title("⏰ Registos de Presença")
    st.write("Gerencie os registos diários, férias, faltas e licenças dos funcionários.")

    registro_type = st.radio(
        "Selecione o Tipo de Registo:",
        ["Registo Diário", "Férias", "Faltas", "Licenças", "Tipos de Ocorrência"],
        key="registro_type_select"
    )

    # --- Gestão de Registo Diário ---
    if registro_type == "Registo Diário":
        st.subheader("Gestão de Registo Diário")
        st.info("Registe as horas trabalhadas, extras e ausências diárias.")

        with st.expander("Adicionar/Editar Registo Diário"):
            with st.form("registo_diario_form", clear_on_submit=True):
                registo_id_edit = st.number_input("ID do Registo (para editar, deixe 0 para adicionar novo)", min_value=0, value=0, step=1, key="rd_id_edit")
                selected_funcionario_name_rd = st.selectbox("Funcionário", funcionario_nomes, key="rd_funcionario_select")
                selected_funcionario_id_rd = funcionario_id_map.get(selected_funcionario_name_rd)
                data_registo = st.date_input("Data do Registo", datetime.now(), key="rd_data_registo")

                # Filtrar tipos de ocorrência para o selectbox
                tipos_ocorrencia_para_select = ['Selecione um Tipo']
                tipo_ocorrencia_map = {}
                if not tipos_ocorrencia_df.empty:
                    tipos_ocorrencia_para_select.extend(tipos_ocorrencia_df['Descricao'].tolist())
                    tipo_ocorrencia_map = pd.Series(tipos_ocorrencia_df.TipoOcorrenciaID.values, index=tipos_ocorrencia_df.Descricao).to_dict()

                selected_tipo_ocorrencia_desc = st.selectbox("Tipo de Ocorrência", tipos_ocorrencia_para_select, key="rd_tipo_ocorrencia_select")
                tipo_ocorrencia_id = tipo_ocorrencia_map.get(selected_tipo_ocorrencia_desc)


                horas_trabalhadas = st.number_input("Horas Trabalhadas", min_value=0.0, format="%.2f", key="rd_horas_trab")
                horas_extra_diarias = st.number_input("Horas Extra Diárias", min_value=0.0, format="%.2f", key="rd_horas_extra")
                horas_ausencia = st.number_input("Horas de Ausência (se aplicável)", min_value=0.0, format="%.2f", key="rd_horas_ausencia")
                observacoes_rd = st.text_area("Observações (Registo Diário)", key="rd_observacoes")

                submitted_rd = st.form_submit_button("Guardar Registo Diário")

                if submitted_rd:
                    if selected_funcionario_id_rd is None or selected_funcionario_name_rd == 'Selecione um Funcionário':
                        st.error("Por favor, selecione um funcionário.")
                    elif tipo_ocorrencia_id is None or selected_tipo_ocorrencia_desc == 'Selecione um Tipo':
                        st.error("Por favor, selecione um tipo de ocorrência.")
                    else:
                        rd_data = {
                            'FuncionarioID': selected_funcionario_id_rd,
                            'DataRegisto': data_registo,
                            'TipoOcorrenciaID': tipo_ocorrencia_id,
                            'HorasTrabalhadas': horas_trabalhadas,
                            'HorasExtraDiarias': horas_extra_diarias,
                            'HorasAusencia': horas_ausencia,
                            'Observacoes': observacoes_rd
                        }
                        if registo_id_edit == 0:
                            if add_registo_diario(rd_data):
                                st.success("Registo diário adicionado com sucesso!")
                            else:
                                st.error("Erro ao adicionar registo diário.")
                        else:
                            if update_registo_diario(registo_id_edit, rd_data):
                                st.success(f"Registo diário {registo_id_edit} atualizado com sucesso!")
                            else:
                                st.error("Erro ao atualizar registo diário.")
                        st.session_state.active_tab_index = 2
                        st.rerun()

        st.markdown("---")
        st.subheader("Registos Diários Existentes")
        registos_diarios_df = get_registos_diarios() # Recarrega dados
        if not registos_diarios_df.empty:
            registos_com_nomes = pd.merge(registos_diarios_df, funcionarios_df[['FuncionarioID', 'NomeCompleto']], on='FuncionarioID', how='left')
            registos_com_nomes = pd.merge(registos_com_nomes, tipos_ocorrencia_df[['TipoOcorrenciaID', 'Descricao']], on='TipoOcorrenciaID', how='left')
            cols_to_display_rd = ['RegistoID', 'NomeCompleto', 'DataRegisto', 'Descricao', 'HorasTrabalhadas', 'HorasExtraDiarias', 'HorasAusencia']
            if 'Observacoes' in registos_com_nomes.columns:
                cols_to_display_rd.append('Observacoes')
            st.dataframe(registos_com_nomes[cols_to_display_rd], use_container_width=True)

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

    # --- Gestão de Férias ---
    elif registro_type == "Férias":
        st.subheader("Gestão de Férias")
        st.info("Registe e aprove os períodos de férias dos funcionários.")

        with st.expander("Adicionar/Editar Registo de Férias"):
            with st.form("ferias_form", clear_on_submit=True):
                ferias_id_edit = st.number_input("ID das Férias (para editar, deixe 0 para adicionar novo)", min_value=0, value=0, step=1, key="ferias_id_edit")
                selected_funcionario_name_ferias = st.selectbox("Funcionário", funcionario_nomes, key="ferias_funcionario_select")
                selected_funcionario_id_ferias = funcionario_id_map.get(selected_funcionario_name_ferias)
                data_inicio_ferias = st.date_input("Data de Início", datetime.now(), key="ferias_data_inicio")
                data_fim_ferias = st.date_input("Data de Fim", datetime.now(), key="ferias_data_fim")
                observacoes_ferias = st.text_area("Observações (Férias)", key="ferias_observacoes")
                aprovado_ferias = st.checkbox("Aprovado", key="ferias_aprovado")

                submitted_ferias = st.form_submit_button("Guardar Registo de Férias")

                if submitted_ferias:
                    if selected_funcionario_id_ferias is None or selected_funcionario_name_ferias == 'Selecione um Funcionário':
                        st.error("Por favor, selecione um funcionário.")
                    elif data_inicio_ferias > data_fim_ferias:
                        st.error("A data de início não pode ser posterior à data de fim.")
                    else:
                        ferias_data = {
                            'FuncionarioID': selected_funcionario_id_ferias,
                            'DataInicio': data_inicio_ferias,
                            'DataFim': data_fim_ferias,
                            'Observacoes': observacoes_ferias,
                            'Aprovado': aprovado_ferias
                        }
                        if ferias_id_edit == 0:
                            if add_ferias(ferias_data):
                                st.success("Registo de férias adicionado com sucesso!")
                            else:
                                st.error("Erro ao adicionar registo de férias.")
                        else:
                            if update_ferias(ferias_id_edit, ferias_data):
                                st.success(f"Registo de férias {ferias_id_edit} atualizado com sucesso!")
                            else:
                                st.error("Erro ao atualizar registo de férias.")
                        st.session_state.active_tab_index = 2
                        st.rerun()

        st.markdown("---")
        st.subheader("Registos de Férias Existentes")
        ferias_df = get_ferias() # Recarrega dados
        if not ferias_df.empty:
            ferias_com_nomes = pd.merge(ferias_df, funcionarios_df[['FuncionarioID', 'NomeCompleto']], on='FuncionarioID', how='left')
            cols_to_display_ferias = ['FeriasID', 'NomeCompleto', 'DataInicio', 'DataFim', 'Aprovado'] # Exibir Aprovado
            if 'Observacoes' in ferias_com_nomes.columns:
                cols_to_display_ferias.append('Observacoes')
            st.dataframe(ferias_com_nomes[cols_to_display_ferias], use_container_width=True)

            st.markdown("#### Apagar Registo de Férias")
            ferias_ids_delete = ferias_df['FeriasID'].tolist()
            if ferias_ids_delete:
                ferias_id_to_delete = st.selectbox("Selecione o ID das férias a apagar", ferias_ids_delete, key="delete_ferias_select")
                if st.button("Apagar Férias", key="delete_ferias_button"):
                    if delete_ferias(ferias_id_to_delete):
                        st.success(f"Registo de férias ID {ferias_id_to_delete} apagado com sucesso!")
                        st.session_state.active_tab_index = 2
                        st.rerun()
                    else:
                        st.error(f"Erro ao apagar registo de férias ID {ferias_id_to_delete}.")
            else:
                st.info("Nenhum registo de férias para apagar.")
        else:
            st.info("Nenhum registo de férias encontrado.")

    # --- Gestão de Faltas ---
    elif registro_type == "Faltas":
        st.subheader("Gestão de Faltas")
        st.info("Registe e gerencie as faltas dos funcionários.")

        with st.expander("Adicionar/Editar Registo de Falta"):
            with st.form("falta_form", clear_on_submit=True):
                falta_id_edit = st.number_input("ID da Falta (para editar, deixe 0 para adicionar nova)", min_value=0, value=0, step=1, key="falta_id_edit")
                selected_funcionario_name_falta = st.selectbox("Funcionário", funcionario_nomes, key="falta_funcionario_select")
                selected_funcionario_id_falta = funcionario_id_map.get(selected_funcionario_name_falta)
                data_falta = st.date_input("Data da Falta", datetime.now(), key="falta_data_falta")
                motivo_falta = st.text_area("Motivo da Falta", key="falta_motivo")
                justificada_falta = st.checkbox("Justificada", key="falta_justificada")
                horas_ausencia_falta = st.number_input("Horas de Ausência pela Falta", min_value=0.0, format="%.2f", key="falta_horas_ausencia")
                aprovado_falta = st.checkbox("Aprovado", key="falta_aprovado")


                submitted_falta = st.form_submit_button("Guardar Registo de Falta")

                if submitted_falta:
                    if selected_funcionario_id_falta is None or selected_funcionario_name_falta == 'Selecione um Funcionário':
                        st.error("Por favor, selecione um funcionário.")
                    else:
                        falta_data = {
                            'FuncionarioID': selected_funcionario_id_falta,
                            'DataFalta': data_falta,
                            'Motivo': motivo_falta,
                            'Justificada': justificada_falta,
                            'HorasAusenciaFalta': horas_ausencia_falta,
                            'Aprovado': aprovado_falta
                        }
                        if falta_id_edit == 0:
                            if add_falta(falta_data):
                                st.success("Registo de falta adicionado com sucesso!")
                            else:
                                st.error("Erro ao adicionar registo de falta.")
                        else:
                            if update_falta(falta_id_edit, falta_data):
                                st.success(f"Registo de falta {falta_id_edit} atualizado com sucesso!")
                            else:
                                st.error("Erro ao atualizar registo de falta.")
                        st.session_state.active_tab_index = 2
                        st.rerun()

        st.markdown("---")
        st.subheader("Registos de Faltas Existentes")
        faltas_df = get_faltas() # Recarrega dados
        if not faltas_df.empty:
            faltas_com_nomes = pd.merge(faltas_df, funcionarios_df[['FuncionarioID', 'NomeCompleto']], on='FuncionarioID', how='left')
            cols_to_display_falta = ['FaltaID', 'NomeCompleto', 'DataFalta', 'Motivo', 'Justificada', 'HorasAusenciaFalta', 'Aprovado'] # Exibir Aprovado
            st.dataframe(faltas_com_nomes[cols_to_display_falta], use_container_width=True)

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

    # --- Gestão de Licenças ---
    elif registro_type == "Licenças":
        st.subheader("Gestão de Licenças")
        st.info("Registe e gerencie as licenças dos funcionários.")

        with st.expander("Adicionar/Editar Registo de Licença"):
            with st.form("licenca_form", clear_on_submit=True):
                licenca_id_edit = st.number_input("ID da Licença (para editar, deixe 0 para adicionar nova)", min_value=0, value=0, step=1, key="licenca_id_edit")
                selected_funcionario_name_licenca = st.selectbox("Funcionário", funcionario_nomes, key="licenca_funcionario_select")
                selected_funcionario_id_licenca = funcionario_id_map.get(selected_funcionario_name_licenca)
                data_inicio_licenca = st.date_input("Data de Início", datetime.now(), key="licenca_data_inicio")
                data_fim_licenca = st.date_input("Data de Fim", datetime.now(), key="licenca_data_fim")
                motivo_licenca = st.text_area("Motivo da Licença", key="licenca_motivo")
                observacoes_licenca = st.text_area("Observações (Licença)", key="licenca_observacoes")
                aprovado_licenca = st.checkbox("Aprovado", key="licenca_aprovado")

                submitted_licenca = st.form_submit_button("Guardar Registo de Licença")

                if submitted_licenca:
                    if selected_funcionario_id_licenca is None or selected_funcionario_name_licenca == 'Selecione um Funcionário':
                        st.error("Por favor, selecione um funcionário.")
                    elif data_inicio_licenca > data_fim_licenca:
                        st.error("A data de início não pode ser posterior à data de fim.")
                    else:
                        licenca_data = {
                            'FuncionarioID': selected_funcionario_id_licenca,
                            'DataInicio': data_inicio_licenca,
                            'DataFim': data_fim_licenca,
                            'Motivo': motivo_licenca,
                            'Observacoes': observacoes_licenca,
                            'Aprovado': aprovado_licenca
                        }
                        if licenca_id_edit == 0:
                            if add_licenca(licenca_data):
                                st.success("Registo de licença adicionado com sucesso!")
                            else:
                                st.error("Erro ao adicionar registo de licença.")
                        else:
                            if update_licenca(licenca_id_edit, licenca_data):
                                st.success(f"Registo de licença {licenca_id_edit} atualizado com sucesso!")
                            else:
                                st.error("Erro ao atualizar registo de licença.")
                        st.session_state.active_tab_index = 2
                        st.rerun()

        st.markdown("---")
        st.subheader("Registos de Licenças Existentes")
        licencas_df = get_licencas() # Recarrega dados
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
            tipo_ids_delete = tipos_ocorrencia_df['TipoOcorrenciaID'].tolist()
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
            taxa_hora_extra_50 = float(funcionario_info['TaxaHoraExtra50']) if 'TaxaHoraExtra50' in funcionario_info else 0.50 # Adicione estas colunas ao seu DB/DataFrame
            taxa_hora_extra_100 = float(funcionario_info['TaxaHoraExtra100']) if 'TaxaHoraExtra100' in funcionario_info else 1.00 # Adicione estas colunas ao seu DB/DataFrame

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
                if selected_funcionario_id_acerto is None or selected_funcionario_name_acerto == 'Selecione um Funcionário':
                    st.warning("Por favor, selecione um funcionário.")
                else:
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
                registos_com_tipo = pd.merge(registos_periodo, tipos_ocorrencia_df[['TipoOcorrenciaID', 'Descricao', 'EhHorasExtra', 'EhAusencia']],
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


# Aba: Configurações
elif st.session_state.active_tab_index == 6:
    st.title("⚙️ Configurações")
    st.write("Ajuste as configurações gerais do sistema aqui.")

    st.markdown("#### Gestão de Utilizadores (Funcionalidade Futura)")
    st.info("Esta secção permitirá gerir utilizadores, permissões e roles no futuro.")