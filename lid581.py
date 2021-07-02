######################################################################################################
                                           #Introdução
######################################################################################################
# O sistema desenvolvido coleta os dados dos 5 porques através de um formulário web e armazena num  
# banco no-SQL. Esses dados são ligos e disponibilizados para visualização e edição

# Tecnologias:
# Streamlit para web, streamlit share para deploy, banco de dados Firebase (Google)

# Link:
# https://share.streamlit.io/eng01git/5pq/main/5pq.py
######################################################################################################
                                 # importar bibliotecas
######################################################################################################

import streamlit as st
from streamlit_tags import st_tags
from streamlit import caching
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import json
import smtplib
import time
import datetime
import time
from datetime import  date
import base64
from io import BytesIO

from google.cloud import firestore
from google.oauth2 import service_account

######################################################################################################
				#Configurações da página
######################################################################################################

st.set_page_config(
     page_title="LID Forms",
     layout="wide",
)

######################################################################################################
				#Configurando acesso ao firebase
######################################################################################################

# Pega as configurações do banco do segredo
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)

# Seleciona o projeto
db = firestore.Client(credentials=creds, project="st-5why")
doc_ref = db.collection(u'5porques')

# Link do arquivo com os dados
DATA_URL = "data.csv"

######################################################################################################
				     #Definição da sidebar
######################################################################################################

fig1s, fig2s, fig3s = st.sidebar.beta_columns([1,2,1])
fig1s.write('')
fig2s.image('latas minas.png', width=150)
fig3s.write('')
st.sidebar.title("LID Forms")
formularios = [
	'Liner diário',
	'Liner semanal',
	'Shell diário',
	'Shell semanal',
	'Autobagger diário',
	'Autobagger semanal',
	'Autobagger Mensal',
	'Conversion diário',
	'Conversion semanal',
	'Conversion mensal',
	'Balacer diário',
	'Balancer semanal',
	'Estatisticas',			# Gráficos com filtros
	'Visualizar formulários',	# Filtros para visualizar os questionários desejeados
	'Suporte Engenharia'
]

func_escolhida = st.sidebar.radio('Selecione o formulário de saída', formularios, index=0)

######################################################################################################
                               #Função para leitura do banco (Firebase)
######################################################################################################
# Efetua a leitura de todos os documentos presentes no banco e passa para um dataframe pandas
# Função para carregar os dados do firebase (utiliza cache para agilizar a aplicação)
@st.cache
def load_data():
	data = pd.read_csv(DATA_URL)
	
	# Define o caminho da coleção do firebase
	posts_ref = db.collection("5porques_2")	
	
	# Busca todos os documentos presentes na coleção e salva num dataframe
	for doc in posts_ref.stream():
		dicionario = doc.to_dict()
		dicionario['document'] = doc.id
		data = data.append(dicionario, ignore_index=True)
	
	# Formata as colunas de data e hora para possibilitar filtros
	data['data'] = pd.to_datetime(data['data']).dt.date
	data['hora'] = pd.to_datetime(data['hora']).dt.time
	return data

# Efetua a leitura dos dados dos usuários no banco
@st.cache
def load_usuarios():
	# Define as colunas do dataframe
	data_user = pd.DataFrame(columns=['Nome', 'Email', 'Gestor', 'Codigo'])
	
	# Define o caminho da coleção do firebase
	posts_ref = db.collection("Users")	
	
	# Busca todos os documentos presentes na coleção e salva num dataframe
	for doc in posts_ref.stream():
		dicionario = doc.to_dict()
		dicionario['document'] = doc.id
		data_user = data_user.append(dicionario, ignore_index=True)
	return data_user

# Efetua a escrita das ações no banco de dados
def write_acoes(acoes, documento, gestor):
	
	# Define o caminho da coleção do firebase
	posts_ref = db.collection("acoes")	
	
	# Lista e dicionario vazio
	acoes_firebase = []
	dic_to_firebase = {}
	
	# Busca todos os documentos presentes na coleção e salva num dataframe
	for doc in posts_ref.stream():
		acoes_firebase.append(doc.id)
		
	index = 0
	
	# Itera sobre todas as ações do 5-Porques
	for i in acoes:
		
		# Separa a string
		lista = i.split(";;")
		
		# Define o nome do documento a ser armazenado na base de dados
		chave = str(documento) + '_' + str(index)
		
		# Verifica se a ação já consta no banco de dados
		if chave not in acoes_firebase:	
			
			# Definição da ação com alteração do status para em aberto
			dic_to_firebase[chave] = {'Ação': lista[0],
						  'Dono': lista[1],
						  'Prazo': lista[2],
						  'Numero da ação': index,
						  'Numero do 5-Porques': documento,
						  'Status': 'Em aberto',
						  'Gestor': gestor,
						  'E-mail': 'Não enviado',
						  'Editor': '',
						  'Data': ''
						 }		
			db.collection("acoes").document(chave).set(dic_to_firebase[chave],merge=True)
			
			# Envia email para o dono da acao 
			remetente = usuarios_fb.loc[usuarios_fb['Nome'] == lista[1], 'Email'].to_list()
			send_email(remetente[0], 6, lista[2], lista[0], 0)
			time.sleep(1)
			#send_email(to, atividade, documento, comentario, gatilho):
			
		else:
			
			# Caso a ação já esteja no banco de dados, ela é modificada mas seu status não é alterado
			dic_to_firebase[chave] = {'Ação': lista[0],
						  'Dono': lista[1],
						  'Prazo': lista[2],
						  'Numero da ação': index,
						  'Numero do 5-Porques': documento,
						  'Gestor': gestor,
						  'E-mail': 'Não enviado'
						 }		
			db.collection("acoes").document(chave).set(dic_to_firebase[chave],merge=True)
		index += 1

# Grava a edição das ações no banco
def gravar_acao_edit(row):
	ea_chave = str(row['Numero do 5-Porques']) + '_' + str(row['Numero da ação'])
	row_string = row.astype(str)
	db.collection("acoes").document(ea_chave).set(row_string.to_dict(),merge=True)
	caching.clear_cache()

######################################################################################################
                                           #Função para enviar email
######################################################################################################
# Recebe como parâmetros destinatário e um código de atividade para o envio
# O email está configurado por parâmetros presentes no streamlit share (secrets)
def send_email(to, atividade, documento, comentario, gatilho):
	
	# Configura quem vai enviar o email
	gmail_user = st.secrets["email"]
	gmail_password = st.secrets["senha"]
	sent_from = gmail_user
	
	# Cria os campos que estarão no e-mail
	from_ = 'LID Forms'
	subject = ""
	body = ''
	atividade = int(atividade)
	
	# Verifica o código da atividade e edita a mensagem (criação, retificação, aprovação ou reproavação de 5-Porques
	# Criação
	if atividade == 0:
		body = "Olá, foi gerada um novo 5-Porques, acesse a plataforma para avaliar.\nhttps://share.streamlit.io/eng01git/5pq/main/5pq.py\n\nAtenciosamente, \nAmbev 5-Porques"
		subject = """Gerado 5-Porques %s""" % (documento)
	
	# Transforma o remetente em lista
	list_to = [to]
	
	# Verifica se precisa mandar o e-mail para a engenharia
	if int(gatilho) > 60:	
		pass
	
	# Monta a mensagem
	email_text = """From: %s\nTo: %s\nSubject: %s\n\n%s
	""" % (from_, list_to, subject, body)
	
	# Envia a mensagem
	try:
		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		server.ehlo()
		server.login(gmail_user, gmail_password)
		server.sendmail(sent_from, list_to, email_text.encode('latin-1'))
		server.close()
		st.write('E-mail enviado!')
	except:
		st.error(list_to)

######################################################################################################
                                           #Função para download
######################################################################################################
# download de csv		
def download(df):
	"""Generates a link allowing the data in a given panda dataframe to be downloaded
	in:  dataframe
	out: href string
	"""
	csv = df.to_csv(index=False)
	b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
	href = f'<a href="data:file/csv;base64,{b64}">Download dos dados como csv</a>'
	return href

# Gera arquivo excel
def to_excel(df):
	output = BytesIO()
	writer = pd.ExcelWriter(output, engine='xlsxwriter')
	df.to_excel(writer, sheet_name='Sheet1')
	writer.save()
	processed_data = output.getvalue()
	return processed_data

# Gera o link para o download do excel
def get_table_download_link(df):
	"""Generates a link allowing the data in a given panda dataframe to be downloaded
	in:  dataframe
	out: href string
	"""
	val = to_excel(df)
	b64 = base64.b64encode(val)  # val looks like b'...'
	return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="dados.xlsx">Download dos dados em Excel</a>' # decode b'abc' => abc

			   
######################################################################################################
                              #Formulários
######################################################################################################

def Liner_diario():
	
	with st.form('Form'):
    
		# Define a organização das colunas
		st0, st1 = st.beta_columns(2)
		st2, st3 = st.beta_columns(2)
		st4, st5 = st.beta_columns(2)
		st6, st7 = st.beta_columns(2)
		st8, st9 = st.beta_columns(2)
		st10, st11 = st.beta_columns(2)
		st12, st13 = st.beta_columns(2)
		st14, st15 = st.beta_columns(2)
		st16, st17 = st.beta_columns(2)

		respostas = ['NOK', 'OK']

		# Questões
		dic['q00'] = st0.selectbox('Nome do colaborador', nomes) #definir nomes
		dic['q01'] = st1.selectbox('Selecione o turno', turnos )
		dic['q02'] = st2.selectbox('Retirar a escova do suporte, depositar a escova dentro do recipiente com solução de limpeza durante 30 minutos.  Inspecionar as escovas para detectar possíveis anomalias e desgastes.', respostas)
		dic['q03'] = st3.text_input('Comentário \n ', "")
		dic['q04'] = st4.selectbox('Limpeza das guias de saída: 1-Limpeza do superfície utilizando pano umedecido com álcool isopropílico. Inspecionar as saídas para detectar possíveis anomalias e desgastes.', respostas)
		dic['q05'] = st5.text_input('Comentário  ', "")
		dic['q06'] = st6.selectbox('Limpeza do conjunto Lower Turret e Upper Turret: 1-Limpeza do superfície utilizando pano umedecido com álcool isopropílico. Inspecionar o conjunto para detectar possíveis anomalias e desgastes.', respostas)
		dic['q07'] = st7.text_input('Comentário   ', "")
		dic['q08'] = st8.selectbox('Limpeza da mesa e da Star Wheel: 1-Limpeza do superfície utilizando pano umedecido com álcool isopropílico. Inspecionar a mesa para detectar possíveis anomalias e desgastes.', respostas)
		dic['q09'] = st9.text_input('Comentário    ', "")
		dic['q10'] = st10.selectbox('Limpeza ao redor do piso do equipamento: 1-Limpeza do superfície utilizando pano umedecido com álcool isopropílico.', respostas)
		dic['q11'] = st11.text_input('Comentário     ', "")
		dic['q12'] = st12.selectbox('Limpeza Balancer "B": 1-Limpeza do superfície utilizando pano umedecido com álcool isopropílico.', respostas)
		dic['q13'] = st13.text_input('Comentário      ', "")
		dic['q14'] = st14.selectbox('Limpeza do visor da estação de aplicação de vedante: 1-Limpeza do superfície utilizando pano umedecido com álcool isopropílico.', respostas)
		dic['q15'] = st15.text_input('Comentário       ', "")
		dic['q16'] = st16.selectbox('Limpeza nos furos do Hopper: 1-Limpeza utilizando pano umedecido com álcool isopropílico.', respostas)
		dic['q17'] = st17.text_input('Comentário        ', "")
		submitted = st.form_submit_button('Enviar formulário')
		
	# Envio do formulário
	if submitted:
		pass
		# Limpa cache
		caching.clear_cache()
		
		# Transforma dados do formulário em um dicionário
		keys_values = dic.items()
		new_d = {str(key): str(value) for key, value in keys_values}

		# Verifica campos não preenchidos e os modifica
		for key, value in new_d.items():
			if (value == '') or value == '[]':
				new_d[key] = '-'
		
		# Dfine o nome do documento a ser armazenado no banco
		val_documento = new_d['linha'] + new_d['equipamento'].replace(" ", "") + new_d['data'] + new_d['hora'] 		#posso colocar como data+turno

		# Armazena 5-Poruqes no banco
		doc_ref = db.collection("5porques_2").document(val_documento)
		doc_ref.set(new_d)
				
######################################################################################################
                                           #Main
######################################################################################################

if __name__ == '__main__':
	# Carrega dados do firebase
	usuarios_fb = load_usuarios()

	# Constantes
	turnos = ['Turno A', 'Turno B', 'Turno C']
	nomes = ['Mario', 'Ivan', 'Camila', 'Gilver', 'Ercílio', 'Thiago']

	# Imagem
	col1_, col2_, col3_ = st.beta_columns([1,1,1])
	col1_.write('')
	col2_.image('Ambev.jpeg', width=250)
	col3_.write('')

	# Lista vazia para input dos dados do formulário
	dic = {} #dicionario

	##################################################################################################
	#			Definiçào das páginas
	##################################################################################################
	
	if func_escolhida == 'Liner diário':
		st.subheader('Liner diário')
		Liner_diario()
		
	if func_escolhida == 'Liner semanal':
		st.subheader('Liner semanal')
		
	if func_escolhida == 'Shell diário':
		st.subheader('Shell diário')
		
	if func_escolhida == 'Shell semanal':
		st.subheader('Shell semanal')
		
	if func_escolhida == 'Autobagger diário':
		st.subheader('Autobagger diário')
		
	if func_escolhida == 'Autobagger semanal':
		st.subheader('Autobagger semanal')
		
	if func_escolhida == 'Autobagger Mensal':
		st.subheader('Autobagger Mensal')
		
	if func_escolhida == 'Conversion diário':
		st.subheader('Conversion diário')
		
	if func_escolhida == 'Conversion semanal':
		st.subheader('Conversion semanal')
		
	if func_escolhida == 'Conversion mensal':
		st.subheader('Conversion mensal')
		
	if func_escolhida == 'Balacer diário':
		st.subheader('Balacer diário')
		
	if func_escolhida == 'Balancer semanal':
		st.subheader('Balancer semanal')
		
	if func_escolhida == 'Estatisticas':
		st.subheader('Estatisticas')
		
	if func_escolhida == 'Visualizar formulários':
		st.subheader('Visualizar formulários')
				
	if func_escolhida == 'Suporte Engenharia':
		st.subheader('Suporte da aplicação 5-Porques')
		
		# Campo para preenchimento de mensagem
		mensagem_suporte = st.text_input('Preencha o campo abaixo para reportar erros ou sugerir melhorias')
		
		# Campo para email
		email_contato = st.text_input('E-mail para contato (Opcional)')
		
		# Montagem da mensagem
		mensagem = mensagem_suporte + '\n\n' + email_contato
		
		# Envio da mensagem
		enviar_suporte = st.button('Enviar e-mail para suporte')
		if enviar_suporte:
			if mensagem_suporte != '':
				send_email('BRMAI0513@ambev.com.br', 4, '', mensagem, 0)
			else:
				st.error('Preencher a mensagem')
		
		st.subheader('Gestão da aplicação')
		
		# Reseta cache para refazer leitura dos bancos
		reset_db = st.button('Atualizar base de dados')
		if reset_db:
			caching.clear_cache()
		
