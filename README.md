Sistema de Gestão de Horas e Assiduidade

Este projeto é uma aplicação web interativa desenvolvida em Python com Streamlit, projetada para gerir de forma eficiente os registos de horas, assiduidade, férias, faltas, licenças e acertos semestrais de funcionários. Oferece uma interface de utilizador intuitiva para adicionar, editar e visualizar dados de funcionários, bem como gerar relatórios e recibos de vencimento.

🎯 Visão Geral do Projeto
O objetivo principal deste sistema é automatizar e simplificar a gestão de recursos humanos no que diz respeito ao controlo de tempo e presença. A aplicação conecta-se a uma base de dados SQL Server, garantindo a persistência e a integridade dos dados, e fornece ferramentas essenciais para a administração de pessoal, cálculo de horas trabalhadas e extra, e preparação de documentação fundamental como recibos de vencimento.

✨ Funcionalidades Principais
O sistema é dividido em várias secções, cada uma com um conjunto específico de funcionalidades:

📊 Dashboard Geral:

Apresenta uma visão macro com métricas chave, como o número total de funcionários, horas trabalhadas e horas extra acumuladas no mês atual.

Exibe os últimos registos de presença para uma rápida auditoria.

Lista as próximas férias e licenças, permitindo um planeamento antecipado.

👥 Gestão de Funcionários:

Adicionar Novo Funcionário: Formulário completo para registar novos colaboradores com detalhes como nome, número de funcionário, dados pessoais (NIF, NISS, contacto, email), categoria profissional, departamento, salário base, subsídio de alimentação diário, taxas de IRS e Segurança Social, horas de trabalho mensais padrão, taxas de hora extra e direito a dias de férias anuais.

Editar Funcionário Existente: Capacidade de atualizar qualquer informação de um funcionário registado.

Apagar Funcionário: Funcionalidade para remover funcionários do sistema, com aviso de que todos os registos associados (presença, férias, faltas, licenças, acertos) serão também eliminados, garantindo a consistência dos dados.

📝 Registos de Presença e Ausência:

Interface unificada para gerir diferentes tipos de registos de tempo.

Registo Diário: Permite registar horas trabalhadas (normais e extra) e horas de ausência para cada funcionário em datas específicas, associadas a um tipo de ocorrência.

Férias: Registo de períodos de férias com datas de início e fim, observações e um campo para aprovação.

Faltas: Registo de faltas por dia, com motivo, indicação de justificação, horas de ausência e aprovação.

Licenças: Registo de períodos de licença com datas de início e fim, motivo, observações e aprovação.

Gestão de Tipos de Ocorrência: Um módulo CRUD (Create, Read, Update, Delete) dedicado para definir e gerir os diferentes tipos de ocorrência (e.g., Turno Diurno, Turno Noturno, Férias, Folga por Trabalho Suplementar, Falta Injustificada), incluindo suas siglas, horas padrão e características (se é turno, hora extra, ausência, FOTS, etc.).

💰 Gerar Recibo de Vencimento:

Permite selecionar um funcionário e um mês/ano específicos para gerar um recibo de vencimento detalhado.

Realiza cálculos automáticos com base nos dados do funcionário e nos registos de presença (salário base, horas extra, subsídio de alimentação, descontos de IRS e Segurança Social, impacto de ausências).

Gera um documento PDF com um layout profissional, pronto para download.

📈 Acertos Semestrais:

Funcionalidade para registar e gerir os acertos semestrais de horas para cada funcionário.

Permite registar o total de horas normais, horas extra acumuladas e Folgas por Trabalho Suplementar (FOTS) disponíveis num determinado semestre e ano.

Suporte para adicionar, editar e apagar registos de acertos semestrais.

📋 Relatórios e Análises:

Filtros Globais: Permite filtrar relatórios por mês, ano e departamento.

Saldos de Horas e Dias: Apresenta um relatório consolidado do saldo de horas extra acumuladas, dias de férias anuais (direito, tirados e disponíveis), dias de faltas e dias de licença para cada funcionário no ano selecionado.

Quadro Mensal de Ocorrências (Assiduidade): Gera um quadro detalhado mês a mês da assiduidade dos funcionários, mostrando as ocorrências diárias (com siglas coloridas para fácil visualização) e totais de horas normais, horas extra, dias de férias, faltas e licenças.

Análise de Horas por Tipo de Ocorrência: Fornece um relatório agrupado por tipo de ocorrência, mostrando as horas normais, extra e de ausência associadas a cada tipo para o período selecionado.

Exportação de Dados: Todos os relatórios podem ser exportados para formatos CSV e Excel para análise externa.

🛠️ Tecnologias Utilizadas
Este projeto foi construído utilizando as seguintes tecnologias:

Python: A linguagem de programação principal para a lógica da aplicação.

Streamlit: Framework Python para a construção rápida e interativa da interface web.

Pandas: Biblioteca fundamental para manipulação e análise de dados, essencial para processar os dados da base de dados e gerar relatórios.

Microsoft SQL Server Express / Azure SQL Database: O sistema de gestão de base de dados relacional (SGBDR) utilizado para armazenar todos os dados do projeto de forma estruturada.

PyODBC: Driver Python que permite a conexão da aplicação Streamlit com a base de dados SQL Server.

ReportLab: Biblioteca Python para a criação programática de documentos PDF, utilizada para gerar os recibos de vencimento.

XlsxWriter: Engine para o Pandas que permite a exportação de DataFrames para ficheiros Excel (.xlsx).

⚙️ Configuração da Base de Dados e Migração
A base de dados GestaoHoras foi inicialmente configurada no Microsoft SQL Server Express e posteriormente migrada para o Azure SQL Database. A conexão da aplicação é feita através do pyodbc.

Destaques da Configuração e Migração da Base de Dados:

Autenticação: A aplicação foi configurada para conectar-se ao SQL Server local via Autenticação do Windows (Trusted_Connection=yes). Após a migração para o Azure SQL Database, a conexão foi ajustada para utilizar autenticação SQL (nome de utilizador e palavra-passe) e garantir a encriptação dos dados em trânsito.

Estrutura de Tabelas: O projeto interage com as seguintes tabelas no esquema dbo:

Funcionarios: Informações detalhadas sobre cada funcionário, incluindo campos como Departamento, DiasFeriasAnuais e Cargo.

RegistosDiarios: Registo diário de horas trabalhadas, horas extra e ausências por funcionário.

Ferias: Registo de períodos de férias, incluindo o estado de Aprovado.

Faltas: Registo de faltas, com indicação se foram Justificadas, HorasAusenciaFalta e o estado de Aprovado.

Licencas: Registo de períodos de licença, incluindo o estado de Aprovado.

TiposOcorrencia: Tabela de lookup para definir diferentes tipos de eventos/ocorrências, com campos como Codigo, Descricao, HorasPadrao, e várias flags (EhTurno, EhHorasExtra, EhAusencia, EhFOTS, EhFolgaCompensatoria, Sigla).

AcertosSemestrais: Registo dos saldos de horas extra e FOTS por semestre.

Processo de Migração: A migração da base de dados local para o Azure SQL Database foi realizada utilizando o Azure Data Migration Assistant (DMA). Este processo envolveu a criação de um servidor SQL e uma base de dados no Azure, configuração de regras de firewall para permitir a conectividade, e a utilização do DMA para copiar o esquema e os dados.

💻 Processo de Desenvolvimento Local e Conexão ao GitHub
Esta seção descreve as etapas que foram executadas para desenvolver o projeto localmente e sincronizá-lo com um repositório no GitHub.

Clonagem do Repositório (ou Inicialização): O projeto foi inicializado (ou clonado de um repositório base) numa pasta local designada para o desenvolvimento.

Criação do requirements.txt: As dependências Python utilizadas no projeto foram registadas num ficheiro requirements.txt através do comando pip freeze > requirements.txt, garantindo a reprodutibilidade do ambiente de desenvolvimento.

Inicialização do Repositório Git Local: Um repositório Git foi inicializado na pasta do projeto (git init) para gerir o controlo de versões das alterações.

Adição de Ficheiros ao Staging: As modificações nos ficheiros do projeto foram adicionadas à área de "staging" (git add .) para preparação do commit.

Realização de Commits: As alterações foram guardadas no histórico local do repositório através de commits (git commit -m "Mensagem do commit"), com mensagens descritivas para cada conjunto de modificações.

Conexão ao Repositório GitHub: O repositório Git local foi ligado a um repositório remoto criado no GitHub (git remote add origin ..., git branch -M main).

Envio de Alterações para o GitHub (git push): As alterações locais foram enviadas (pushed) para o repositório remoto no GitHub (git push -u origin main), tornando o código acessível e versionado na plataforma.

Configuração de Segredos do Streamlit: Para a segurança das credenciais da base de dados, foi utilizado o sistema de segredos do Streamlit. Um ficheiro .streamlit/secrets.toml foi configurado com as variáveis de conexão para o Azure SQL Database, garantindo que as credenciais não fossem expostas diretamente no código ou no repositório público.

🛠️ Melhorias Futuras Potenciais
Autenticação de Utilizadores: Implementar um sistema de login de utilizadores dentro da própria aplicação (além da autenticação da base de dados) para diferentes níveis de acesso e permissões.

Auditoria de Registos: Adicionar campos de data de criação/última atualização e o utilizador que realizou a alteração.

Notificações: Enviar notificações por email sobre férias aprovadas ou faltas não justificadas.

Integração com Calendários: Sincronizar eventos (férias, licenças) com calendários externos.

Otimização de Performance: Para grandes volumes de dados, considerar otimizações de query ou indexação.

Interface mais Avançada: Gráficos interativos no dashboard para visualização de tendências.

🤝 Autor
Susana Gonçalves
