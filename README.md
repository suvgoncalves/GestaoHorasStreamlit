# Sistema de Gestão de Horas e Assiduidade

Este projeto é uma aplicação web interativa desenvolvida em Python com Streamlit, projetada para a gestão eficiente de horas de trabalho, assiduidade e dados de funcionários. A solução integra-se com uma base de dados SQL Server (MS SQL Server) para armazenamento e recuperação de informações críticas, oferecendo uma interface de utilizador intuitiva e rica em funcionalidades.

Principais Funcionalidades:

Gestão de Funcionários: Adicionar, editar e remover dados de funcionários, incluindo informações pessoais, profissionais e fiscais, com suporte para campos como Departamento e Dias de Férias Anuais.

Registos de Presença e Ausência: Registo diário de horas trabalhadas, horas extra, e gestão de ausências (faltas e licenças), bem como registo e acompanhamento de férias.

Tipos de Ocorrência Configuráveis: Definição e gestão de diversos tipos de ocorrências (e.g., Diurno, Noturno, Férias, Faltas Justificadas/Injustificadas), permitindo flexibilidade na categorização dos registos de horas.

Acertos Semestrais: Ferramentas para registar e consultar acertos semestrais de horas normais, horas extra acumuladas e Folgas por Horas Extra (FOTS) disponíveis.

Relatórios e Análises Abrangentes:

Recibo de Vencimento: Geração detalhada de recibos de vencimento em formato PDF, com cálculos automáticos de salário base, horas extra, subsídio de alimentação, IRS e Segurança Social.

Quadro Mensal de Ocorrências: Visualização da assiduidade mensal dos funcionários, com um resumo das horas normais, horas extra e dias de ausência por tipo (férias, faltas, licenças).

Análise de Horas por Tipo de Ocorrência: Relatório consolidado das horas registadas por cada tipo de ocorrência num dado período.

Saldos de Horas e Dias: Acompanhamento do saldo de horas extra, dias de férias disponíveis, dias de faltas e licenças acumulados por funcionário.

Exportação de Dados: Capacidade de exportar relatórios e tabelas de dados para formatos CSV e Excel (.xlsx) para análise externa ou arquivamento.

Tecnologias Utilizadas:

Frontend/Backend: Python com Streamlit

Base de Dados: MS SQL Server (via pyodbc)

Processamento de Dados: Pandas

Geração de PDF: ReportLab

Exportação de Excel: XlsxWriter

Este projeto visa proporcionar uma ferramenta robusta e de fácil utilização para otimizar os processos de gestão de recursos humanos relacionados com o tempo de trabalho.


Nota: Todos os nomes e dados utilizados neste projeto são fictícios e não representam informações reais, visando preservar a privacidade dos dados do cliente.