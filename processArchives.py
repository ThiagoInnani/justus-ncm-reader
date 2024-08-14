import os
import xml.etree.ElementTree as ET
import fileAlteration

import databaseOperations

class ProcessXmls:
    def __init__(self):
        super().__init__()
        self.tableData = []
        self.db_ops = databaseOperations.DatabaseOperations()

    def openXmlFile(self):
        diretorio = fileAlteration.FileAlteration.selectFileExplorer()
        if not diretorio:
            return

        arquivos_xml = [os.path.join(diretorio, f) for f in os.listdir(diretorio) if f.endswith('.xml')]
        self.tableData = []

        ns = {"": "http://www.portalfiscal.inf.br/nfe"}
        self.db_ops.connect_to_database()
        for arquivo in arquivos_xml:
            try:
                tree = ET.parse(arquivo)
                root = tree.getroot()
                
                nota_num = root.find('.//nNF', ns)
                #xproduct = root.find('.//xProd', ns)
                xproduct_list = [xproduct.text for xproduct in root.findall('.//xProd', ns)]
                #cfop = root.find('.//CFOP', ns)
                cfop_list = [cfop.text for cfop in root.findall('.//CFOP', ns)]
                ncm_list = [ncm.text for ncm in root.findall('.//NCM', ns)]
                
                for i in range(len(ncm_list)):
                    xproduct = xproduct_list[i] if i < len(xproduct_list) else ''
                    cfop = cfop_list[i] if i < len(cfop_list) else ''
                    ncm = ncm_list[i]
                    descricao_ncm = ProcessXmls.get_ncm_description(self, ncm)
                    self.tableData.append([nota_num.text, xproduct, ncm, cfop, descricao_ncm])

            except ET.ParseError:
                print(f"Erro ao parsear o arquivo {arquivo}")
        self.db_ops.save_and_close()
        self.table_frame.clean_table()
        self.table_frame.add_item(self.tableData)

    def get_ncm_description(self, ncm_code):
        
        query = f"SELECT Descricao FROM Nomenclaturas WHERE Codigo = '{ncm_code}'"
        result = self.db_ops.execute_command(query)

        return result[0][0] if result else 'Descrição não encontrada'

    def reviewXmlFile(self):
        filter_values = self.filter_frame.get_values()
        print(filter_values)
        filter_values = [value for value in filter_values if value]  # Remove campos vazios

        if not filter_values:  # Se todos os campos estiverem vazios, mostra todos os dados
            filtered_data = self.tableData
        else:
            filtered_data = []
            for row in self.tableData:
                ncm = row[2]
                if ncm not in filter_values:
                    filtered_data.append(row)

        self.table_frame.clean_table()
        self.table_frame.add_item(filtered_data)
