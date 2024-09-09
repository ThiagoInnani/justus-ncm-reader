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
                xproduct_list = [xproduct.text for xproduct in root.findall('.//xProd', ns)]
                cfop_list = [cfop.text for cfop in root.findall('.//CFOP', ns)]
                ncm_list = [ncm.text for ncm in root.findall('.//NCM', ns)]
                csosn_list = [csosn.text for csosn in root.findall('.//CSOSN', ns)]
                cst_list = [produto.find('.//CST', ns).text for produto in root.findall('.//det', ns) if produto.find('.//CST', ns) is not None]

                for i in range(len(ncm_list)):
                    xproduct = xproduct_list[i] if i < len(xproduct_list) else ''
                    cfop = cfop_list[i] if i < len(cfop_list) else ''
                    csosn_cst = csosn_list[i] if csosn_list else cst_list[i]
                    ncm = ncm_list[i]
                    descricao_ncm = ProcessXmls.get_ncm_description(self, ncm)
                    self.tableData.append([nota_num.text, xproduct, ncm, cfop, csosn_cst, descricao_ncm])

            except ET.ParseError:
                print(f"Erro ao parsear o arquivo {arquivo}")
        self.db_ops._save_connection()
        self.table_frame.clean_table()
        self.table_frame.add_item(self.tableData)

    def get_ncm_description(self, ncm_code):
        
        query = f"SELECT description FROM Nomenclaturas WHERE id = '{ncm_code}'"
        result = self.db_ops.execute_command(query)

        return result[0][0] if result else 'Descrição não encontrada'

    def reviewXmlFile(self):
        filter_values = self.filter_frame.get_values()
        filtered_data = self.tableData

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
            fields = ["N° da nota", "Produto", "NCM(s)", "CFOP", "CST/CSOSN", "Descrição"]
            index = fields.index(field)
            return compare(row[index], operation, value)

        for i, (logic, field, operation, value) in enumerate(filter_values):
            if field and operation and value:
                if i == 0:
                    filtered_data = [row for row in filtered_data if apply_filter(row, field, operation, value)]
                elif logic == "E":
                    filtered_data = [row for row in filtered_data if apply_filter(row, field, operation, value)]
                elif logic == "OU":
                    additional_data = [row for row in self.tableData if apply_filter(row, field, operation, value)]
                    filtered_data.extend(additional_data)
                    filtered_data = [list(x) for x in set(tuple(x) for x in filtered_data)]

        self.table_frame.clean_table()
        self.table_frame.add_item(filtered_data)

