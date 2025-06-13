import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
from datetime import datetime, date

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

def get_db_connection():
    try:
        cnxn = pyodbc.connect(conn_str)
        return cnxn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        messagebox.showerror("Erro de Conexão", f"Ocorreu um erro ao conectar à base de dados: {ex}")
        return None

def get_employees(conn):
    employees = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT FuncionarioID, NomeCompleto FROM Funcionarios ORDER BY NomeCompleto")
        for row in cursor.fetchall():
            employees.append({"id": row.FuncionarioID, "name": row.NomeCompleto})
    return employees

def get_occurrence_types(conn):
    occurrence_types = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT TipoID, Codigo, HorasPadrao FROM TiposOcorrencia ORDER BY Codigo")
        for row in cursor.fetchall():
            occurrence_types.append({"id": row.TipoID, "code": row.Codigo, "default_hours": row.HorasPadrao})
    return occurrence_types

def get_registro_existente(conn, funcionario_id, data_registo):
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                rd.HorasTrabalhadas, rd.HorasExtraDiarias, rd.HorasAusencia, rd.Observacoes, to.Codigo
            FROM RegistosDiarios rd
            JOIN TiposOcorrencia to ON rd.TipoOcorrenciaID = to.TipoID
            WHERE FuncionarioID = ? AND DataRegisto = ?
        """, (funcionario_id, data_registo))
        return cursor.fetchone()
    return None

def submit_data():
    selected_employee_name = employee_combo.get()
    selected_date_str = date_entry.get()
    selected_occurrence_code = occurrence_combo.get()
    horas_extra = horas_extra_entry.get()
    horas_ausencia = horas_ausencia_entry.get()
    observacoes = observacoes_entry.get()

    if not selected_employee_name or not selected_date_str or not selected_occurrence_code:
        messagebox.showwarning("Campos Obrigatórios", "Por favor, preencha o Funcionário, Data e Tipo de Ocorrência.")
        return

    try:
        selected_employee_id = next(item['id'] for item in employees_data if item['name'] == selected_employee_name)
        selected_occurrence_id = next(item['id'] for item in occurrence_types_data if item['code'] == selected_occurrence_code)
        selected_occurrence_hours_padrao = next(item['default_hours'] for item in occurrence_types_data if item['code'] == selected_occurrence_code)
        
        data_registo_dt = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

        horas_trabalhadas = float(selected_occurrence_hours_padrao) if selected_occurrence_hours_padrao is not None else 0.00
        horas_extra = float(horas_extra) if horas_extra else 0.00
        horas_ausencia = float(horas_ausencia) if horas_ausencia else 0.00

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            update_sql = """
            UPDATE RegistosDiarios
            SET TipoOcorrenciaID = ?, HorasTrabalhadas = ?, HorasExtraDiarias = ?, HorasAusencia = ?, Observacoes = ?
            WHERE FuncionarioID = ? AND DataRegisto = ?
            """
            cursor.execute(update_sql, 
                           selected_occurrence_id, horas_trabalhadas, horas_extra, horas_ausencia, observacoes,
                           selected_employee_id, data_registo_dt)
            
            if cursor.rowcount == 0:
                insert_sql = """
                INSERT INTO RegistosDiarios (FuncionarioID, DataRegisto, TipoOcorrenciaID, HorasTrabalhadas, HorasExtraDiarias, HorasAusencia, Observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(insert_sql, 
                               selected_employee_id, data_registo_dt, selected_occurrence_id, horas_trabalhadas, horas_extra, horas_ausencia, observacoes)
                messagebox.showinfo("Sucesso", "Novo registo inserido com sucesso!")
            else:
                messagebox.showinfo("Sucesso", "Registo atualizado com sucesso!")
            
            conn.commit()
            conn.close()

    except ValueError:
        messagebox.showerror("Erro de Formato", "Formato de data inválido. Use AAAA-MM-DD (ex: 2025-01-31).")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        import traceback
        traceback.print_exc()

def load_existing_data():
    selected_employee_name = employee_combo.get()
    selected_date_str = date_entry.get()

    if not selected_employee_name or not selected_date_str:
        return

    try:
        selected_employee_id = next(item['id'] for item in employees_data if item['name'] == selected_employee_name)
        data_registo_dt = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

        conn = get_db_connection()
        if conn:
            registro = get_registro_existente(conn, selected_employee_id, data_registo_dt)
            conn.close()

            if registro:
                horas_trabalhadas_existente, horas_extra_existente, horas_ausencia_existente, observacoes_existente, codigo_ocorrencia_existente = registro
                
                occurrence_combo.set(codigo_ocorrencia_existente)
                horas_extra_entry.delete(0, tk.END)
                horas_extra_entry.insert(0, f"{horas_extra_existente:.2f}")

                horas_ausencia_entry.delete(0, tk.END)
                horas_ausencia_entry.insert(0, f"{horas_ausencia_existente:.2f}")

                observacoes_entry.delete(0, tk.END)
                observacoes_entry.insert(0, observacoes_existente if observacoes_existente is not None else "")
                
                messagebox.showinfo("Dados Carregados", "Dados existentes carregados para edição.")
            else:
                occurrence_combo.set("")
                horas_extra_entry.delete(0, tk.END)
                horas_extra_entry.insert(0, "0.00")
                horas_ausencia_entry.delete(0, tk.END)
                horas_ausencia_entry.insert(0, "0.00")
                observacoes_entry.delete(0, tk.END)
                observacoes_entry.insert(0, "")
                messagebox.showinfo("Dados Não Encontrados", "Não há registo para esta data e funcionário. Pode inserir um novo.")

    except ValueError:
        pass
    except Exception as e:
        messagebox.showerror("Erro ao Carregar", f"Ocorreu um erro ao carregar dados: {e}")
        import traceback
        traceback.print_exc()

root = tk.Tk()
root.title("Gestão de Registos Diários")
root.geometry("500x450")
root.resizable(False, False)

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill="both", expand=True)

row_counter = 0

ttk.Label(main_frame, text="Funcionário:").grid(row=row_counter, column=0, sticky="w", pady=2)
employee_combo = ttk.Combobox(main_frame, width=40, state="readonly")
employee_combo.grid(row=row_counter, column=1, sticky="ew", pady=2)
row_counter += 1

ttk.Label(main_frame, text="Data (AAAA-MM-DD):").grid(row=row_counter, column=0, sticky="w", pady=2)
date_entry = ttk.Entry(main_frame, width=40)
date_entry.grid(row=row_counter, column=1, sticky="ew", pady=2)
date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
row_counter += 1

load_button = ttk.Button(main_frame, text="Carregar Dados Existentes", command=load_existing_data)
load_button.grid(row=row_counter, column=0, columnspan=2, pady=5)
row_counter += 1

ttk.Label(main_frame, text="Tipo Ocorrência:").grid(row=row_counter, column=0, sticky="w", pady=2)
occurrence_combo = ttk.Combobox(main_frame, width=40, state="readonly")
occurrence_combo.grid(row=row_counter, column=1, sticky="ew", pady=2)
row_counter += 1

ttk.Label(main_frame, text="Horas Extra Diárias:").grid(row=row_counter, column=0, sticky="w", pady=2)
horas_extra_entry = ttk.Entry(main_frame, width=40)
horas_extra_entry.grid(row=row_counter, column=1, sticky="ew", pady=2)
horas_extra_entry.insert(0, "0.00")
row_counter += 1

ttk.Label(main_frame, text="Horas Ausência:").grid(row=row_counter, column=0, sticky="w", pady=2)
horas_ausencia_entry = ttk.Entry(main_frame, width=40)
horas_ausencia_entry.grid(row=row_counter, column=1, sticky="ew", pady=2)
horas_ausencia_entry.insert(0, "0.00")
row_counter += 1

ttk.Label(main_frame, text="Observações:").grid(row=row_counter, column=0, sticky="w", pady=2)
observacoes_entry = ttk.Entry(main_frame, width=40)
observacoes_entry.grid(row=row_counter, column=1, sticky="ew", pady=2)
row_counter += 1

submit_button = ttk.Button(main_frame, text="Submeter Registo", command=submit_data)
submit_button.grid(row=row_counter, column=0, columnspan=2, pady=10)
row_counter += 1

conn_initial = get_db_connection()
employees_data = []
occurrence_types_data = []

if conn_initial:
    try:
        employees_data = get_employees(conn_initial)
        employee_combo['values'] = [emp['name'] for emp in employees_data]

        occurrence_types_data = get_occurrence_types(conn_initial)
        occurrence_combo['values'] = [ot['code'] for ot in occurrence_types_data]
    except Exception as e:
        messagebox.showerror("Erro ao Carregar Dados Iniciais", f"Não foi possível carregar funcionários ou tipos de ocorrência: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn_initial.close()

root.mainloop()