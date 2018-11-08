import pandas as pd
import requests
import json
import os, sys
from time import sleep

file_cnpjs = 'cnpjs.csv'
file_ceapd = 'ceapd_2017.csv'
url = 'https://www.receitaws.com.br/v1/cnpj/:cnpj'
data = None
sleep_secs = 60


# Cria arquivo de CNPJs únicos ou lê caso já exista
if os.path.isfile(file_cnpjs):
	data = pd.read_csv(file_cnpjs, dtype = str)
elif os.path.isfile(file_ceapd):
	ceapd = pd.read_csv(file_ceapd, sep = ';', dtype = str)
	cnpjs = ceapd['txtCNPJCPF'].unique()

	d = { 'cnpj' : cnpjs,
		  'razao_social' : '' * len(cnpjs),
		  'nome_fantasia' : '' * len(cnpjs),
		  'uf' : '' * len(cnpjs),
		  'municipio' : '' * len(cnpjs),
		  'cep' : '' * len(cnpjs),
		  'data_abertura' : '' * len(cnpjs),
		  'situacao' : '' * len(cnpjs)}

	data = pd.DataFrame(data = d)
	data.to_csv(file_cnpjs, index = False)


# Verifica os CNPJs com informações em branco para atualizar
for idx, row in data.iterrows():
	if pd.isnull(row['razao_social']):
		r = requests.get(url.replace(':cnpj', str(row['cnpj'])))

		while r.status_code != 200:
			print('Bad request: ' + r.text)
			data.to_csv(file_cnpjs, index = False)

			print('Sleeping for ' + str(sleep_secs) + ' seconds...')
			sleep(sleep_secs)			
			r = requests.get(url.replace(':cnpj', str(row['cnpj'])))

		cnt = r.json()

		if cnt['status'] != 'ERROR':
			data.loc[idx,] = [row['cnpj'], cnt['nome'], cnt['fantasia'], cnt['uf'], \
							  cnt['municipio'], cnt['cep'], cnt['abertura'], cnt['situacao']]
			print('Updated CNPJ ' + row['cnpj'] + ' - ' + cnt['nome'])
		else:
			print('Request error: ' + cnt['message'])
