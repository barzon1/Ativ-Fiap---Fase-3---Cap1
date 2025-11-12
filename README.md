# PBL Fase 3 - FarmTech Solutions (IA)

Este repositório documenta a Fase 3 do Projeto-Base de Aprendizagem (PBL) do curso de Inteligência Artificial, focado na startup fictícia FarmTech Solutions.

## Entrega Obrigatória: Banco de Dados Oracle

Nesta fase, o objetivo foi carregar os dados coletados na Fase 2 em um banco de dados relacional Oracle SQL Developer, simulando o armazenamento e a consulta de dados de sensores no agronegócio.

### 1. Processo de Conexão e Importação

Seguindo o guia fornecido, realizamos a conexão com o banco de dados Oracle da FIAP.
![Configurações da conexão](/assets/config.jpg)

Após a conexão bem-sucedida, utilizamos a ferramenta de importação de dados ("Importa Dados") para carregar nosso arquivo de dados da Fase 2.
![Importação da tabela](/assets/import_date.jpg)

### 2. Definição e Carga da Tabela

O arquivo foi carregado para uma nova tabela, que nomeamos como `HISTORICO`. As colunas foram mapeadas automaticamente a partir do arquivo de origem, e os dados foram importados com sucesso.
![Tela de Confirmação](/assets/confirmation.jpg)

### 3. Consulta SQL dos Dados

Para verificar se os dados foram carregados corretamente, executamos uma consulta `SELECT *` na tabela criada. Os resultados confirmam que os dados estão agora armazenados no banco de dados Oracle.

**Consulta Realizada:**
![Tabela importada](/assets/table.jpg)
SELECT * FROM HISTORICO;




