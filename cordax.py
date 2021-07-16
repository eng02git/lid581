import streamlit as st
import pandas as pd 
import numpy as np
from itertools import cycle
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import streamlit.components.v1 as components
import base64
import json
import smtplib
import time
import datetime
import time
from datetime import  date

from google.cloud import firestore
from google.oauth2 import service_account

######################################################################################################
				#Configurações da página
######################################################################################################

st.set_page_config(
     page_title="Cordax",
     layout="wide",
)

######################################################################################################
				#Configurando acesso ao firebase
######################################################################################################
textkey_2 = """{\n  \"type\": \"service_account\",\n  \"project_id\": \"lid-forms\",\n  \"private_key_id\": \"de4fcc45d24308eaa9101b4d4d651c0e1f1c192e\",\n  \"private_key\": \"-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCQL7wXeUw7bxgB\\n0kivlcQyVhrBW+ufV1cgv1ySMjqhBxuGK6/4x3Po2/a/phcPxYN7hfsmcq1ZmCMx\\nMHU2TicbRtxA0XqXCi1wfbHYUQk49fT7SJRI9R5C3cCq6hicAYXAdC0BCqvXcmB7\\n8JSRBhdiLmMziQlcb1OkKtTrMkg8/2xhPXVQ8snBzYxrcpGL70IUMW/4FKdABBxg\\ne1uV8Xs11e3pWqQVNxd6FKnanBg/88/wleMb0wZRc0ULhrVEJCFYX8ycjLgoMn4+\\nKNDXdl7zs41IoEdSqs9VTjrrJFGPE6lxUO/qb4FE76qU/4BEmyXjiggLFpu+mjOO\\n0JvN2E6xAgMBAAECggEAB0NISQcUoR0doKCG2xqtqSVvhT7hQFj7bAxc7YZMhWZL\\na3eRjnP+3C4RoKINS6o/eb42zOnTiThMdC1Z3MmUrF87jU5KoQdjtjoL9nalLXKC\\nNmgiWVxze5saRIxfKfiPqVvmFRqEVmljVSA6COYS0SC/YXitI96oYBQXk939XTPN\\nz5LxXyubM00vK1MgdCw8lMajE0l1w7FkqyupolStYeX8l23Kfp6o/Kte/IdZpWR6\\ngefnMEvVCUorNjpuFlvOQrxgm6ygAsuFglRshPqXzUS9761TyBcKPdr4znAA3gns\\nrEqi+6Lrh9xz+t5K8aHodjzvNHQ9yjAiGZHZsoO5WQKBgQDK7IXXslOz7lJ5ZLSl\\njJRtLbs6C0cOmmf+7UQXJmtsL0OHsYgWMzTtrqEo2EqCq0C8UCvCCyUs/d0LrwU4\\n40U9+CUYQMP9PtezqK23XFuLg7upJzY2AH3mNkRr8CMCuyWisw+W/o8QF6jUijtP\\nT0JIrdYyfrGUEx+JnogW4pW+pQKBgQC15j3D/0zRBaM71DjXGc9UDX2M7V56e07S\\nsEJvvzTPbh86VQ3sZTVPoC1jXhV/IzyT3+uxMvrNhEwP15pQzLkMW2J/uZzI3Q+L\\nvhUl6Lk8RIMTFFO2CkNfugPZwPmUxe9/Cu0y9AbeBR7v1zouxFkaNAEkMOrpQ3Ds\\nDwWqLbL+HQKBgAlzMlh1KYi7lIOquO7suQzMkGeHluuLLUSl8AHT/DSxjseG8Pt3\\nrwNSmpa4W9/x8bXTVfZXZofN2rlskSWxD8xu/es/OOFWR91KAa0EVA8PN3INLW0e\\nYL6T0GPmbvr1lC8bf6JcgHUTZP1g4poy6rdPwSXg2Iw4x8M06smGC8sxAoGBAKAx\\nKGwXxhq+kEb8WyJ0BHbNeqhF01KijYRW3etzxJp5LN8+UIjDiPOa6N392YiiC5Nf\\nPD5N2zprLGE3Sxulb8JGKLS7TixHIo261P0RuzAsVhLTb/V9jGAdfY6juCkhOA32\\nHXcmGXYlpF0senz9RkshSXAJ9JeBYU1C3YZFwMCxAoGAaFm980daY3c3P/6mSWC6\\nTImniGbAUbUNFxpC3VUcDTtaC4WtGNe5vcVbvPxWXqBTPo8S7q5eq0JWJipfy4Gp\\ncU3+qMM+Z9jLwasmwKAjN066BH1gPC6AB9m+T2U/N6EY1mTp+DEYfFGhwJCB9coC\\nJ2krpcK4f+zsV7XGgnwUhic=\\n-----END PRIVATE KEY-----\\n\",\n  \"client_email\": \"firebase-adminsdk-r4dlw@lid-forms.iam.gserviceaccount.com\",\n  \"client_id\": \"101767194762733526952\",\n  \"auth_uri\": \"https://accounts.google.com/o/oauth2/auth\",\n  \"token_uri\": \"https://oauth2.googleapis.com/token\",\n  \"auth_provider_x509_cert_url\": \"https://www.googleapis.com/oauth2/v1/certs\",\n  \"client_x509_cert_url\": \"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-r4dlw%40lid-forms.iam.gserviceaccount.com\"\n}\n"""


# Pega as configurações do banco do segredo
key_dict = json.loads(textkey_2)
creds = service_account.Credentials.from_service_account_info(key_dict)

# Seleciona o projeto
db = firestore.Client(credentials=creds, project="lid-forms")

###########################################################################################################################################
#####                    			funcoes                                                                            #########
###########################################################################################################################################

# Define cores para os valores validos ou invalidos
def color(val):
	if val == 'invalido':
		color = 'red'
	else:
		color = 'white'
	return 'background-color: %s' % color
	
#leitura de dados do banco
@st.cache
def load_colecoes(colecao):
	# dicionario vazio
	dicionario = {}
	index = 0
	
	# Define o caminho da coleção do firebase
	posts_ref = db.collection(colecao)	
	
	# Busca todos os documentos presentes na coleção e salva num dataframe
	for doc in posts_ref.stream():
		dic_auxiliar = doc.to_dict()
		dicionario[str(index)] = dic_auxiliar
		index += 1
		
	df = pd.DataFrame.from_dict(dicionario)
	df = df.T
	#df.reset_index(inplace=True)
	#df.drop('index', axis=1, inplace=True)
	
	df = df.reindex(columns=['Medidas', 'L', 'V'])
	df['data'] = pd.to_datetime(df['data']).dt.date
	
	return data_user

###########################################################################################################################################
#####                    			cofiguracoes aggrid							                #######
###########################################################################################################################################
def config_grid(height, df, lim_min, lim_max):
	sample_size = 12
	grid_height = height

	return_mode = 'AS_INPUT'
	return_mode_value = DataReturnMode.__members__[return_mode]

	update_mode = 'VALUE_CHANGED'
	update_mode_value = GridUpdateMode.__members__[update_mode]

	#enterprise modules
	enable_enterprise_modules = False
	enable_sidebar = False

	#features
	fit_columns_on_grid_load = False
	enable_pagination = False
	paginationAutoSize = False
	use_checkbox = False
	enable_selection = False
	selection_mode = 'single'
	rowMultiSelectWithClick = False
	suppressRowDeselection = False

	if use_checkbox:
		groupSelectsChildren = True
		groupSelectsFiltered = True

	#Infer basic colDefs from dataframe types
	gb = GridOptionsBuilder.from_dataframe(df)

	#customize gridOptions
	gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
	gb.configure_column("Medidas", editable=False)
	gb.configure_column('L', editable=False)
	gb.configure_column('V', type=["numericColumn"], precision=5)

	#configures last row to use custom styles based on cell's value, injecting JsCode on components front end
	func_js = """
	function(params) {
	    if (params.value > %f) {
		return {
		    'color': 'black',
		    'backgroundColor': 'orange'
		}
	    } else if(params.value <= %f) {
		return {
		    'color': 'black',
		    'backgroundColor': 'green'
		}
	    } else if((params.value <= %f) && (params.value >= %f)) {
		return {
		    'color': 'black',
		    'backgroundColor': 'white'
		}
	    } else {
		return {
		    'color': 'black',
		    'backgroundColor': 'red'
		} 
	    } 
	};
	"""%(lim_max, lim_min, lim_max, lim_min)
	
	cellsytle_jscode = JsCode(func_js)

	gb.configure_column('V', cellStyle=cellsytle_jscode)

	if enable_sidebar:
		gb.configure_side_bar()

	if enable_selection:
		gb.configure_selection(selection_mode)
	if use_checkbox:
		gb.configure_selection(selection_mode, use_checkbox=True, groupSelectsChildren=groupSelectsChildren, groupSelectsFiltered=groupSelectsFiltered)
	if ((selection_mode == 'multiple') & (not use_checkbox)):
		gb.configure_selection(selection_mode, use_checkbox=False, rowMultiSelectWithClick=rowMultiSelectWithClick, suppressRowDeselection=suppressRowDeselection)

	if enable_pagination:
		if paginationAutoSize:
			gb.configure_pagination(paginationAutoPageSize=True)
		else:
			gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=paginationPageSize)

	gb.configure_grid_options(domLayout='normal')
	gridOptions = gb.build()
	return gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules

###########################################################################################################################################
#####                    			Teste											########
###########################################################################################################################################

# definicao das telas da aplicacao
telas = ['Kiss Block (1)','Kiss Block (2)','Bubble From (1)','Bubble From (2)','Bubble From (3)','1st Rivet (1)','1st Rivet (2)','2nd Rivet (1)','2nd Rivet (2)','Score (1)','Score (2)','Panel Form (1)','Panel Form (2)','Panel Form (3)','Panel Form (4)','Strake (1)','Strake (2)']

# Menu externo ao formulario
aba, i01, i02 = st.beta_columns([4,10,4])	
sel_tela = aba.selectbox('Selecione o ferramental', options=telas)
nomes = ['Mario', 'Carvalho']
	
# Tela Kiss Block	
if sel_tela == 'Kiss Block (1)':
	df = pd.DataFrame()

	valor = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
	linhas = [ 'A', 'B', 'C', 'D', 'A', 'B', 'C', 'D', 'A', 'B', 'C', 'D', 'A', 'B', 'C', 'D', 'A', 'B', 'C', 'D']
	val_max = [50, 50, 50, 50, 50]
	val_min = [0.1, 0.1, 0.1, 0.1, 0.1]
	medidas =     ['SPACER LOWER CAP',
		  	'SPACER LOWER CAP',
		  	'SPACER LOWER CAP',
		  	'SPACER LOWER CAP',
		  	'SPACER UPPER BLANK BEAD',
		  	'SPACER UPPER BLANK BEAD',
		  	'SPACER UPPER BLANK BEAD',
		  	'SPACER UPPER BLANK BEAD',
		  	'TOOLING PLATE',
		  	'TOOLING PLATE',
		  	'TOOLING PLATE',
		  	'TOOLING PLATE',
		  	'SPACER UPPER CAP',
		  	'SPACER UPPER CAP',
		  	'SPACER UPPER CAP',
		  	'SPACER UPPER CAP',
		  	'SPACER LOWER RIVET INSERT',
		  	'SPACER LOWER RIVET INSERT',
		  	'SPACER LOWER RIVET INSERT',
		  	'SPACER LOWER RIVET INSERT'
		  	]
	try:
		df = load_colecoes(medidas, 'Kiss Block (1)')
	except:
		d = {'Medidas': medidas, 'L': linhas, 'V': valor}
		df = pd.DataFrame(data=d)

	# carrega pagina html
	htmlfile = open('teste.html', 'r', encoding='utf-8')
	source = htmlfile.read()
	
	# carrega imagem da tela do cordax
	file_ = open("Untitled.png", "rb")
	contents = file_.read()
	data_url = base64.b64encode(contents).decode("utf-8")
	file_.close()
	
	# cria dicionario vazio
	dic = {} 
		
	#with st.form('form'):
	
	# Input de informacoes de nome e data
	nome = i01.selectbox('Nome do colaborador:', nomes) 
	data = i02.date_input('Data:')
	
	# define as colunas da pagina
	t1, html, t2 = st.beta_columns([4,10,4])
	

	with t1:
		df_validacao = pd.DataFrame()
		medida = ['SPACER LOWER CAP', 'SPACER UPPER BLANK BEAD', 'TOOLING PLATE', 'SPACER UPPER CAP', 'SPACER LOWER RIVET INSERT']
		  	
		for (mi, ma, med) in zip(val_min, val_max, medida):
			
			 gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(150, df, mi, ma)
			 response = AgGrid(
			    df[df['Medidas'] == med], 
			    gridOptions=gridOptions,
			    height=grid_height, 
			    width='100%',
			    data_return_mode=return_mode_value, 
			    update_mode=update_mode_value,
			    fit_columns_on_grid_load=fit_columns_on_grid_load,
			    allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
			    enable_enterprise_modules=enable_enterprise_modules)
			 df_validacao = pd.concat([df_validacao, response['data']])
		
		df_validacao['V'] = pd.to_numeric(df_validacao['V'], errors='coerce')
		
		if df_validacao['V'].isnull().sum() > 0:
			t2.error('Caracter invalido no campo Valor')
		else:
			t2.write('Avalicao das medidas')
				
			df_group = df_validacao[['L', 'V']].groupby(['L']).sum() 
			df_group['Max'] = [ 123, 4321, 123, 4321]
			df_group['Min'] = [ 13, 43, 3, 1]
			df_group['Resultado'] = np.where(((df_group['V'] < df_group['Max']) & (df_group['V'] > df_group['Min'])), 'valido', 'invalido')
			t2.write(df_group.style.applymap(color, subset=['Resultado']))
			
			# Preparando dados para escrita no banco
			
			dic = {}
			for index, row in df_validacao.iterrows():
				chave = row['Medidas'] + '__' + row['L']
				dic[chave] = str(row['V'])
			dic['Nome'] = nome
			dic['Data'] = str(data)
			st.write(dic)
			
			

	# HTML: html com imagens e dados				
	with html:
		components.html(source.format(image=data_url,
					       v0=df.iloc[0,0],
					       v1=df.iloc[1,0],
					       v2=df.iloc[2,0],
					       v3=df.iloc[3,0],
					       v4=df.iloc[4,0],
					       v5=df.iloc[5,0],
					       v6=df.iloc[6,0],
					       v7=df.iloc[7,0],
					       v8=df.iloc[8,0],
					       v9=df.iloc[9,0],
					       v10=df.iloc[10,0],
					       v11=df.iloc[11,0],
					       v12=df.iloc[12,0],
					       v13=df.iloc[13,0],
					       v14=df.iloc[14,0],
					       v15=df.iloc[15,0],
					       v16=df.iloc[16,0],
					       v17=df.iloc[17,0],
					       v18=df.iloc[18,0],
					       v19=df.iloc[19,0]),
					        height=1300)
	
	# coluna 2: tabela para preenchimento e avalicao dos inputs




