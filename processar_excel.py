import pyodbc
import pandas as pd
import os
from datetime import datetime, date
import sys

DB_SERVER = '.\\SQLEXPRESS'
DB_DATABASE = 'GestaoHoras'
DB_DRIVER = '{ODBC Driver 17 for SQL Server}'

conn_str = (
    f"DRIVER={DB_DRIVER};"
    f"SERVER={DB_SERVER};"
    f"DATABASE={DB_DATABASE};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

def get_next_funcionario_number(cursor):
    """
    Obtém o próximo número de funcionário sequencial (F001, F002, etc.).
    Considera os números existentes para encontrar o próximo disponível.
    """
    try:
        # Tenta encontrar o maior número existente no formato FXXX
        cursor.execute("SELECT MAX(CAST(SUBSTRING(NumeroFuncionario, 2, LEN(NumeroFuncionario)) AS INT)) FROM Funcionarios WHERE NumeroFuncionario LIKE 'F%' AND ISNUMERIC(SUBSTRING(NumeroFuncionario, 2, LEN(NumeroFuncionario))) = 1")
        max_num = cursor.fetchone()[0]
        
        if max_num is None:
            next_num = 1
        else:
            next_num = max_num + 1
        
        return f"F{next_num:03d}" # Formata para F001, F002, etc.
    except Exception as e:
        print(f"Erro ao obter o próximo número de funcionário: {e}")
        # Retorna um número temporário em caso de erro grave, para não impedir a inserção
        return f"ERROR_{datetime.now().strftime('%H%M%S')}"

try:
    cnxn = pyodbc.connect(conn_str)
    cursor = cnxn.cursor()
    print("Conexão à base de dados SQL Server estabelecida com sucesso!")

    # Carrega TiposOcorrencia com TipoID, Codigo, HorasPadrao
    cursor.execute("SELECT TipoID, Codigo, HorasPadrao FROM TiposOcorrencia")
    tipos_ocorrencia_data = {}
    for row in cursor.fetchall():
        tipos_ocorrencia_data[row.Codigo] = {
            'TipoID': row.TipoID,
            'HorasPadrao': row.HorasPadrao
        }
    print("\nTipos de Ocorrência carregados para mapeamento:")
    for codigo, data in tipos_ocorrencia_data.items():
        print(f"  {codigo}: TipoID={data['TipoID']}, HorasPadrao={data['HorasPadrao']}")

    excel_file_path = '01Jan_12Dez_Escala_Geral_2025_AHD.xlsx'
    
    print(f"\nVerificando ficheiro Excel: '{excel_file_path}'")
    current_working_directory = os.getcwd()
    print(f"Diretório de trabalho atual do Python: {current_working_directory}")
    
    files_in_directory = os.listdir(current_working_directory)
    print(f"Ficheiros encontrados no diretório de trabalho: {files_in_directory}")
    
    is_file_present = os.path.exists(os.path.join(current_working_directory, excel_file_path))
    print(f"Os.path.exists('{excel_file_path}'): {is_file_present}")

    dates_row_index = 11      # Linha 12 do Excel
    employees_col_index = 1   # Coluna B do Excel
    data_start_col_index = 3  # Coluna D do Excel
    data_start_row_index = 12 # Linha 13 do Excel

    if os.path.exists(excel_file_path):
        try:
            df = pd.read_excel(excel_file_path, header=None)

            print(f"\nConteúdo da célula da primeira data (D12 no Excel, [11,3] no Pandas): '{df.iloc[dates_row_index, data_start_col_index]}'")
            print(f"Tipo da célula da primeira data: <class '{type(df.iloc[dates_row_index, data_start_col_index]).__name__}'>")
            
            print(f"Conteúdo da célula do primeiro funcionário (B13 no Excel, [12,1] no Pandas): '{df.iloc[data_start_row_index, employees_col_index]}'")
            print(f"Tipo da célula do primeiro funcionário: <class '{type(df.iloc[data_start_row_index, employees_col_index]).__name__}'>")
            

            dates = []
            fixed_year = 2025      # Ano fixo
            current_month = 1      # Começamos com Janeiro
            last_day_value = 0     # Para detetar a mudança de mês

            for col_idx in range(data_start_col_index, df.shape[1]):
                cell_value = df.iloc[dates_row_index, col_idx]
                
                if not isinstance(cell_value, (int, float, datetime)):
                    print(f"INFO: Parando a leitura de datas na coluna {col_idx} (valor: '{cell_value}', tipo: <class '{type(cell_value).__name__}'>), pois não é um número ou data.")
                    break 

                if pd.isna(cell_value):
                    print(f"INFO: Parando a leitura de datas na coluna {col_idx} (valor: {cell_value}), pois está vazia.")
                    break

                try:
                    date_obj = None
                    if isinstance(cell_value, (int, float)): 
                        day = int(cell_value)
                        
                        # Lógica para detetar mudança de mês, considerando anos bissextos e fim de mês
                        if day <= last_day_value and last_day_value > 0 and day < 10: 
                            current_month += 1
                            if current_month > 12:
                                current_month = 1 
                        
                        try:
                            date_obj = date(fixed_year, current_month, day)
                        except ValueError as ve:
                            if "day is out of range for month" in str(ve):
                                current_month += 1
                                if current_month > 12:
                                    current_month = 1
                                try:
                                    date_obj = date(fixed_year, current_month, day)
                                except ValueError:
                                    print(f"AVISO: Data inválida mesmo após tentar próximo mês (dia {day}, mês {current_month}, ano {fixed_year}). Coluna {col_idx}. Ignorando.")
                                    continue
                            else:
                                print(f"AVISO: Erro de valor ao criar data (dia {day}, mês {current_month}, ano {fixed_year}). Coluna {col_idx}. Erro: {ve}. Ignorando.")
                                continue
                        
                        last_day_value = day
                    
                    elif isinstance(cell_value, datetime):
                        date_obj = cell_value.date()
                        current_month = date_obj.month
                        last_day_value = date_obj.day
                    
                    elif isinstance(cell_value, str):
                        try:
                            day_str, month_str = map(int, cell_value.split('/'))
                            date_obj = date(fixed_year, month_str, day_str)
                            current_month = date_obj.month
                            last_day_value = date_obj.day
                        except ValueError:
                            try:
                                date_obj = datetime.strptime(cell_value.split(' ')[0], '%d/%m/%Y').date()
                                current_month = date_obj.month
                                last_day_value = date_obj.day
                            except ValueError:
                                print(f"AVISO: Não foi possível parsear a string da data '{cell_value}'. Coluna {col_idx}. Ignorando.")
                                continue
                    
                    if date_obj:
                        dates.append((col_idx, date_obj))

                except Exception as e:
                    print(f"AVISO: Erro inesperado ao processar célula de data na coluna {col_idx} (valor: '{cell_value}', tipo: <class '{type(cell_value).__name__}'>). Erro: {e}")
                    continue
            
            print(f"\nDatas extraídas (ano ajustado para {fixed_year}):")
            if not dates:
                print("  Nenhuma data foi extraída. Verifique a linha das datas no Excel.")
            else:
                for col_idx, d_date in dates:
                    print(f"  Coluna {col_idx}, Data: {d_date}")

            print("\nProcessando registos de funcionários:")
            registos_para_processar = []
            novos_funcionarios_inseridos = []
            funcionarios_atualizados_com_id = []

            # Mapeamento de nome de funcionário para FuncionarioID para evitar consultas repetidas
            func_info_cache = {} # Agora vai guardar { 'FuncionarioID': ID, 'NumeroFuncionario': 'FXXX' }

            for row_idx in range(data_start_row_index, df.shape[0]):
                employee_name = df.iloc[row_idx, employees_col_index]

                if pd.isna(employee_name) or str(employee_name).strip() == '':
                    break

                employee_name = str(employee_name).strip()
                print(f"  Funcionário: {employee_name}")

                # Tenta obter FuncionarioID e NumeroFuncionario do cache primeiro
                func_data = func_info_cache.get(employee_name)

                if func_data is None: # Se não está no cache, consulta a DB
                    cursor.execute("SELECT FuncionarioID, NumeroFuncionario FROM Funcionarios WHERE NomeCompleto = ?", employee_name)
                    result = cursor.fetchone()
                    
                    if result:
                        func_id = result.FuncionarioID
                        num_func_existente = result.NumeroFuncionario
                        
                        # Se existe mas o NumeroFuncionario é PENDENTE, atualiza
                        if num_func_existente and num_func_existente.startswith('PENDENTE_'):
                            new_num_func = get_next_funcionario_number(cursor)
                            print(f"  INFO: Atualizando NumeroFuncionario para '{employee_name}' de '{num_func_existente}' para '{new_num_func}'")
                            cursor.execute(
                                "UPDATE Funcionarios SET NumeroFuncionario = ? WHERE FuncionarioID = ?", 
                                new_num_func, func_id
                            )
                            cnxn.commit() # Comita a atualização do funcionário imediatamente
                            funcionarios_atualizados_com_id.append(f"{employee_name} (ID Antigo: {num_func_existente}, Novo ID: {new_num_func})")
                            func_data = {'FuncionarioID': func_id, 'NumeroFuncionario': new_num_func}
                        else:
                            func_data = {'FuncionarioID': func_id, 'NumeroFuncionario': num_func_existente}
                            
                    else:
                        # Se o funcionário não existe, gera um novo NumeroFuncionario e insere-o
                        new_num_func = get_next_funcionario_number(cursor)
                        print(f"  INFO: Inserindo novo funcionário '{employee_name}' com NumeroFuncionario: '{new_num_func}'")
                        cursor.execute(
                            "INSERT INTO Funcionarios (NomeCompleto, NumeroFuncionario) VALUES (?, ?)", 
                            employee_name, new_num_func
                        )
                        cnxn.commit() # Comita a inserção do funcionário imediatamente
                        cursor.execute("SELECT FuncionarioID FROM Funcionarios WHERE NomeCompleto = ?", employee_name)
                        func_id = cursor.fetchone().FuncionarioID
                        novos_funcionarios_inseridos.append(f"{employee_name} (ID: {new_num_func})")
                        func_data = {'FuncionarioID': func_id, 'NumeroFuncionario': new_num_func}
                    
                    func_info_cache[employee_name] = func_data # Adiciona ao cache


                for col_idx, current_date in dates:
                    ocorrencia_code = df.iloc[row_idx, col_idx]

                    if pd.notna(ocorrencia_code) and str(ocorrencia_code).strip() != '':
                        ocorrencia_code_str = str(ocorrencia_code).strip().upper()

                        if ocorrencia_code_str in tipos_ocorrencia_data:
                            ocorrencia_info = tipos_ocorrencia_data[ocorrencia_code_str]
                            
                            horas_trabalhadas = float(ocorrencia_info['HorasPadrao']) if ocorrencia_info['HorasPadrao'] is not None else 0.00
                            horas_extra_diarias = 0.00 
                            horas_ausencia = 0.00 
                            observacoes = "" 

                            if ocorrencia_code_str in ['N', 'D']:
                                horas_trabalhadas = 12.00
                                horas_ausencia = 0.00 
                            elif ocorrencia_code_str in ['F', 'L', 'B']:
                                horas_trabalhadas = 0.00 
                                horas_ausencia = 0.00 

                            registos_para_processar.append({
                                'FuncionarioID': func_data['FuncionarioID'], 
                                'DataRegisto': current_date,
                                'TipoOcorrenciaID': ocorrencia_info['TipoID'],
                                'HorasTrabalhadas': horas_trabalhadas,
                                'HorasExtraDiarias': horas_extra_diarias,
                                'HorasAusencia': horas_ausencia,
                                'Observacoes': observacoes
                            })
                        else:
                            print(f"    AVISO: Código de ocorrência '{ocorrencia_code_str}' não mapeado/encontrado em TiposOcorrencia para {employee_name} em {current_date}.")

            if registos_para_processar:
                print(f"\nTotal de {len(registos_para_processar)} registos prontos para processamento (UPSERT).")
                
                total_inseridos = 0
                total_atualizados = 0
                
                for reg in registos_para_processar:
                    func_id = reg['FuncionarioID'] 
                    data_registo = reg['DataRegisto']
                    tipo_ocorrencia_id = reg['TipoOcorrenciaID']
                    horas_trabalhadas = reg['HorasTrabalhadas']
                    horas_extra_diarias = reg['HorasExtraDiarias']
                    horas_ausencia = reg['HorasAusencia']
                    observacoes = reg['Observacoes']

                    # Tenta atualizar primeiro
                    update_sql = """
                    UPDATE RegistosDiarios
                    SET 
                        TipoOcorrenciaID = ?,
                        HorasTrabalhadas = ?,
                        HorasExtraDiarias = ?,
                        HorasAusencia = ?,
                        Observacoes = ?
                    WHERE FuncionarioID = ? AND DataRegisto = ?
                    """
                    cursor.execute(update_sql, 
                                   tipo_ocorrencia_id, 
                                   horas_trabalhadas, 
                                   horas_extra_diarias, 
                                   horas_ausencia, 
                                   observacoes,
                                   func_id, 
                                   data_registo)
                    
                    if cursor.rowcount == 0:
                        # Se nenhuma linha foi atualizada, significa que o registo não existe, então insere
                        insert_sql = """
                        INSERT INTO RegistosDiarios (
                            FuncionarioID,
                            DataRegisto,
                            TipoOcorrenciaID,
                            HorasTrabalhadas,
                            HorasExtraDiarias,
                            HorasAusencia,
                            Observacoes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """
                        cursor.execute(insert_sql, 
                                       func_id, 
                                       data_registo, 
                                       tipo_ocorrencia_id, 
                                       horas_trabalhadas, 
                                       horas_extra_diarias, 
                                       horas_ausencia, 
                                       observacoes)
                        total_inseridos += 1
                    else:
                        total_atualizados += 1
                
                cnxn.commit()
                print(f"SUCESSO: Processamento de registos concluído. {total_inseridos} inseridos, {total_atualizados} atualizados na base de dados 'RegistosDiarios'.")
            else:
                print("\nNenhum registo encontrado para inserir/atualizar na base de dados.")

            if novos_funcionarios_inseridos or funcionarios_atualizados_com_id:
                print("\n--- RESUMO DE ATRIBUIÇÃO DE NÚMERO DE FUNCIONÁRIO ---")
                if novos_funcionarios_inseridos:
                    print("Os seguintes funcionários foram INSERIDOS com um novo número de funcionário sequencial:")
                    for func_info in novos_funcionarios_inseridos:
                        print(f"- {func_info}")
                if funcionarios_atualizados_com_id:
                    print("Os seguintes funcionários tiveram o seu NumeroFuncionario ATUALIZADO para um sequencial:")
                    for func_info in funcionarios_atualizados_com_id:
                        print(f"- {func_info}")
                print("---------------------------------------------------------------")

        except FileNotFoundError:
            print(f"Erro: O ficheiro Excel '{excel_file_path}' NÃO foi encontrado. Verifique novamente a pasta e o nome.")
        except Exception as e:
            print(f"Erro ao ler ou processar o ficheiro Excel: {e}")
            import traceback
            traceback.print_exc()

    else:
        print(f"Erro: O ficheiro Excel '{excel_file_path}' NÃO foi encontrado pelo os.path.exists. Verifique a pasta e o nome.")

    cursor.close()
    cnxn.close()
    print("\nConexão à base de dados fechada.")

except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    if sqlstate == '08001':
        print("Erro de conexão (08001): O servidor ou instância não foi encontrado ou não está acessível.")
    elif sqlstate == '28000':
        print("Erro de autenticação (28000): Credenciais incorretas ou acesso negado.")
    else:
        print(f"Ocorreu um erro na base de dados: {ex}")
    import traceback
    traceback.print_exc()

print("\n--- Processamento concluído. Pressione Enter para sair... ---")
input("Pressione Enter para sair...")