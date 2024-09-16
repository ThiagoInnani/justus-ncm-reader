import os
import xml.etree.ElementTree as ET
from tkinter import messagebox


import fileAlteration
import databaseOperations
import baseIcms
import cfopEquivalent

class ProcessXmls:
    def __init__(self):
        super().__init__()
        self.tableData = []
        self.filtered_data = []
        self.db_ops = databaseOperations.DatabaseOperations()

    def openXmlFile(self):
        diretorio = fileAlteration.FileAlteration.selectFileExplorer()
        if not diretorio:
            return

        arquivos_xml = [os.path.join(diretorio, f) for f in os.listdir(diretorio) if f.endswith('.xml')]
        self.tableData = []
        self.support_data = []

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
                # Busca a UF no bloco 'dest' ou 'enderEmit' se não encontrar
                uf_list = root.find('.//dest//UF', ns)

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
                    picms = cst_list[i] if i < len(picms_list) else ''
                    uf = uf_list_text if uf_list_text else ''
                    status = ''

                    self.tableData.append([nota_num.text, xproduct, ncm, cfop, csosn_cst, descricao_ncm, status])
                    self.support_data.append([picms, uf])

            except ET.ParseError:
                print(f"Erro ao parsear o arquivo {arquivo}")

        self.filtered_data = self.tableData
        self.db_ops._save_connection()
        self.table_frame.clean_table()
        self.table_frame.add_item(self.tableData)

        print(f'Cfop_list = {cfop_list}')
        if int(cfop_list[0]) >= 5000:
            self.mainButton_frame.buttons[6].select()
            return
        if int(cfop_list[0]) < 5000:
            self.mainButton_frame.buttons[6].deselect()

    def get_ncm_description(self, ncm_code):
        query = f"SELECT description FROM Nomenclaturas WHERE id = '{ncm_code}'"
        result = self.db_ops.execute_command(query)

        return result[0][0] if result else 'Descrição não encontrada'

    def reviewXmlFile(self):
        filter_values = self.filter_frame.get_values()
        self.filtered_data = self.tableData

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
            fields = ["N° da nota", "Produto", "NCM(s)", "CFOP", "CST/CSOSN", "Descrição", "Status"]
            index = fields.index(field)
            return compare(row[index], operation, value)

        for i, (logic, field, operation, value) in enumerate(filter_values):
            if field and operation and value:
                if i == 0:
                    self.filtered_data = [row for row in self.filtered_data if apply_filter(row, field, operation, value)]
                elif logic == "E":
                    self.filtered_data = [row for row in self.filtered_data if apply_filter(row, field, operation, value)]
                elif logic == "OU":
                    additional_data = [row for row in self.tableData if apply_filter(row, field, operation, value)]
                    self.filtered_data.extend(additional_data)
                    self.filtered_data = [list(x) for x in set(tuple(x) for x in self.filtered_data)]

        self.table_frame.clean_table()
        self.table_frame.add_item(self.filtered_data)

    def analyze_button_click_event(self):
        self.filtered_data = []
        print(f'TableData: {self.tableData}, linhas: {list(enumerate(self.tableData))}')
        for i, (row, support) in enumerate(zip(self.tableData, self.support_data)):
            print(f'index: {i}')
            picms = support[0]  # Obtém o valor picms da lista support_data
            ncm_value = row[2]  # Assumindo que NCM está na coluna 2
            cfop_value = row[3]  # Assumindo que CFOP está na coluna 3
            uf_value = support[1]  # Obtém o valor uf da lista support_data
            cst_csosn_value = row[4]  # Assumindo que CST/CSOSN está na coluna 4
            status = ""

            # Processa e compara os dados como antes
            picms = float(picms)
            print(f'PICMS: {picms}, NCM: {ncm_value}, CFOP: {cfop_value}, UF: {uf_value}, CST/CSOSN: {cst_csosn_value}')
            db_base_icms = baseIcms.BaseICMS.get_base_icms(ncm_value, cfop_value, uf_value, cst_csosn_value)

            print(f'DB_BASE_ICMS_ANTES: {db_base_icms}')
            var_aux = 0

            if not db_base_icms:
                status = 'Base ICMS sem valor no sistema'
                print('Base ICMS sem valor no sistema')
                var_aux = 1
            else:
                db_base_icms = float(db_base_icms[0][0])
                print(f'db_base_icms_DEPOIS: {db_base_icms}')
                if db_base_icms != picms:
                    status = f'ERRO: Alíq. ICMS da nota ({picms}) deve ser {db_base_icms}'
                    print('Diferentes!!')
                    var_aux = 1
                else:
                    status = 'Correto'
                    print('Iguais!!')
                    var_aux = 0

            row[6] = status

            if status and var_aux:
                self.filtered_data.append(row)

        if self.filtered_data:
            self.table_frame.clean_table()
            self.table_frame.add_item(self.filtered_data)
        else:
            messagebox.showerror('ERRO: Tabela sem dados', 'ERRO: Sem dados na tabela para filtrar')

    def cfop_swap(self):
        cfop_list = self.table_frame.get_tree(3)
        print(f'Tree(3): {cfop_list}')

        if cfop_list:
            cfop_equivalent = cfopEquivalent.CFOPEquivalent.get_cfop_equivalent(self, cfop_list)
            for i, row in enumerate(self.filtered_data):
                row[3] = cfop_equivalent[i]
            '''
            cfop_table_data = []
            for i, row in enumerate(self.tableData):
                cfop_table_data.append(row[3])

            cfop_table_data_equivalent = cfopEquivalent.CFOPEquivalent.get_cfop_equivalent(self, cfop_table_data)
            for i, row in enumerate(self.tableData):
                row[3] = cfop_table_data_equivalent[i]
            '''
            self.table_frame.clean_table()
            self.table_frame.add_item(self.filtered_data) 
        else:
            messagebox.showerror('ERRO: Tabela sem dados', 'ERRO: Sem dados na tabela para filtrar')
            self.mainButton_frame.buttons[6].deselect()
        
        status_list = self.table_frame.get_tree(6)
        if status_list[0] != "":
            ProcessXmls.analyze_button_click_event(self)

            