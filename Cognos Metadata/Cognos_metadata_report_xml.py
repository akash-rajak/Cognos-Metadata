# import getData as data
import os
import xml.etree.ElementTree as et
import pandas as pd
import re
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows


### ----------------------------------- get data ------------------------------------------------
def getNamespace(elem):
    if elem.tag[0] == "{":
        uri, ignore, tag = elem.tag[1:].partition("}")
    else:
        uri = None
        tag = elem.tag
    return uri


def getTwoClause(st):
    req = set()
    start = 0
    stack = []
    count = 0
    for i in range(0, len(st)):
        if (st[i] == "[" and len(stack) == 0):
            if (count == 0):
                start = i
            stack.append("[")
        elif (i + 1 < len(st) and st[i] == "]" and st[i + 1] != "." and len(stack) != 0 and count != 1):
            stack.pop()
            count = 0
        elif (i + 1 < len(st) and st[i] == "]" and st[i + 1] != "." and len(stack) != 0 and count == 1):
            stack.pop()
            end = i
            req.add(st[start:i + 1])
            count = 0
        elif (i + 1 < len(st) and st[i] == "]" and st[i + 1] == "." and len(stack) != 0 and count == 1 and i + 2 < len(
                st) and st[i + 2] != "["):
            stack.pop()
            end = i
            req.add(st[start:i + 1])
            count = 0
        elif (i + 1 == len(st) and st[i] == "]" and len(stack) != 0 and count == 1):
            stack.pop()
            end = i
            req.add(st[start:i + 1])
            count = 0
        elif (i + 1 < len(st) and st[i] == "]" and st[i + 1] == "." and len(stack) != 0):
            stack.pop()
            count = count + 1
            if (i + 2 < len(st) and st[i + 2] != '['):
                count = 0
    return req


def getOneClause(st):
    req = set()
    start = 0
    stack = []
    count = 0
    for i in range(0, len(st)):
        # print(st[i],count)
        if (st[i] == "[" and len(stack) == 0):
            if (count == 0):
                start = i
            stack.append("[")
        elif (i + 1 < len(st) and st[i] == "]" and st[i + 1] != "." and len(stack) != 0 and count != 0):
            stack.pop()
            count = 0
        elif (i + 1 < len(st) and st[i] == "]" and st[i + 1] != "." and len(stack) != 0 and count == 0):
            stack.pop()
            end = i
            req.add(st[start:i + 1])
            count = 0
        elif (i + 1 < len(st) and st[i] == "]" and st[i + 1] == "." and len(stack) != 0 and count == 0 and i + 2 < len(
                st) and st[i + 2] != "["):
            stack.pop()
            end = i
            req.add(st[start:i + 1])
            count = 0
        elif (i + 1 == len(st) and st[i] == "]" and len(stack) != 0 and count == 0):
            stack.pop()
            end = i
            req.add(st[start:i + 1])
            count = 0
        elif (i + 1 < len(st) and st[i] == "]" and st[i + 1] == "." and len(stack) != 0):
            stack.pop()
            count = count + 1
            if (i + 2 < len(st) and st[i + 2] != '['):
                count = 0
    return req


def QueryDataItemsPage(namespace, root):
    dict = {}

    for queries in root:
        if (re.sub(namespace, '', queries.tag) == 'queries'):
            for query in queries:
                if (re.sub(namespace, '', query.tag) == 'query'):
                    for selection in query:
                        if (re.sub(namespace, '', selection.tag) == 'selection'):
                            dataItemDict = {}
                            for dataItem in selection:
                                if (re.sub(namespace, '', dataItem.tag) == 'dataItem'):
                                    for expressions in dataItem:
                                        if (re.sub(namespace, '', expressions.tag) == 'expression'):
                                            dataItemDict[dataItem.attrib['name']] = expressions.text
                            dict[query.attrib['name']] = dataItemDict
    # Creating a dictonary for quick addition to a dataframe for csv export
    # Adding the expression like [*].[*].[*] to a new column as a list

    total_queries = len(dict)
    # Get Total number of data items
    total_dataItems = 0
    for itemdict in dict:
        total_dataItems = total_dataItems + len(dict[itemdict])

    transferdictWithExp = {'query_name': [], 'dataItem_name': [], 'expression': [], 'data_objects': []}
    for i in dict:
        for j in dict[i]:
            # print(i, "   ",j, "   ",dict[i][j])
            k1 = set(re.findall(r"\[[a-zA-Z0-9_ ]*\]\.\[[a-zA-Z0-9_ ]*\]\.\[[a-zA-Z0-9_ ]*\]", dict[i][j]))
            k2 = getTwoClause(dict[i][j])
            k3 = getOneClause(dict[i][j])
            if (len(k1)):
                for k in k1:
                    transferdictWithExp['query_name'].append(i.strip())
                    transferdictWithExp['dataItem_name'].append(j.strip())
                    transferdictWithExp['expression'].append(dict[i][j].strip())
                    l = k.replace('[', '')
                    l = l.replace(']', '')
                    transferdictWithExp['data_objects'].append(l)
            if (len(k2)):
                for k in k2:
                    transferdictWithExp['query_name'].append(i.strip())
                    transferdictWithExp['dataItem_name'].append(j.strip())
                    transferdictWithExp['expression'].append(dict[i][j].strip())
                    l = k.replace('[', '')
                    l = l.replace(']', '')
                    transferdictWithExp['data_objects'].append(l)
            if (len(k3)):
                for k in k3:
                    transferdictWithExp['query_name'].append(i.strip())
                    transferdictWithExp['dataItem_name'].append(j.strip())
                    transferdictWithExp['expression'].append(dict[i][j].strip())
                    l = k.replace('[', '')
                    l = l.replace(']', '')
                    transferdictWithExp['data_objects'].append(l)

            if (len(k1) == 0 and len(k2) == 0 and len(k3) == 0):
                transferdictWithExp['query_name'].append(i.strip())
                transferdictWithExp['dataItem_name'].append(j.strip())
                transferdictWithExp['expression'].append(dict[i][j].strip())
                transferdictWithExp['data_objects'].append("")

    df_query_dataItems = pd.DataFrame(transferdictWithExp)
    return (df_query_dataItems, total_queries, total_dataItems)


def getPageItems(namespace, root, tempList, myList, lastRefQuery, prefixIdentifier, prefixContentType, pageNameList,
                 firstRefQuery, isMasterContext, seenContents):
    if ('refQuery' in root.attrib):
        lastRefQuery = root.attrib['refQuery']
    if ('refQuery' in root.attrib and firstRefQuery == "" and seenContents == 1):
        firstRefQuery = root.attrib['refQuery']
    if (re.sub(namespace, '', root.tag) == 'masterContext'):
        isMasterContext = 1
    if (re.sub(namespace, '', root.tag) == 'textItem'):
        for j in root:
            if (re.sub(namespace, '', j.tag) == 'dataSource'):
                for k in j:
                    if (re.sub(namespace, '', k.tag) == 'staticValue'):
                        newtempList = list(tempList)
                        newtempList.append('staticValue')
                        newtempList.append(k.text)
                        if (isMasterContext):
                            # if it's next to master Context it's referred query will be the first ref query in the traversal
                            newtempList.append(firstRefQuery)
                        else:
                            newtempList.append(lastRefQuery)
                        newtempList.append(prefixContentType + str(prefixIdentifier)[0])
                        if (len(newtempList) == 6):
                            myList.append(newtempList)
    elif ('refDataItem' in root.attrib):
        newtempList = list(tempList)
        newtempList.append('refDataItem')
        newtempList.append(root.attrib['refDataItem'])
        if (isMasterContext):
            # if it's next to master Context it's referred query will be the first ref query in the traversal
            newtempList.append(firstRefQuery)
        else:
            newtempList.append(lastRefQuery)
        newtempList.append(prefixContentType + str(prefixIdentifier)[0])
        if (len(newtempList) == 6):
            myList.append(newtempList)
    passTempList = list(tempList)
    for i in range(0, len(root)):
        if (re.sub(namespace, '', root.tag) == 'contents'):
            seenContents = 1
            prefixIdentifier = prefixIdentifier * 10 + (i + 1)
            if (len(prefixContentType) == 0):
                prefixContentType = re.sub(namespace, '', root[i].tag)
        newTempList = list(passTempList)
        if (re.sub(namespace, '', root.tag) == 'reportPages' or re.sub(namespace, '', root.tag) == 'promptPages'):
            newTempList.append(re.sub(namespace, '', root.tag))
        if (re.sub(namespace, '', root.tag) == 'page'):
            newTempList.append(root.attrib['name'])
            pageNameList.append(root.attrib['name'])
        copyList = list(newTempList)
        getPageItems(namespace, root[i], copyList, myList, lastRefQuery, prefixIdentifier, prefixContentType,
                     pageNameList, firstRefQuery, isMasterContext, seenContents)


def createPagesDF(namespace, root, joiningString, dataItemDict):
    # Extracting data from Layouts section of xml file as page items and storing them as reportPages or promptPages
    reportPages = []
    pageNames = []
    for i in root:
        if re.sub(namespace, '', i.tag) == 'layouts':
            # calling the earlier defined method to get page items which are refered in the order of textItem->dataSource->staticValue/refDataItem
            getPageItems(namespace, i, [], reportPages, "", 0, "", pageNames, "", 0, 0)

    # created dataframe for reportPages/promptPages
    reportPages_df = pd.DataFrame(reportPages,
                                  columns=['reportPages/promptPages', 'page_Name', 'staticValue/refDataItem', 'value',
                                           'lastRefQuery', 'prefixIdentifier', ])

    mappedRefDataItem = []
    for index, row in reportPages_df.iterrows():
        if (row['staticValue/refDataItem'] == 'refDataItem'):
            if (row['lastRefQuery']):
                if (row['lastRefQuery'] + joiningString + row['value'] in dataItemDict):
                    mappedRefDataItem.append(dataItemDict[row['lastRefQuery'] + joiningString + row['value']])
                else:
                    mappedRefDataItem.append('NA')
            else:
                mappedRefDataItem.append('NA')
        else:
            mappedRefDataItem.append("")

    reportPages_df['mappedRefDataItem'] = mappedRefDataItem

    pageNames_df = pd.DataFrame(set(pageNames), columns=['Page_Name'])
    return reportPages_df, pageNames_df


def getModelPath(namespace, root):
    modelPath = []
    for child in root:
        if (re.sub(namespace, '', child.tag) == 'modelPath'):
            modelPath.append(child.text)
    package = []
    model = []
    if (len(modelPath)):
        pathFromXML = modelPath[0]
        package = (re.findall(r"package\[@name='([^']+)'", pathFromXML))
        model = (re.findall(r"model\[@name='([^']+)'", pathFromXML))

    modelPath_df = pd.DataFrame({'modelPath': modelPath, 'package': package, 'model': model})
    return modelPath_df


def getReportName(namespace, root):
    reportName_df = {'Name':[]}
    for child in root:
        if (re.sub(namespace, '', child.tag) == 'reportName'):
            # print(child.text)
            reportName_df['Name'].append(child.text)
            # reportName_df = pd.DataFrame({'Name': child.text})

    df_reportName = pd.DataFrame(reportName_df)
    return df_reportName


## ----------------------------------- Parameter  ----------------------------------------
def get_parameters(namespace, root):
    dict = {}
    transferdictWithExp = {'Name': [], 'Type': [], "Report Expression": [], "Variable Value":[]}

    for reportVariables in root:
        if (re.sub(namespace, '', reportVariables.tag) == 'reportVariables'):
            for reportVariable in reportVariables:
                # print(repor)
                if (re.sub(namespace, '', reportVariable.tag) == 'reportVariable'):
                    # print("Report Variable Name: ", reportVariable.attrib['name'])
                    # print("Report Variable Type: ", reportVariable.attrib['type'])

                    lis_exp = []
                    for reportExpression in reportVariable:
                        # print("Report Variable Expression: ", reportExpression.text)
                        lis_exp.append(reportExpression.text)

                    for variableValues in reportVariable:
                        if (re.sub(namespace, '', variableValues.tag) == 'variableValues'):
                            for variableValue in variableValues:
                                if (re.sub(namespace, '', variableValue.tag) == 'variableValue'):
                                    # for values in variableValue:
                                    # print("Report Variable Value: ", variableValue.attrib['value'])
                                    transferdictWithExp['Name'].append(reportVariable.attrib['name'])
                                    transferdictWithExp['Type'].append(reportVariable.attrib['type'])
                                    transferdictWithExp['Report Expression'].append(lis_exp[0])
                                    transferdictWithExp['Variable Value'].append(variableValue.attrib['value'])

    df_parameters = pd.DataFrame(transferdictWithExp)
    return df_parameters


## ----------------------------------- Measure  ----------------------------------------
def get_measures(namespace, root):
    dict = {}
    transferdictWithExp = {'Name': [], 'Expression': []}

    for queries in root:
        if (re.sub(namespace, '', queries.tag) == 'queries'):
            for query in queries:
                if (re.sub(namespace, '', query.tag) == 'query'):
                    for selection in query:
                        if (re.sub(namespace, '', selection.tag) == 'selection'):
                            for dataItemCalculatedMeasure in selection:
                                if (re.sub(namespace, '', dataItemCalculatedMeasure.tag) == 'dataItemCalculatedMeasure'):
                                    lis_exp = []
                                    for expressions in dataItemCalculatedMeasure:
                                        if (re.sub(namespace, '', expressions.tag) == 'expression'):
                                            lis_exp.append(expressions.text)
                                            # print("Measure Name: ", dataItemCalculatedMeasure.attrib['name'])
                                            # print("Measure Expression: ", expressions.text)
                                            transferdictWithExp['Name'].append(dataItemCalculatedMeasure.attrib['name'])
                                            transferdictWithExp['Expression'].append(expressions.text)



    df_measures_dimensions = pd.DataFrame(transferdictWithExp)
    return df_measures_dimensions


## ----------------------------------- Hierarchy  ----------------------------------------
def get_hierarchies(namespace, root):
    dict = {}
    transferdictWithExp = {'Item': [], 'Hierarchy': []}

    for queries in root:
        if (re.sub(namespace, '', queries.tag) == 'queries'):
            for query in queries:
                if (re.sub(namespace, '', query.tag) == 'query'):
                    for selection in query:
                        if (re.sub(namespace, '', selection.tag) == 'selection'):
                            for dataItemMemberProperty in selection:
                                if (re.sub(namespace, '', dataItemMemberProperty.tag) == 'dataItemMemberProperty'):
                                    for dmHierarchy in dataItemMemberProperty:
                                        if (re.sub(namespace, '', dmHierarchy.tag) == 'dmHierarchy'):
                                            idx = 0
                                            for val in dmHierarchy:
                                                if idx & 1:
                                                    # print("Hierarchy Name: ", val.text)
                                                    transferdictWithExp['Item'].append(val.text)
                                                else:
                                                    # print("Hierarchy : ", val.text)
                                                    transferdictWithExp['Hierarchy'].append(val.text)
                                                idx = idx + 1




    df_hierarchies = pd.DataFrame(transferdictWithExp)
    return df_hierarchies


## ----------------------------------- Measure  ----------------------------------------
def get_filters(namespace, root):
    dict = {}
    transferdictWithExp = {'Expression': [], 'Use':[]}

    for queries in root:
        if (re.sub(namespace, '', queries.tag) == 'queries'):
            for query in queries:
                if (re.sub(namespace, '', query.tag) == 'query'):
                    for detailFilters in query:
                        if (re.sub(namespace, '', detailFilters.tag) == 'detailFilters'):
                            for detailFilter in detailFilters:
                                if (re.sub(namespace, '', detailFilter.tag) == 'detailFilter'):
                                    for filterExpression in detailFilter:
                                        if (re.sub(namespace, '', filterExpression.tag) == 'filterExpression'):
                                            # print("Filter Expression: ", filterExpression.text)
                                            transferdictWithExp['Expression'].append(filterExpression.text)
                                            try:
                                                transferdictWithExp['Use'].append(detailFilter.attrib['use'])
                                                # print("Filter Use: ", detailFilter.attrib['use'])
                                            except:
                                                transferdictWithExp['Use'].append("")


    df_filters = pd.DataFrame(transferdictWithExp)
    return df_filters


# def get_queries(namespace1, root1):
#     transferdictWithExp = {'Query': []}
#
#
#     for namespace in root1:
#         print(namespace)
#         if (re.sub(namespace1, '', namespace.tag) == 'namespace'):
#             for namespace in namespace:
#                 if (re.sub(namespace1, '', namespace.tag) == 'namespace'):
#                     for folder in namespace:
#                         if (re.sub(namespace1, '', folder.tag) == 'folder'):
#                             print(folder)
#                             for folder in folder:
#                                 if (re.sub(namespace1, '', folder.tag) == 'folder'):
#                                     for dimension in folder:
#                                         if (re.sub(namespace1, '', dimension.tag) == 'dimension'):
#                                             for definition in dimension:
#                                                 if (re.sub(namespace1, '', definition.tag) == 'definition'):
#                                                     for modelQuery in definition:
#                                                         if (re.sub(namespace1, '', modelQuery.tag) == 'modelQuery'):
#                                                             for sql in definition:
#                                                                 if (re.sub(namespace1, '', sql.tag) == 'sql'):
#                                                                     print(sql.text)
#
#
#                             for dimension in folder:
#                                 if (re.sub(namespace1, '', dimension.tag) == 'dimension'):
#                                     for definition in dimension:
#                                         if (re.sub(namespace1, '', definition.tag) == 'definition'):
#                                             for modelQuery in definition:
#                                                 if (re.sub(namespace1, '', modelQuery.tag) == 'modelQuery'):
#                                                     for sql in definition:
#                                                         if (re.sub(namespace1, '', sql.tag) == 'sql'):
#                                                             print(sql.text)

## ----------------------------------- write to excel ----------------------------------------
def export_to_excel(filename, outputPath, modelPath_df, df_reportName, df_query_dataItems, df_promptPages, df_reportPages,
                    df_pageNames, df_parameters, df_measures_dimensions, df_hierarchy, df_filters):
    exportFileName = os.path.join(outputPath, filename[:-4] + ".xlsx")
    with pd.ExcelWriter(exportFileName) as writer:
        # use to_excel function and specify the sheet_name and index
        # to store the dataframe in specified sheet
        # modelPath_df.to_excel(writer, sheet_name="Model Path", index=False)
        df_reportName.to_excel(writer, sheet_name="Report", index=False)
        df_pageNames.to_excel(writer, sheet_name="Pages", index=False)
        df_promptPages.to_excel(writer, sheet_name="Prompt Page", index=False)
        df_reportPages.to_excel(writer, sheet_name="Report Pages", index=False)
        df_query_dataItems.to_excel(writer, sheet_name="Query Details", index=False)
        df_parameters.to_excel(writer, sheet_name="Parameters", index=False)
        df_measures_dimensions.to_excel(writer, sheet_name="Measures-Dimensions", index=False)
        df_hierarchy.to_excel(writer, sheet_name="Hierarchy", index=False)
        df_filters.to_excel(writer, sheet_name="Filters", index=False)
    print(f"[+] {filename[:-4]}.xlsx file created")


def parse_xml(report_filePath, report_filename, package_filePath, package_filename, directory):
    outputPath = os.path.join(directory, "cognosOutput")
    if not os.path.exists(outputPath):
        try:
            os.mkdir(outputPath)
        except OSError:
            print(f"[-]Can't Create output directory on {outputPath}")
            return
    try:
        tree = et.parse(report_filePath)
    except et.XMLSyntaxError as e:
        print('[-] Error parsing file:', str(report_filePath), str(e))
        return
    root = tree.getroot()

    namespace = getNamespace(root)
    # print("nameSpace" , root, namespace)
    if (namespace == None):
        namespace = ''
    else:
        namespace = '{' + namespace + '}'

    ## ------------------------------------ Query Data Item Page --------------------------------------------------------------------------------
    # call code to create query Data Items page
    df_query_dataItems, total_queries, total_dataItems = QueryDataItemsPage(namespace, root)

    # creating a dictionary of query_name joined with dataItem_name using joiningString mapped to Data Objects
    dataItemDict = {}
    joiningString = '##JOINING##'
    for index, row in df_query_dataItems.iterrows():
        if (row['query_name'] + joiningString + row['dataItem_name'] not in dataItemDict):
            dataItemDict[row['query_name'] + joiningString + row['dataItem_name']] = {row['data_objects']}
        dataItemDict[row['query_name'] + joiningString + row['dataItem_name']].add(row['data_objects'])

    # updating [*] type objects to their referenced paths
    for index, row in df_query_dataItems.iterrows():
        obj = row['data_objects'].split(".")
        if (len(obj) == 1):
            ProbableQueryName = row['query_name']
            ProbableDataItemName = obj[0]
            if (ProbableQueryName + joiningString + ProbableDataItemName in dataItemDict):
                row['data_objects'] = dataItemDict[ProbableQueryName + joiningString + ProbableDataItemName]
    df_query_dataItems = df_query_dataItems.explode('data_objects')

    # updating dictionary
    dataItemDict = {}
    joiningString = '##JOINING##'
    for index, row in df_query_dataItems.iterrows():
        # print(row)
        if (row['query_name'] + joiningString + row['dataItem_name'] not in dataItemDict):
            dataItemDict[row['query_name'] + joiningString + row['dataItem_name']] = {row['data_objects']}
        dataItemDict[row['query_name'] + joiningString + row['dataItem_name']].add(row['data_objects'])

    # updating [*][*] type objects to their referenced paths
    for index, row in df_query_dataItems.iterrows():
        obj = row['data_objects'].split(".")
        if (len(obj) == 2):
            ProbableQueryName = obj[0]
            ProbableDataItemName = obj[1]
            if (ProbableQueryName + joiningString + ProbableDataItemName in dataItemDict):
                row['data_objects'] = dataItemDict[ProbableQueryName + joiningString + ProbableDataItemName]
    df_query_dataItems = df_query_dataItems.explode('data_objects')

    # updating dictionary
    dataItemDict = {}
    joiningString = '##JOINING##'
    for index, row in df_query_dataItems.iterrows():
        if (row['query_name'] + joiningString + row['dataItem_name'] not in dataItemDict):
            dataItemDict[row['query_name'] + joiningString + row['dataItem_name']] = {row['data_objects']}
        dataItemDict[row['query_name'] + joiningString + row['dataItem_name']].add(row['data_objects'])

    # updating [*][*] type objects to their referenced paths for 2nd time because the earlier referenced objects could also be of [*].[*] type
    for index, row in df_query_dataItems.iterrows():
        obj = row['data_objects'].split(".")
        if (len(obj) == 2):
            ProbableQueryName = obj[0]
            ProbableDataItemName = obj[1]
            if (ProbableQueryName + joiningString + ProbableDataItemName in dataItemDict):
                row['data_objects'] = dataItemDict[ProbableQueryName + joiningString + ProbableDataItemName]
    df_query_dataItems = df_query_dataItems.explode('data_objects')

    # updating dictionary again
    dataItemDict = {}
    joiningString = '##JOINING##'
    for index, row in df_query_dataItems.iterrows():
        if (row['query_name'] + joiningString + row['dataItem_name'] not in dataItemDict):
            dataItemDict[row['query_name'] + joiningString + row['dataItem_name']] = {row['data_objects']}
        dataItemDict[row['query_name'] + joiningString + row['dataItem_name']].add(row['data_objects'])
    # dataItemDict


    # end of creating Query Data Items Page

    ## ------------------------------------ Pages Page --------------------------------------------------------------------------------
    reportPages_df, df_pageNames = createPagesDF(namespace, root, joiningString, dataItemDict)

    count_objects_in_reportPages = (reportPages_df['reportPages/promptPages'] == 'reportPages').sum()
    count_objects_in_promptPages = (reportPages_df['reportPages/promptPages'] == 'promptPages').sum()
    count_expression_in_Pages = (reportPages_df['mappedRefDataItem'] != '').sum()

    reportPages_df = reportPages_df.explode('mappedRefDataItem')
    df_reportPages = reportPages_df[reportPages_df['reportPages/promptPages'] == 'reportPages']
    df_reportPages.drop(['reportPages/promptPages'], axis=1, inplace=True)
    df_promptPages = reportPages_df[reportPages_df['reportPages/promptPages'] == 'promptPages']
    df_promptPages.drop(['reportPages/promptPages'], axis=1, inplace=True)

    ## ------------------------------------ Model Path Page --------------------------------------------------------------------------------
    # print(namespace)
    # print(root)
    # get model path dataframe
    modelPath_df = getModelPath(namespace, root)

    df_reportName = getReportName(namespace, root)

    ## -------------------------------- parameter page -------------------------------------------------------------------------------------
    df_parameters = get_parameters(namespace, root)

    ## -------------------------------- measure page -------------------------------------------------------------------------------------
    df_measures_dimensions = get_measures(namespace, root)

    ## -------------------------------- hierarchy page ----------------------------------------------------------------------------------
    df_hierarchy = get_hierarchies(namespace, root)

    ## -------------------------------- filters page -------------------------------------------------------------------------------------
    df_filters = get_filters(namespace, root)



    #### ============================================== Parsing Package XML ====================================================================
    try:
        tree1 = et.parse(package_filePath)
    except et.XMLSyntaxError as e:
        print('[-] Error parsing file:', str(package_filePath), str(e))
        return
    root1 = tree1.getroot()

    namespace1 = getNamespace(root1)
    # print("nameSpace1" , root1, namespace1)
    if (namespace1 == None):
        namespace1 = ''
    else:
        namespace1 = '{' + namespace + '}'

    # get_queries(namespace1, root1)


    ## -------------------------------------  Writing to Excel --------------------------------------------------
    export_to_excel(report_filename, outputPath, modelPath_df, df_reportName, df_query_dataItems, df_promptPages, df_reportPages, df_pageNames, df_parameters, df_measures_dimensions, df_hierarchy, df_filters)

    ## -------------------------------------  Writing to Excel --------------------------------------------------
    export_to_excel(report_filename, outputPath, modelPath_df, df_reportName, df_query_dataItems, df_promptPages, df_reportPages, df_pageNames, df_parameters, df_measures_dimensions, df_hierarchy, df_filters)

    total_data_objects = len(df_query_dataItems)

    # print("Page (Query Data Items) -> Total Number of Queries = ", total_queries)
    # print("Page (Query Data Items) -> Total Number of dataItems = ", total_dataItems)
    # print("Page (Query Data Items) -> Total Number of dataObjects = ", total_data_objects)
    # Will not include number of pages in complexity print("Page (Pages) -> Total Number of Pages = ", len(df_pageNames))
    # print("Page  -> Total Number of count_objects_in_reportPages = ", count_objects_in_reportPages)
    # print("Page  -> Total Number of count_objects_in_promptPages = ", count_objects_in_promptPages)
    # print("Page  -> Total Number of count_expression_in_Pages = ", count_expression_in_Pages)

    # data_for_complexity = (
    # filename[:-4], total_queries, total_dataItems, total_data_objects, count_objects_in_reportPages,
    # count_objects_in_promptPages, count_expression_in_Pages)
    #
    # createExcel.export_to_excel(filename, outputPath, modelPath_df, df_query_dataItems, df_promptPages, df_reportPages, df_pageNames)
    # return data_for_complexity


directory = r'C:\Users\MAQ\OneDrive - MAQ Software\Documents\Akash Rajak\Megha Team Assignment\4 - Migration Automation CIP\work\Cognos\Sample Congnos Files'
# mainCode(directory)
report_filePath = r"C:\Users\MAQ\OneDrive - MAQ Software\Documents\Akash Rajak\Megha Team Assignment\4 - Migration Automation CIP\work\Cognos\Sample Congnos Files\Report_Sales by Customer.xml"
report_filename = "Report_Sales by Customer.xml"
package_filePath = r"C:\Users\MAQ\OneDrive - MAQ Software\Documents\Akash Rajak\Megha Team Assignment\4 - Migration Automation CIP\work\Cognos\Sample Congnos Files\Package_BSD Sales Relational_model.xml"
package_filename = "Package_BSD Sales Relational_model.xml"

parse_xml(report_filePath, report_filename, package_filePath, package_filename, directory)


