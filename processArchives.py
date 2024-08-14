import os
import xml.etree.ElementTree as ET

import fileAlteration


class ProcessXmls:
    def __init__(self):
        super().__init__()

    def openXmlFile(self):
            diretorio = fileAlteration.FileAlteration.selectFileExplorer()
            if not diretorio:
                return
            
            arquivos_xml = [os.path.join(diretorio, f) for f in os.listdir(diretorio) if f.endswith('.xml')]

            self.tableData = []

            ns = {"": "http://www.portalfiscal.inf.br/nfe"}


            for arquivo in arquivos_xml:
                tree = ET.parse(arquivo)
                root = tree.getroot()
                
                nota_num = root.find('.//nNF', ns)
                ncm_list = [ncm.text for ncm in root.findall('.//NCM', ns)]
                ncm = ', '.join(ncm_list)
                try:
                    self.tableData.append([nota_num.text, ncm])
                except:
                    continue    
            self.table_frame.clean_table()
            self.table_frame.add_item(self.tableData)
        
    def reviewXmlFile(self):
            filter_values = self.filter_frame.get_values()
            print(filter_values)
            filter_values = [value for value in filter_values if value]  # Remove campos vazios

            if not filter_values:  # Se todos os campos estiverem vazios, mostra todos os dados
                filtered_data = self.tableData
            else:
                filtered_data = []
                for row in self.tableData:
                    ncm_values = row[1].split(', ')
                    if not any(ncm in filter_values for ncm in ncm_values):
                        filtered_data.append(row)

            self.table_frame.clean_table()
            self.table_frame.add_item(filtered_data)
