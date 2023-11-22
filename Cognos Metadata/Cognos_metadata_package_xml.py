import xml.etree.ElementTree as ET
import pandas as pd
import os


### ----------------------------------- get data ------------------------------------------------
def getNamespace(elem):
    if elem.tag[0] == "{":
        uri, ignore, tag = elem.tag[1:].partition("}")
    else:
        uri = None
        tag = elem.tag
    return uri

## ----------------------------------- write to excel ----------------------------------------
def export_to_excel(filename, outputPath, df_datasources, df_tables, df_relationships, df_joins, df_queries):
    # print(outputPath)
    exportFileName = os.path.join(outputPath, filename[:-4] + " + 1.xlsx")
    with pd.ExcelWriter(exportFileName) as writer:
        # use to_excel function and specify the sheet_name and index
        # to store the dataframe in specified sheet
        df_datasources.to_excel(writer, sheet_name="DataSource", index=False)
        df_tables.to_excel(writer, sheet_name="Tables", index=False)
        df_relationships.to_excel(writer, sheet_name="Relationships", index=False)
        df_joins.to_excel(writer, sheet_name="Joins", index=False)
        df_queries.to_excel(writer, sheet_name="Query", index=False)
    print(f"[+] {filename[:-4]} + 1.xlsx file created")


def getDatasource(namespace, root):
    transferdictWithExp = {'DataSource Name': [], 'DataSource CM': [], 'DataSource Type': []}

    data_source_name = root.find(f'.//{namespace}dataSource/{namespace}name').text
    data_source_cm = root.find(f'.//{namespace}dataSource/{namespace}cmDataSource').text
    data_source_type = root.find(f'.//{namespace}dataSource/{namespace}type').text

    # print(f'Data Source Name: {data_source_name}')
    # print(f'Data Source CM: {data_source_cm}')
    # print(f'Data Source Type: {data_source_type}')

    transferdictWithExp['DataSource Name'].append(data_source_name)
    transferdictWithExp['DataSource CM'].append(data_source_cm)
    transferdictWithExp['DataSource Type'].append(data_source_type)

    df_datasources = pd.DataFrame(transferdictWithExp)
    return df_datasources

def get_relationships(namespace, root):
    transferdictWithExp = {'Table_1': [], 'Attribute_1': [], 'Unique_key1': [], 'Table_2': [], 'Attribute_2': [], 'Unique_key2': []}
    transferdictWithExp1 = {'Table 1': [], 'Table 2': []}

    # Fetch relationships
    relationships = root.findall(f'.//{namespace}relationship')
    for relationship in relationships:
        relationship_name = relationship.find(f'{namespace}name').text
        # print(f'Relationship: {relationship_name}')

        # Fetch relationship details (left, right, expression, etc.) as needed
        left = relationship.find(f'{namespace}left/{namespace}refobj').text
        right = relationship.find(f'{namespace}right/{namespace}refobj').text
        expression = relationship.find(f'{namespace}expression/{namespace}refobj').text

        # print(f'Left: {left}, Right: {right}, Expression: {expression}\n')

        t1 = left.split('].[')[0].split('[')[1]
        t2 = left.split('].[')[0].split('[')[1]
        exp = expression.split('].[')[2].split(']')[0]

        if ' <--> ' in relationship_name:
            attributes_lis = relationship_name.split(' <--> ')
            # print(len(attributes_lis), attributes_lis)
            transferdictWithExp['Attribute_1'].append(attributes_lis[0])
            transferdictWithExp['Attribute_2'].append(attributes_lis[1])
        elif ' <> ' in relationship_name:
            attributes_lis = relationship_name.split(' <> ')
            # print(len(attributes_lis), attributes_lis)
            transferdictWithExp['Attribute_1'].append(attributes_lis[0])
            transferdictWithExp['Attribute_2'].append(attributes_lis[1])
        # print(len(attributes_lis), attributes_lis)
        transferdictWithExp['Table_1'].append(t1)
        # transferdictWithExp['Attribute_1'].append('attributes_lis[0]')
        transferdictWithExp['Unique_key1'].append(exp)
        transferdictWithExp['Table_2'].append(t2)
        # transferdictWithExp['Attribute_2'].append('attributes_lis[1]')
        transferdictWithExp['Unique_key2'].append(exp)

        transferdictWithExp1['Table 1'].append(left)
        transferdictWithExp1['Table 2'].append(right)

    # print(transferdictWithExp)

    df_relatioships = pd.DataFrame(transferdictWithExp)
    df_joins = pd.DataFrame(transferdictWithExp1)
    return df_relatioships, df_joins


def get_queries(namespace, root):
    transferdictWithExp = {'Query': []}

    # Define the XML namespace
    namespace = {'bmt': 'http://www.developer.cognos.com/schemas/bmt/60/12'}

    # Find all elements with the tag 'lastChanged' using XPath with the namespace
    last_changed_elements = root.findall(".//bmt:sql", namespaces=namespace)

    # Extract and print the text content of each 'lastChanged' element
    for element in last_changed_elements:
        # print(element.text)
        transferdictWithExp['Query'].append(element.text)

    df_queries = pd.DataFrame(transferdictWithExp)
    return df_queries


def get_tables(namespace, root):
    transferdictWithExp = {'Table Name': []}

    # Define the XML namespace
    namespace = {'bmt': 'http://www.developer.cognos.com/schemas/bmt/60/12'}

    # Find all elements with the tag 'lastChanged' using XPath with the namespace
    last_changed_elements = root.findall(".//bmt:table", namespaces=namespace)

    # Extract and print the text content of each 'lastChanged' element
    for element in last_changed_elements:
        # print(element.text)
        transferdictWithExp['Table Name'].append(element.text)

    df_tables = pd.DataFrame(transferdictWithExp)
    return df_tables


def parse_package_xml(filepath, filename, directory):
    outputPath = os.path.join(directory, "cognosOutput1")
    # print(outputPath)
    if not os.path.exists(outputPath):
        try:
            os.mkdir(outputPath)
        except OSError:
            print(f"[-]Can't Create output directory on {outputPath}")
            return
    try:
        tree = ET.parse(filepath)
    except et.XMLSyntaxError as e:
        print('[-] Error parsing file:', str(filepath), str(e))
        return

    # Parse the XML file
    tree = ET.parse(package_filePath)
    root = tree.getroot()

    namespace = getNamespace(root)
    # print("nameSpace" , root, namespace)
    if (namespace == None):
        namespace = ''
    else:
        namespace = '{' + namespace + '}'

    # print(namespace)
    # print(root)

    df_dataSources = getDatasource(namespace, root)

    df_relationships, df_joins = get_relationships(namespace, root)

    df_queries = get_queries(namespace, root)

    df_tables = get_tables(namespace, root)

    export_to_excel(package_filename, outputPath, df_dataSources, df_tables, df_relationships, df_joins, df_queries)


# Specify the path to your XML file
directory = r'C:\Users\MAQ\OneDrive - MAQ Software\Documents\Akash Rajak\Megha Team Assignment\4 - Migration Automation CIP\work\Cognos\Sample Congnos Files'
# package_filePath = r"C:\Users\MAQ\OneDrive - MAQ Software\Documents\Akash Rajak\Megha Team Assignment\4 - Migration Automation CIP\work\Cognos\Sample Congnos Files\Packages_model.xml"
# package_filename = "Packages_model.xml"
package_filePath = r"C:\Users\MAQ\OneDrive - MAQ Software\Documents\Akash Rajak\Megha Team Assignment\4 - Migration Automation CIP\work\Cognos\Sample Congnos Files\Package_BSD Sales Relational_model.xml"
package_filename = "Package_BSD Sales Relational_model.xml"

parse_package_xml(package_filePath, package_filename, directory)




# Access elements in the XML tree
# project_name = root.find('.//{http://www.developer.cognos.com/schemas/bmt/60/12}name').text
# print(f'Project Name: {project_name}')

# # Fetch query subjects and their details
# query_subjects = root.findall(f'.//{namespace}querySubject')
# for query_subject in query_subjects:
#     query_subject_name = query_subject.find(f'{namespace}name').text
#     print(f'Query Subject: {query_subject_name}')
#
#     # Fetch details of query items
#     query_items = query_subject.findall(f'.//{namespace}queryItem')
#     for query_item in query_items:
#         query_item_name = query_item.find(f'{namespace}name').text
#         print(f'\tQuery Item: {query_item_name}')
#
#         # Fetch details of the query item (externalName, usage, datatype, etc.) as needed
#         external_name = query_item.find(f'{namespace}externalName').text
#         usage = query_item.find(f'{namespace}usage').text
#         datatype = query_item.find(f'{namespace}datatype').text
#
#         print(f'\t\tExternal Name: {external_name}, Usage: {usage}, Datatype: {datatype}\n')


