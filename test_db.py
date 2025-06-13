import pyodbc

DB_SERVER = '.\\SQLEXPRESS'
DB_DATABASE = 'GestaoHoras'
DB_DRIVER = '{ODBC Driver 17 for SQL Server}' # Mantenha 17, já que você instalou essa versão

conn_str = (
    f"DRIVER={DB_DRIVER};"
    f"SERVER={DB_SERVER};"
    f"DATABASE={DB_DATABASE};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

try:
    print("Tentando conectar à base de dados...")
    cnxn = pyodbc.connect(conn_str)
    print("Conexão bem-sucedida ao SQL Server!")
    cursor = cnxn.cursor()
    cursor.execute("SELECT @@SERVERNAME, DB_NAME()")
    server_name, db_name = cursor.fetchone()
    print(f"Conectado ao Servidor: {server_name}, Base de Dados: {db_name}")

    # Teste extra: Buscar alguns funcionários
    cursor.execute("SELECT TOP 5 NomeCompleto FROM Funcionarios")
    print("\nPrimeiros 5 funcionários:")
    for row in cursor.fetchall():
        print(f"- {row.NomeCompleto}")

    cursor.close()
    cnxn.close()
    print("\nConexão fechada.")
except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    print(f"Erro de conexão SQL Server: {ex}")
    print(f"SQLSTATE: {sqlstate}")
    print("Verifique:")
    print(f"  - O nome do servidor: '{DB_SERVER}'")
    print(f"  - O nome da base de dados: '{DB_DATABASE}'")
    print(f"  - Se o SQL Server Express está a correr.")
    print(f"  - Se o serviço SQL Server Browser está a correr (se aplicável).")
    print(f"  - Se as permissões do Windows (Trusted_Connection=yes) estão corretas.")
except Exception as e:
    print(f"Erro inesperado: {e}")