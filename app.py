import io
import csv
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, send_file

# --- LÓGICA DE CONVERSÃO ---

# MODIFICADO: Adicionado o parâmetro 'formato_decimal'
def analisar_transacoes(cabecalho_str, linhas_csv, tipo_conta, delimitador, formato_decimal, palavras_a_ignorar=None):
    MAPEAMENTO_CAMPOS = {
        'data': ['data', 'date'],
        'descricao': ['histórico', 'historico', 'descrição', 'descricao', 'description', 'memo'],
        'valor': ['valor', 'montante', 'amount', 'value']
    }
    cabecalho_original = [h.strip() for h in cabecalho_str.split(delimitador)]
    cabecalho_busca = [h.lower() for h in cabecalho_original]
    mapa_final = {}
    for campo, nomes in MAPEAMENTO_CAMPOS.items():
        for nome in nomes:
            if nome in cabecalho_busca:
                mapa_final[campo] = cabecalho_original[cabecalho_busca.index(nome)]
                break
    
    if not all(k in mapa_final for k in ['data', 'descricao', 'valor']):
        raise ValueError("Cabeçalho do CSV inválido. Faltam colunas essenciais: 'data', 'descricao' ou 'valor'.")

    transacoes = []
    palavras_a_ignorar_lower = [palavra.lower() for palavra in (palavras_a_ignorar or [])]
    leitor_csv = csv.DictReader(linhas_csv, fieldnames=cabecalho_original, delimiter=delimitador)
    
    for i, linha in enumerate(leitor_csv):
        try:
            descricao = linha[mapa_final['descricao']].strip()
            if palavras_a_ignorar_lower and any(p in descricao.lower() for p in palavras_a_ignorar_lower):
                continue

            data_obj = datetime.strptime(linha[mapa_final['data']], '%d/%m/%Y')
            valor_str = linha[mapa_final['valor']].replace('R$', '').strip()
            
            # MODIFICADO: Lógica para normalizar o valor com base na escolha do usuário
            if formato_decimal == 'virgula':
                # Se a vírgula é o decimal, removemos os pontos (milhar) e trocamos a vírgula por ponto
                valor_normalizado = valor_str.replace('.', '').replace(',', '.')
            else: # formato_decimal == 'ponto'
                # Se o ponto é o decimal, apenas removemos as vírgulas (milhar)
                valor_normalizado = valor_str.replace(',', '')
            
            valor_float = float(valor_normalizado)
            
            if tipo_conta == 'credito':
                valor_float = -valor_float

            fitid_hash = hashlib.md5(f"{data_obj}{descricao}{valor_float}{i}".encode('utf-8')).hexdigest()
            transacoes.append({'data': data_obj, 'descricao': descricao, 'valor': valor_float, 'fitid': fitid_hash})
        except (ValueError, KeyError, IndexError) as e:
            # Adiciona mais detalhes ao erro para facilitar a depuração
            print(f"Aviso: Linha ignorada por erro de formatação. Linha: {linha}. Erro: {e}")
            continue
    
    transacoes.sort(key=lambda t: t['data'])
    return transacoes

# MODIFICADO: A função inteira foi reestruturada para gerar a saída OFX na ordem correta.
def gerar_ofx(transacoes, tipo_conta):
    if not transacoes:
        return ""
    
    fuso_horario_str = "120000[-3:BRT]"
    data_servidor = transacoes[-1]['data'].strftime('%Y%m%d') + fuso_horario_str
    
    header = f"""OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX>
<SIGNONMSGSRSV1><SONRS><STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS><DTSERVER>{data_servidor}</DTSERVER><LANGUAGE>POR</LANGUAGE></SONRS></SIGNONMSGSRSV1>
"""
    footer = "</OFX>"
    
    # Gera a lista de transações
    tran_list_header = f"<BANKTRANLIST><DTSTART>{transacoes[0]['data'].strftime('%Y%m%d')}</DTSTART><DTEND>{transacoes[-1]['data'].strftime('%Y%m%d')}</DTEND>"
    tran_list_footer = "</BANKTRANLIST>"
    
    trans_content_list = []
    for t in transacoes:
        trntype = "CREDIT" if t['valor'] > 0 else "DEBIT"
        valor_ofx = f"{t['valor']:.2f}".replace('.', ',')
        trans_content_list.append(f"<STMTTRN><TRNTYPE>{trntype}</TRNTYPE><DTPOSTED>{t['data'].strftime('%Y%m%d')}{fuso_horario_str}</DTPOSTED><TRNAMT>{valor_ofx}</TRNAMT><FITID>{t['fitid']}</FITID><MEMO>{t['descricao']}</MEMO></STMTTRN>")

    # Gera o bloco de saldo
    ledger_bal = f"<LEDGERBAL><BALAMT>0.00</BALAMT><DTASOF>{data_servidor}</DTASOF></LEDGERBAL>"

    # Agrupa o conteúdo interno (lista de transações + saldo)
    transacoes_e_saldo = "\n".join([
        tran_list_header,
        *trans_content_list,
        tran_list_footer,
        ledger_bal
    ])

    # Cria o "envelope" específico para o tipo de conta
    if tipo_conta == 'credito':
        acct_header = "<CREDITCARDMSGSRSV1><CCSTMTTRNRS><TRNUID>1</TRNUID><STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS><CCSTMTRS><CURDEF>BRL</CURDEF><CCACCTFROM><ACCTID>CARTAO-FINAL-0000</ACCTID></CCACCTFROM>"
        acct_footer = "</CCSTMTRS></CCSTMTTRNRS></CREDITCARDMSGSRSV1>"
    else:
        acct_header = "<BANKMSGSRSV1><STMTTRNRS><TRNUID>1</TRNUID><STATUS><CODE>0</CODE><SEVERITY>INFO</SEVERITY></STATUS><STMTRS><CURDEF>BRL</CURDEF><BANKACCTFROM><BANKID>000</BANKID><ACCTID>CONTA-FINAL-0000</ACCTID><ACCTTYPE>CHECKING</ACCTTYPE></BANKACCTFROM>"
        acct_footer = "</STMTRS></STMTTRNRS></BANKMSGSRSV1>"

    # Junta o envelope com o conteúdo interno
    conteudo_final_da_conta = "\n".join([acct_header, transacoes_e_saldo, acct_footer])

    # Junta o cabeçalho principal, o conteúdo e o rodapé
    return "\n".join([header, conteudo_final_da_conta, footer])


# --- ROTAS DA APLICAÇÃO WEB ---

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/converter', methods=['POST'])
def converter_arquivo():
    try:
        arquivo_csv = request.files['csv_file']
        tipo_conta = request.form['tipo_conta']
        delimitador = request.form['delimitador']
        # NOVO: Obtém o novo parâmetro do formulário
        formato_decimal = request.form['formato_decimal']
        palavras_a_ignorar = [p.strip() for p in request.form.get('ignorar', '').split(',') if p.strip()]
        
        if not arquivo_csv:
            raise ValueError("Nenhum ficheiro enviado.")

        linhas = arquivo_csv.stream.read().decode('utf-8-sig').splitlines()
        
        if len(linhas) < 2:
            return "Ficheiro CSV parece estar vazio ou não contém linhas de dados.", 400

        cabecalho, linhas_csv = linhas[0], linhas[1:]
        
        # MODIFICADO: Passa o novo parâmetro para a função de análise
        transacoes = analisar_transacoes(cabecalho, linhas_csv, tipo_conta, delimitador, formato_decimal, palavras_a_ignorar)
        ofx_content = gerar_ofx(transacoes, tipo_conta)
        
        if not ofx_content:
            return "Nenhuma transação válida foi encontrada no ficheiro para gerar um OFX.", 400

        return send_file(
            io.BytesIO(ofx_content.encode('utf-8')),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name='convertido.ofx'
        )
    except Exception as e:
        return f"Ocorreu um erro: <br><pre>{e}</pre>", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

