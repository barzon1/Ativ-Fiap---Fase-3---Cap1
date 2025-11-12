import json
import os
import datetime

try:
    import oracledb as oracle_driver
except ImportError:
    oracle_driver = None
    print("Aviso: A biblioteca 'oracledb' não foi encontrada. A conexão com o DB não será funcional.")

ESTAGIOS_CRITICOS = ('V3 (Primeiro trifólio)', 'R5 (Pré-floração)',
                     'R6 (Floração)', 'R7 (Enchimento de grãos)')

# Lista para armazenar dados em memória (requisito de Lista)
TALHOES_MONITORADOS = []

# Carrega as regras do JSON ao iniciar o programa
CONFIG = {}
try:
    with open('config_perdas.json', 'r', encoding='utf-8') as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    print("Erro: Arquivo 'config_perdas.json' não encontrado. Crie o arquivo conforme a documentação.")
    CONFIG = {
        "regras_perda": [
            {"nivel_estresse": "Baixo", "perda_percentual": 0.05,
                "alerta": "Risco baixo."},
            {"nivel_estresse": "Alto", "perda_percentual": 0.35,
                "alerta": "Risco crítico."}
        ],
        "custo_medio_feijao_rs_ton": 3000.00
    }
except json.JSONDecodeError:
    print("Erro: Arquivo 'config_perdas.json' inválido.")
    exit()

# 1. Função: Conexão com Banco de Dados Oracle

def conectar_oracle():
    """Tenta estabelecer a conexão com o banco de dados Oracle."""
    if not oracle_driver:
        print("\nERRO: Driver Oracle (cx_Oracle/oracledb) não instalado. A conexão foi simulada.")
        return None

    USUARIO = "rm567914"
    SENHA = "060497"
    DSN = "oracle.fiap.com.br:1521/ORCL"
    try:
        conexao = oracle_driver.connect(user=USUARIO, password=SENHA, dsn=DSN)
        print("\n[SUCESSO] Conexão com Oracle estabelecida!")
        return conexao
    except Exception as e:
        print(f"\n[ERRO] Falha ao conectar ao Oracle: {e}")
        return None

# 2. Função: Cálculo da Perda Estimada

def calcular_perda_estimada(nivel_estresse: str) -> dict:
    """Calcula a porcentagem de perda e o alerta com base no nível de estresse."""
    nivel_estresse = nivel_estresse.strip().capitalize()

    for regra in CONFIG.get('regras_perda', []):
        if regra['nivel_estresse'] == nivel_estresse:
            return regra

    return CONFIG['regras_perda'][0]

# 3. Procedimento: Registrar Log e Gravar no Banco



def registrar_log_e_salvar(talhao: dict, conexao_db):
    """Grava o registro no banco de dados e no arquivo de log."""

    # 3.1. GRAVAÇÃO NO ORACLE
    if conexao_db:
        cursor = conexao_db.cursor()
        try:

            sql = """
            INSERT INTO HISTORICO_PLANTIO 
            (ID, DATA_MONITORAMENTO, CULTIVAR, AREA, ESTRESSE, PERDA_PERC, PREJUIZO_ESTIMADO) 
            VALUES (:1, :2, :3, :4, :5, :6, :7)
            """
            cursor.execute(sql, (
                talhao['id'],                               
                talhao['data_monitoramento'],               
                talhao['cultivar'],                        
                talhao['area'],                             
                talhao['estresse_hidrico'],                 
                talhao['perda_percentual'],                
                talhao['prejuizo_estimado_rs']              
            ))
            conexao_db.commit()
            print(
                f"-> Dados do Talhão {talhao['id']} gravados no Oracle com sucesso!")
        except Exception as e:
            print(f"-> ERRO ao gravar no Oracle: {e}")
        finally:
            cursor.close()

    # 3.2. GRAVAÇÃO EM ARQUIVO DE TEXTO (LOG)
    log_entry = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Talhão ID {talhao['id']} - Estresse: {talhao['estresse_hidrico']} - Perda: {talhao['perda_percentual'] * 100:.1f}%\n"
    with open('registro_monitoramento.txt', 'a') as log_file:
        log_file.write(log_entry)

# 4. Procedimento: Geração do Relatório
def gerar_relatorio(lista_talhoes: list):
    """Exibe o relatório de todos os talhões monitorados com alertas."""
    if not lista_talhoes:
        print("\nNenhum talhão cadastrado para monitoramento.")
        return

    print("\n" + "="*50)
    print("      RELATÓRIO DE MONITORAMENTO DE ESTRESSE HÍDRICO")
    print("="*50)

    total_prejuizo = 0

    for talhao in lista_talhoes:
        print(
            f"\n[TALHÃO ID: {talhao['id']} | CULTIVAR: {talhao['cultivar']} | ÁREA: {talhao['area']} ha]")
        print(f"Estágio Fenológico (Exemplo Fixo): {ESTAGIOS_CRITICOS[2]}")
        print("-" * 40)

        # Cálculo do Prejuízo (Usando o Dicionário de Config)
        custo_ton = CONFIG.get('custo_medio_feijao_rs_ton', 3000.00)
        perda_perc = talhao['perda_percentual']
        prejuizo = talhao['produtividade_esperada_ton'] * \
            perda_perc * custo_ton
        total_prejuizo += prejuizo

        print(
            f"Nível de Estresse Hídrico: {talhao['estresse_hidrico'].upper()}")
        print(f"PERDA ESTIMADA DE PRODUTIVIDADE: {perda_perc * 100:.1f}%")
        print(f"PREJUÍZO FINANCEIRO ESTIMADO: R$ {prejuizo:,.2f}")
        print(f"ALERTA DO SISTEMA: {talhao['alerta']}")
        print("-" * 40)

    print("\n" + "="*50)
    print(f"TOTAL DE PREJUÍZO (Simulado): R$ {total_prejuizo:,.2f}")
    print("="*50)

# 5. Função de Cadastro (Interface)


def cadastrar_novo_talhao(conexao_db) -> bool:
    """Solicita dados do usuário e adiciona um novo talhão à lista."""

    print("\n--- CADASTRO DE NOVO TALHÃO ---")

    # 1. Validação de Entrada (Requisito: Consistir os dados)
    while True:
        try:
            area = float(input("Área do Talhão (em hectares): "))
            if area <= 0:
                raise ValueError
            break
        except ValueError:
            print("Entrada inválida. Digite um número positivo para a área.")

    while True:
        try:
            produtividade_esperada = float(
                input("Produtividade Esperada (em Toneladas): "))
            if produtividade_esperada <= 0:
                raise ValueError
            break
        except ValueError:
            print("Entrada inválida. Digite um número positivo para a produtividade.")

    # 2. Entrada de Dados Chave
    cultivar = input("Tipo de Feijão (Ex: Carioca, Preto): ")

    while True:
        estresse_hidrico = input(
            "Nível de Estresse (Baixo, Moderado, Alto): ").strip().capitalize()
        niveis_validos = [r['nivel_estresse']
                          for r in CONFIG.get('regras_perda', [])]
        if estresse_hidrico in niveis_validos:
            break
        print(f"Nível inválido. Escolha entre: {', '.join(niveis_validos)}")

    # 3. Cálculo e Montagem do Dicionário (Requisito: Dicionário)
    regra_perda = calcular_perda_estimada(estresse_hidrico)
    perda_percentual = regra_perda['perda_percentual']
    alerta_sistema = regra_perda['alerta']

    prejuizo_estimado = produtividade_esperada * perda_percentual * \
        CONFIG.get('custo_medio_feijao_rs_ton', 3000.00)

    novo_talhao = {
        'id': len(TALHOES_MONITORADOS) + 1,
        'data_monitoramento': datetime.datetime.now(), 
        'area': area,
        'produtividade_esperada_ton': produtividade_esperada,
        'cultivar': cultivar,
        'estresse_hidrico': estresse_hidrico,
        'perda_percentual': perda_percentual,
        'alerta': alerta_sistema,
        'prejuizo_estimado_rs': prejuizo_estimado
    }

    TALHOES_MONITORADOS.append(novo_talhao)

    # 4. Gravação (Usa o Procedimento)
    registrar_log_e_salvar(novo_talhao, conexao_db)

    print(f"\n[SUCESSO] Talhão {novo_talhao['id']} cadastrado e monitorado.")
    return True

# --- Execução Principal ---


def main():
    """Função principal que executa o menu."""

    conexao_db = conectar_oracle()

    while True:
        print("\n" + "="*30)
        print("  SISTEMA AGROTECH - FEIJÃO")
        print("="*30)
        print("1. Cadastrar Novo Talhão e Monitorar")
        print("2. Gerar Relatório de Alertas")
        print("3. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            cadastrar_novo_talhao(conexao_db)
        elif opcao == '2':
            gerar_relatorio(TALHOES_MONITORADOS)
        elif opcao == '3':
            print("Encerrando o sistema de monitoramento. Até breve!")
            if conexao_db:
                conexao_db.close()
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
