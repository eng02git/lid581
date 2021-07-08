import streamlit as st
import pandas as pd 
import numpy as np
from itertools import cycle
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import streamlit.components.v1 as components
import base64

st.set_page_config(
     page_title="Cordax",
     layout="wide",
)



###########################################################################################################################################
#####                    			funcooes                                                                            #########
###########################################################################################################################################

def color(val):
	if val == 'invalido':
		color = 'red'
	else:
		color = 'white'
	return 'background-color: %s' % color

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
	fit_columns_on_grid_load = True
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
	gb.configure_column("Linha", editable=False)
	gb.configure_column("Valor", type=["numericColumn"], precision=5)

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
		    'backgroundColor': 'white'
		}
	    } else {
		return {
		    'color': 'white',
		    'backgroundColor': 'darkred'
		} 
	    } 
	};
	"""%(lim_max, lim_min)
	
	cellsytle_jscode = JsCode(func_js)

	gb.configure_column("Valor", cellStyle=cellsytle_jscode)

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

telas = ['Kiss Block (1)',
	'Kiss Block (2)',
	'Bubble From (1)',
	'Bubble From (2)',
	'Bubble From (3)',
	'1st Rivet (1)',
	'1st Rivet (2)',
	'2nd Rivet (1)',
	'2nd Rivet (2)',
	'Score (1)',
	'Score (2)',
	'Panel Form (1)',
	'Panel Form (2)',
	'Panel Form (3)',
	'Panel Form (4)',
	'Strake (1)',
	'Strake (2)']

aba, i01, i02 = st.beta_columns([2,10,4])	
sel_tela = aba.selectbox('Selecione o ferramental', options=telas)
nomes = ['Mario', 'Carvalho']
	
if sel_tela == 'Kiss Block (1)':

	valor = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
	linhas = [ 'A', 'B', 'C', 'D', 'A', 'B', 'C', 'D', 'A', 'B', 'C', 'D', 'A', 'B', 'C', 'D', 'A', 'B', 'C', 'D']
	val_max = [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
	val_min = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
	medidas = ['SPACER LOWER CAP',
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

	d = {'Medidas': medidas, 'Linha': linhas, 'Valor': valor}
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
	dic['I01'] = i01.selectbox('Nome do colaborador:', nomes) 
	dic['I02'] = i02.date_input('Data:')
	
	# define as colunas da pagina
	t1, t2 = st.beta_columns([10,4])
	
	# coluna 1: html com imagens e dados				
	with t1:
		components.html(source.format(image=data_url, teste=0.0001), height=1500)
	
	# coluna 2: tabela para preenchimento e avalicao dos inputs
	with t2:
		gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(150, df, 10.0, 10.0)
		grid_response = AgGrid(
		    df[df['Medidas'] == 'SPACER LOWER CAP'], 
		    gridOptions=gridOptions,
		    height=grid_height, 
		    width='100%',
		    data_return_mode=return_mode_value, 
		    update_mode=update_mode_value,
		    fit_columns_on_grid_load=fit_columns_on_grid_load,
		    allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
		    enable_enterprise_modules=enable_enterprise_modules,
		    )
		    
		gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(150, df, 15.0, 15.0)
		grid_response = AgGrid(
		    df[df['Medidas'] == 'SPACER UPPER BLANK BEAD'], 
		    gridOptions=gridOptions,
		    height=grid_height, 
		    width='100%',
		    data_return_mode=return_mode_value, 
		    update_mode=update_mode_value,
		    fit_columns_on_grid_load=fit_columns_on_grid_load,
		    allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
		    enable_enterprise_modules=enable_enterprise_modules,
		    )
		    
		gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(150, df, 15.0, 15.0)
		grid_response = AgGrid(
		    df[df['Medidas'] == 'TOOLING PLATE'], 
		    gridOptions=gridOptions,
		    height=grid_height, 
		    width='100%',
		    data_return_mode=return_mode_value, 
		    update_mode=update_mode_value,
		    fit_columns_on_grid_load=fit_columns_on_grid_load,
		    allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
		    enable_enterprise_modules=enable_enterprise_modules,
		    )
		    
		gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(150, df, 15.0, 15.0)
		grid_response = AgGrid(
		    df[df['Medidas'] == 'SPACER UPPER CAP'], 
		    gridOptions=gridOptions,
		    height=grid_height, 
		    width='100%',
		    data_return_mode=return_mode_value, 
		    update_mode=update_mode_value,
		    fit_columns_on_grid_load=fit_columns_on_grid_load,
		    allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
		    enable_enterprise_modules=enable_enterprise_modules,
		    )
		    
		gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(150, df, 15.0, 15.0)
		grid_response = AgGrid(
		    df[df['Medidas'] == 'SPACER LOWER RIVET INSERT'], 
		    gridOptions=gridOptions,
		    height=grid_height, 
		    width='100%',
		    data_return_mode=return_mode_value, 
		    update_mode=update_mode_value,
		    fit_columns_on_grid_load=fit_columns_on_grid_load,
		    allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
		    enable_enterprise_modules=enable_enterprise_modules,
		    )
		    
		
		df_validacao = grid_response['data']
		
		df_validacao['Valor'] = pd.to_numeric(df_validacao['Valor'], errors='coerce')
		
		if df_validacao['Valor'].isnull().sum() > 0:
			t2.error('Caracter invalido no campo Valor')
		else:
			t2.write('Avalicao das medidas')
				
			df_group = df_validacao[['Linha', 'Valor']].groupby(['Linha']).sum() 
			df_group['Max'] = [ 123, 4321, 123, 4321]
			df_group['Min'] = [ 13, 43, 3, 1]
			
			df_group['Resultado'] = np.where(((df_group['Valor'] < df_group['Max']) & (df_group['Valor'] > df_group['Min'])), 'valido', 'invalido')
			t2.write(df_group.style.applymap(color, subset=['Resultado']))







