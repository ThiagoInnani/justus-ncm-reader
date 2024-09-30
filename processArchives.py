import os
import xml.etree.ElementTree as ET
import copy
from tkinter import messagebox


import fileAlteration
import databaseOperations
import baseIcms
import cfopEquivalent

class ProcessXmls:
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.table_data = []
        self.filtered_data = []
        self.original_data = []
        self.is_switch_activated_once = False
        self.is_analyze_button_active = False
        self.is_filter_button_active = True
        self.db_ops = databaseOperations.DatabaseOperations()

    def openXmlFile(self):
        diretorio = fileAlteration.FileAlteration.selectFileExplorer()
        if not diretorio:
            return

        arquivos_xml = [os.path.join(diretorio, f) for f in os.listdir(diretorio) if f.endswith('.xml')]
        self.table_data = []
        self.support_data = []
        self.due_value = 0

        ns = {"": "http://www.portalfiscal.inf.br/nfe"}
        self.db_ops.connect_to_database()
        for arquivo in arquivos_xml:
            try:
                tree = ET.parse(arquivo)
                root = tree.getroot()
                
                nota_num = root.find('.//nNF', ns)
                xproduct_list = [xproduct.text for xproduct in root.findall('.//xProd', ns)]
                cfop_list = [cfop.text for cfop in root.findall('.//CFOP', ns)]
                ncm_list = [ncm.text for ncm in root.findall('.//NCM', ns)]
                csosn_list = [csosn.text for csosn in root.findall('.//CSOSN', ns)]
                cst_list = [produto.find('.//CST', ns).text for produto in root.findall('.//det', ns) if produto.find('.//CST', ns) is not None]
                picms_list = [produto.find('.//pICMS', ns).text if produto.find('.//pICMS', ns) is not None else '0' for produto in root.findall('.//det', ns)]
                due_list = [produto.find('.//vICMS', ns).text if produto.find('.//vICMS', ns) is not None else '0' for produto in root.findall('.//det', ns)]
                nf_total_value_list = [produto.find('.//vProd', ns).text for produto in root.findall('.//det', ns) if produto.find('.//vProd', ns) is not None]
                # Busca a UF no bloco 'dest' ou 'enderEmit' se não encontrar
                uf_list = root.find('.//dest//UF', ns)
                print(f'picms: {picms_list}')
                # Se não encontrar no 'dest', busca no 'enderEmit'
                if uf_list is None:
                    uf_list = root.find('.//enderEmit//UF', ns)

                # Obtém o valor do texto, se encontrado
                if uf_list is not None:
                    uf_list_text = uf_list.text

                for i in range(len(ncm_list)):
                    xproduct = xproduct_list[i] if i < len(xproduct_list) else ''
                    cfop = cfop_list[i] if i < len(cfop_list) else ''
                    csosn_cst = csosn_list[i] if csosn_list else cst_list[i]
                    ncm = ncm_list[i]
                    descricao_ncm = ProcessXmls.get_ncm_description(self, ncm)
                    picms = picms_list[i] if i < len(picms_list) else ''
                    uf = uf_list_text if uf_list_text else ''
                    status = ''
                    credit = ''
                    due = due_list[i] if i < len(due_list) else ''
                    nf_total_value = nf_total_value_list[i] if i < len(nf_total_value_list) else ''

                    self.table_data.append([nota_num.text, xproduct, ncm, cfop, csosn_cst, descricao_ncm, status, credit, due])
                    self.support_data.append([picms, uf, nf_total_value])

                    self.due_value += float(due)
            except ET.ParseError:
                print(f"Erro ao parsear o arquivo {arquivo}")

        self.filtered_data = self.table_data
        self.db_ops._save_connection()
        self.master.table_frame.clean_table()
        self.master.table_frame.add_item(self.table_data)
        self.master.analyze_button_frame.due_money_value.configure(text=self.due_value)
        self.original_data = copy.deepcopy(self.table_data)

        if int(cfop_list[0]) >= 5000:
            self.master.analyze_button_frame.equivalent_switch.select()
            return
        if int(cfop_list[0]) < 5000:
            self.master.analyze_button_frame.equivalent_switch.deselect()

    def get_ncm_description(self, ncm_code):
        query = f"SELECT description FROM Nomenclaturas WHERE id = '{ncm_code}'"
        result = self.db_ops.execute_command(query)

        return result[0][0] if result else 'Descrição não encontrada'

    def reviewXmlFile(self):
        filter_values = self.master.filter_frame.get_values()
        self.filtered_data = self.table_data

        def compare(value, operation, target):
            if operation == "é igual a":
                return value == target
            elif operation == "é diferente de":
                return value != target
            elif operation == "maior que":
                return value > target
            elif operation == "menor que":
                return value < target
            elif operation == "contém":
                return target in value
            return False

        def apply_filter(row, field, operation, value):
            fields = ["N° da nota", "Produto", "NCM(s)", "CFOP", "CST/CSOSN", "Descrição", "Status", "Creditado", "Devido"]
            index = fields.index(field)
            return compare(row[index], operation, value)

        for i, (logic, field, operation, value) in enumerate(filter_values):
            if field and operation and value:
                if i == 0:
                    self.filtered_data = [row for row in self.filtered_data if apply_filter(row, field, operation, value)]
                elif logic == "E":
                    self.filtered_data = [row for row in self.filtered_data if apply_filter(row, field, operation, value)]
                elif logic == "OU":
                    additional_data = [row for row in self.table_data if apply_filter(row, field, operation, value)]
                    self.filtered_data.extend(additional_data)
                    self.filtered_data = [list(x) for x in set(tuple(x) for x in self.filtered_data)]

        self.master.table_frame.clean_table()
        self.master.table_frame.add_item(self.filtered_data)
        self.is_analyze_button_active = False
        self.is_filter_button_active = True

    def analyze_button_click_event(self):
        self.filtered_data = []
        print(f'table_data: {self.table_data}, linhas: {list(enumerate(self.table_data))}')

        self.credit_value = 0
        if self.table_data:
            for i, (row, support) in enumerate(zip(self.table_data, self.support_data)):
                print(f'index: {i}')
                picms = support[0]  # Obtém o valor picms da lista support_data
                ncm_value = row[2]  # Assumindo que NCM está na coluna 2
                uf_value = support[1]  # Obtém o valor uf da lista support_data
                cst_csosn_value = row[4]  # Assumindo que CST/CSOSN está na coluna 4
                status = ""
                credit = ""
                nf_total = support[2] #Obtém o valor de Total da Nota 

                # Processa e compara os dados como antes
                picms = float(picms)
                print(f'PICMS: {picms}, NCM: {ncm_value}, UF: {uf_value}, CST/CSOSN: {cst_csosn_value}')
                db_base_icms = baseIcms.BaseICMS.get_base_icms(ncm_value, uf_value, cst_csosn_value)

                print(f'DB_BASE_ICMS_ANTES: {db_base_icms}')
                var_aux = False

                if not db_base_icms:
                    status = 'Base ICMS sem valor no sistema'
                    print('Base ICMS sem valor no sistema')
                    var_aux = True
                    credit = 0
                else:
                    db_base_icms = float(db_base_icms[0][0])
                    nf_total = float(nf_total)
                    print(f'db_base_icms_DEPOIS: {db_base_icms}')
                    credit = (db_base_icms/100)*nf_total
                    credit = round(credit, 2)
                    if db_base_icms != picms:
                        status = f'ERRO: Alíq. ICMS da nota ({picms}) deve ser {db_base_icms}'
                        print('Diferentes!!')
                        var_aux = True
                    else:
                        status = 'Correto'
                        print('Iguais!!')
                        var_aux = False

                row[6] = status
                row[7] = credit
                self.credit_value+=float(credit)

                if status and var_aux:
                    self.filtered_data.append(row)

        if self.filtered_data:
            self.master.table_frame.clean_table()
            self.master.table_frame.add_item(self.filtered_data)
            self.is_analyze_button_active = True
            self.is_filter_button_active = False
        else:
            messagebox.showerror('ERRO: Tabela sem dados', 'ERRO: Sem dados na tabela para filtrar')
        
        self.master.analyze_button_frame.credit_money_value.configure(text = self.credit_value)
        
    def cfop_swap(self):
        cfop_list = self.master.table_frame.get_tree(3)
        cst_csosn_list = self.master.table_frame.get_tree(4)

        if cfop_list:
            if not self.is_switch_activated_once:
                print('O switch ativou uma vez')
                cfop_equivalent = cfopEquivalent.CFOPEquivalent.get_cfop_equivalent(self, cfop_list, cst_csosn_list)
                print(f'CFOP EQUIVALENT: {cfop_equivalent}')
                for i, row in enumerate(self.filtered_data):
                    row[3] = cfop_equivalent[i]
                    
                self.master.table_frame.clean_table()
                self.master.table_frame.add_item(self.filtered_data) 
                self.is_switch_activated_once = True
            else:
                print(f'Switch voltou para o estado original')
                cfop_table_cfops = []
                print(f'Original_data: {self.original_data}')
                for i, row in enumerate(self.original_data):
                    cfop_table_cfops.append(row[3]) #CFOPs

                for i, row in enumerate(self.table_data):
                    row[3] = cfop_table_cfops[i]

                self.master.table_frame.clean_table()
                self.master.table_frame.add_item(self.table_data) 

                self.is_switch_activated_once = False

            if self.is_analyze_button_active:
                self.master.process_archive.analyze_button_click_event()
                return
            
            if self.is_filter_button_active:
                self.master.process_archive.reviewXmlFile()
                return
        else:
            messagebox.showerror('ERRO: Tabela sem dados', 'ERRO: Sem dados na tabela para filtrar')
            self.master.analyze_button_frame.equivalent_switch.deselect()
            