import pandas as pd
import pyodbc
import os

# --- Configurações da Base de Dados ---
# Ajusta estas variáveis de acordo com a tua configuração
DB_SERVER = 'SusanaGonçalves\\SQLEXPRESS'
DB_DATABASE = 'GestaoHoras'
DB_DRIVER = '{ODBC Driver 17 for SQL Server}' # Verifica se é a versão correta instalada

# --- Caminho para o teu ficheiro CSV ---
# Certifica-te que este caminho está CORRETO e que o ficheiro existe
# Podes usar r'C:\Users\subgrj\OneDrive\Ambiente de Trabalho\NIF NISS.csv'
# ou os.path.join para portabilidade
csv_file_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Ambiente de Trabalho", "NIF NISS.csv")
# O os.path.expanduser("~") resolve para o teu diretório de utilizador, como C:\Users\subgrj

print(f"Caminho do CSV: {csv_file_path}") # Para debugging

def get_db_connection_script():
    """Tenta estabelecer uma conexão com a base de dados."""
    try:
        conn = pyodbc.connect(
            f'DRIVER={DB_DRIVER};'
            f'SERVER={DB_SERVER};'
            f'DATABASE={DB_DATABASE};'
            f'Trusted_Connection=yes;'
        )
        print("Conexão à base de dados estabelecida com sucesso!")
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"ERRO DE CONEXÃO À BASE DE DADOS (SQLSTATE: {sqlstate}): {ex}")
        return None

def update_nif_niss_from_csv(csv_path):
    """
    Lê um ficheiro CSV e atualiza as colunas NIF e NISS na tabela Funcionarios.
    """
    if not os.path.exists(csv_path):
        print(f"Erro: O ficheiro CSV não foi encontrado em '{csv_path}'.")
        return

    try:
        # 1. Carregar dados do CSV
        # Usamos 'sep=;' porque é comum CSVs portugueses usarem ponto e vírgula
        # Se o teu CSV usa vírgula, muda para sep=','
        df_csv = pd.read_csv(csv_path, sep=';', dtype={'NIF': str, 'NISS': str})
        
        # Opcional: Visualizar as primeiras linhas do DataFrame carregado
        print("\nDados carregados do CSV (primeiras 5 linhas):")
        print(df_csv.head())
        print(f"Colunas no CSV: {df_csv.columns.tolist()}")

        # 2. Validar que as colunas essenciais existem no CSV
        required_columns = ['FuncionarioID', 'NIF', 'NISS']
        if not all(col in df_csv.columns for col in required_columns):
            print(f"Erro: O CSV deve conter as colunas {required_columns}.")
            return

        # 3. Conectar à base de dados SQL Server
        cnxn = get_db_connection_script()
        if cnxn is None:
            print("Não foi possível estabelecer conexão com a base de dados. Abortando a atualização.")
            return

        cursor = cnxn.cursor()
        
        # 4. Iterar sobre as linhas do DataFrame e atualizar no SQL Server
        update_count = 0
        total_rows = len(df_csv)

        print(f"\nIniciando atualização de {total_rows} registos...")

        for index, row in df_csv.iterrows():
            try:
                funcionario_id = int(row['FuncionarioID'])
                nif = str(row['NIF']).strip() # .strip() para remover espaços em branco
                niss = str(row['NISS']).strip()

                # Previne NIF/NISS vazios ou 'nan' (Not a Number de pandas)
                if pd.isna(nif) or nif.lower() == 'nan':
                    nif = "" # Ou gerar um fictício se preferires
                if pd.isna(niss) or niss.lower() == 'nan':
                    niss = "" # Ou gerar um fictício se preferires
                
                # Opcional: Se o NIF ou NISS for para ser gerado fictício caso esteja vazio no CSV
                # if not nif: nif = "NIF_FICTICIO_" + str(funcionario_id)
                # if not niss: niss = "NISS_FICTICIO_" + str(funcionario_id)

                sql_update = """
                    UPDATE dbo.Funcionarios
                    SET NIF = ?, NISS = ?
                    WHERE FuncionarioID = ?;
                """
                cursor.execute(sql_update, nif, niss, funcionario_id)
                update_count += 1
                
                if (index + 1) % 10 == 0: # Imprime progresso a cada 10 linhas
                    print(f"  Progresso: {update_count}/{total_rows} registos processados.")

            except ValueError as ve:
                print(f"Erro de valor na linha {index+2} do CSV: {ve}. Linha: {row.to_dict()}")
            except Exception as e:
                print(f"Erro ao processar linha {index+2} (ID: {row.get('FuncionarioID', 'N/A')}): {e}")

        cnxn.commit() # Confirma as alterações na base de dados
        print(f"\n{update_count} registos atualizados com sucesso na tabela dbo.Funcionarios.")

    except pd.errors.EmptyDataError:
        print(f"Erro: O ficheiro CSV '{csv_path}' está vazio.")
    except pd.errors.ParserError as pe:
        print(f"Erro ao analisar o CSV: {pe}. Verifique o delimitador de colunas e o formato.")
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Erro de Base de Dados (SQLSTATE: {sqlstate}): {ex}")
        cnxn.rollback() # Reverte em caso de erro na base de dados
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        if 'cnxn' in locals() and cnxn:
            cnxn.close()
            print("Conexão à base de dados fechada.")

# --- Executar a função de atualização ---
if __name__ == "__main__":
    print("Iniciando o script de atualização de NIF/NISS...")
    update_nif_niss_from_csv(csv_file_path)
    print("Script de atualização finalizado.")