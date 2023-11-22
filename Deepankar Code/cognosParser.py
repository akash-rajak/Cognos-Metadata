import getData as data
import writeDataToExcel as createExcel
import os
import xml.etree.ElementTree as et
import pandas as pd
import similarityScores as similarity

def myCode(filePath,filename,directory):
  outputPath = os.path.join(directory,"cognosOutput")
  if not os.path.exists(outputPath):
    try:
      os.mkdir(outputPath)
    except OSError:
      print(f"[-]Can't Create output directory on {outputPath}")
      return
  try:
    tree=et.parse(filePath)
  except et.XMLSyntaxError as e:
    print('[-] Error parsing file:', str(filePath), str(e))
    return
  root=tree.getroot() 
  print(data.hello)
  namespace = data.getNamespace(root)
  if(namespace == None):
    namespace = ''
  else:
    namespace = '{'+namespace+'}'

  #call code to create query Data Items page
  df_query_dataItems,total_queries,total_dataItems = data.QueryDataItemsPage(namespace,root)
  
  #creating a dictionary of query_name joined with dataItem_name using joiningString mapped to Data Objects
  dataItemDict = {}
  joiningString = '##JOINING##'
  for index, row in df_query_dataItems.iterrows():
    if(row['query_name']+joiningString+row['dataItem_name'] not in dataItemDict):
      dataItemDict[row['query_name']+joiningString+row['dataItem_name']]= {row['data_objects']}
    dataItemDict[row['query_name']+joiningString+row['dataItem_name']].add(row['data_objects'])
  dataItemDict
  
  #updating [*] type objects to their referenced paths
  for index, row in df_query_dataItems.iterrows():
    obj = row['data_objects'].split(".")
    if(len(obj)==1):
      ProbableQueryName = row['query_name']
      ProbableDataItemName = obj[0]
      if(ProbableQueryName+joiningString+ProbableDataItemName in dataItemDict):
        row['data_objects'] = dataItemDict[ProbableQueryName+joiningString+ProbableDataItemName]
  df_query_dataItems = df_query_dataItems.explode('data_objects')

  #updating dictionary
  dataItemDict = {}
  joiningString = '##JOINING##'
  for index, row in df_query_dataItems.iterrows():
    # print(row)
    if(row['query_name']+joiningString+row['dataItem_name'] not in dataItemDict):
      dataItemDict[row['query_name']+joiningString+row['dataItem_name']]= {row['data_objects']}
    dataItemDict[row['query_name']+joiningString+row['dataItem_name']].add(row['data_objects'])
  dataItemDict

  #updating [*][*] type objects to their referenced paths
  for index, row in df_query_dataItems.iterrows():
    obj = row['data_objects'].split(".")
    if(len(obj)==2):
      ProbableQueryName = obj[0]
      ProbableDataItemName = obj[1]
      if(ProbableQueryName+joiningString+ProbableDataItemName in dataItemDict):
        row['data_objects'] = dataItemDict[ProbableQueryName+joiningString+ProbableDataItemName]
  df_query_dataItems = df_query_dataItems.explode('data_objects')

  #updating dictionary
  dataItemDict = {}
  joiningString = '##JOINING##'
  for index, row in df_query_dataItems.iterrows():
    if(row['query_name']+joiningString+row['dataItem_name'] not in dataItemDict):
      dataItemDict[row['query_name']+joiningString+row['dataItem_name']]= {row['data_objects']}
    dataItemDict[row['query_name']+joiningString+row['dataItem_name']].add(row['data_objects'])

  #updating [*][*] type objects to their referenced paths for 2nd time because the earlier referenced objects could also be of [*].[*] type
  for index, row in df_query_dataItems.iterrows():
    obj = row['data_objects'].split(".")
    if(len(obj)==2):
      ProbableQueryName = obj[0]
      ProbableDataItemName = obj[1]
      if(ProbableQueryName+joiningString+ProbableDataItemName in dataItemDict):
        row['data_objects'] = dataItemDict[ProbableQueryName+joiningString+ProbableDataItemName]
  df_query_dataItems = df_query_dataItems.explode('data_objects')

  #updating dictionary again
  dataItemDict = {}
  joiningString = '##JOINING##'
  for index, row in df_query_dataItems.iterrows():
    if(row['query_name']+joiningString+row['dataItem_name'] not in dataItemDict):
      dataItemDict[row['query_name']+joiningString+row['dataItem_name']]= {row['data_objects']}
    dataItemDict[row['query_name']+joiningString+row['dataItem_name']].add(row['data_objects'])
  # dataItemDict

  #end of creating Query Data Items Page 
  reportPages_df,df_pageNames = data.createPagesDF(namespace,root,joiningString,dataItemDict)
  
  count_objects_in_reportPages = (reportPages_df['reportPages/promptPages'] == 'reportPages').sum()
  count_objects_in_promptPages = (reportPages_df['reportPages/promptPages'] == 'promptPages').sum()
  count_expression_in_Pages = (reportPages_df['mappedRefDataItem'] != '').sum()
  
  reportPages_df = reportPages_df.explode('mappedRefDataItem')
  df_reportPages = reportPages_df[reportPages_df['reportPages/promptPages'] =='reportPages']
  df_reportPages.drop(['reportPages/promptPages'], axis=1 ,inplace = True)
  df_promptPages = reportPages_df[reportPages_df['reportPages/promptPages'] =='promptPages']
  df_promptPages.drop(['reportPages/promptPages'], axis=1 ,inplace = True)

  #get model path dataframe
  modelPath_df = data.getModelPath(namespace,root)
  
  createExcel.export_to_excel(filename,outputPath,modelPath_df,df_query_dataItems,df_promptPages,df_reportPages,df_pageNames)
  
  total_data_objects = len(df_query_dataItems)

  # print("Page (Query Data Items) -> Total Number of Queries = ", total_queries)
  # print("Page (Query Data Items) -> Total Number of dataItems = ", total_dataItems)
  # print("Page (Query Data Items) -> Total Number of dataObjects = ", total_data_objects)
  # Will not include number of pages in complexity print("Page (Pages) -> Total Number of Pages = ", len(df_pageNames))
  # print("Page  -> Total Number of count_objects_in_reportPages = ", count_objects_in_reportPages)
  # print("Page  -> Total Number of count_objects_in_promptPages = ", count_objects_in_promptPages)
  # print("Page  -> Total Number of count_expression_in_Pages = ", count_expression_in_Pages)

  data_for_complexity = (filename[:-4],total_queries,total_dataItems,total_data_objects,count_objects_in_reportPages,count_objects_in_promptPages,count_expression_in_Pages)

  createExcel.export_to_excel(filename,outputPath,modelPath_df,df_query_dataItems,df_promptPages,df_reportPages,df_pageNames)
  return data_for_complexity



def mainCode(cognosQueue):
  if cognosQueue.qsize() == 0:
        return
  # iterate over files in the directory
  file_count = cognosQueue.qsize()
  list_data_for_complexity = []
  directory = ""
  for i in range(file_count):
    filePath = cognosQueue.get()
    if filePath == None:
      break
    directory = os.path.dirname(filePath)
    filename = os.path.basename(filePath)
    data_for_complexity = myCode(filePath,filename,directory)
    list_data_for_complexity.append(data_for_complexity)

  data_for_complexity_df = pd.DataFrame(list_data_for_complexity, columns = ['Report Name','Total Queries','Total DataItems','Total Data Objects','Objects in Report Pages','Objects in Prompt Pages','Expressions in Pages'])
  data_for_complexity_df.index = pd.RangeIndex(start=1, stop=len(data_for_complexity_df)+1)
  data_for_complexity_df = data_for_complexity_df.reset_index().rename(columns={'index': 'Report Number'})                     
  complexity_sheet_name = 'Reports Complexity'
  complexity_workbook_name = r'COGNOS Complexity Report.xlsm'
  outputPath = os.path.join(directory,'cognosOutput')

  createExcel.save_complexity_report(data_for_complexity_df,complexity_sheet_name,complexity_workbook_name,outputPath)

  similarity.similarityCode(outputPath)
  # print("asdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasd")


directory = r'C:\Users\MAQ\OneDrive - MAQ Software\Documents\Akash Rajak\Megha Team Assignment\4 - Migration Automation CIP\work\Cognos\Sample Congnos Files'
# mainCode(directory)
filePath = r"C:\Users\MAQ\OneDrive - MAQ Software\Documents\Akash Rajak\Megha Team Assignment\4 - Migration Automation CIP\work\Cognos\Sample Congnos Files\Average Days Matter Assigned to Organization.xml"
filename = "Average Days Matter Assigned to Organization.xml"

myCode(filePath, filename, directory)