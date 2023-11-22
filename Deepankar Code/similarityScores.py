import os
import glob
import pandas as pd
import Levenshtein
import itertools
import sys
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
import writeDataToExcel as createExcel

#threshold is between 0 and 1
def DocRepScore(b1, b2,threshold):
  len_b1 = len(b1)
  len_b2 = len(b2)
  if len_b1>len_b2:
    return DocRepScore(b2,b1,threshold)
  sumb1 = 0
  for i in b1:
    maxHere = 0
    for j in b2:
      a = len(i)
      b = len(j)
      i1=i
      j1=j
      if b>a:
        i1=j
        j1=i
        d=a
        a=b
        b=d
      editDistance = Levenshtein.distance(i1, j1)
      formulae1 = (a-editDistance)/a
      maxHere = max(maxHere,formulae1)
    if maxHere>threshold:
      sumb1=sumb1+maxHere
  return sumb1/len_b1

def MatchFormulae(a,b):
  union_set = a.union(b)
  intersection = a.intersection(b)
  len_intersection = len(intersection)
  len_union_set = len(union_set)
  len_a = len(a)
  len_b = len(b)
  if(len_intersection == len(a) or len_intersection == len(b)):
    return min(len_a,len_b)/max(len_a,len_b)
  else:
    return 2*len_intersection/(len_intersection+len_union_set)
  

def dataExtraction(path):
  folder_path = path
  print(folder_path)
  cols_to_extract_QueryDataItems = ['dataItem_name','expression','data_objects']
  cols_to_extract_Pages = ['staticValue/refDataItem','value','mappedRefDataItem']

  # create a list of all .xlsx files in the folder
  xlsx_files = glob.glob(os.path.join(folder_path, "*.xlsx"))

  # check if there are any xlsx files in the folder
  if len(xlsx_files) == 0:
      sys.exit("No metadata xlsx files found in folder") 
  else:
      # create an empty list to store the dataframes
      dfs_query_data_items = []
      dfs_prompt_page = []
      dfs_report_page = []
      # loop through each file and extract the data
      for file in xlsx_files:
          # For extracting expressions from Query Data Items sheet
          df = pd.read_excel(file, sheet_name="Query Data Items", usecols=cols_to_extract_QueryDataItems)
          df["Expression"] = df["expression"].str.upper()
          df["Data Object"] = df["data_objects"].str.upper()
          df["Data Item Name"] = df["dataItem_name"].str.upper()
          df["Report Name"] = os.path.basename(file)
          df["Report Name"] = df["Report Name"].apply(lambda x: x[:-5])
          df = df[["Report Name", "Expression","Data Object","Data Item Name"]]
          dfs_query_data_items.append(df)

          #For extracting Measure from Measures sheet\
          df_3 = pd.read_excel(file, sheet_name="Prompt Page", usecols=cols_to_extract_Pages)
          df_3["staticValue/refDataItem"] = df_3["staticValue/refDataItem"].str.upper()
          df_3["Value"] = df_3["value"].str.upper()
          df_3["Data Object"] = df_3["mappedRefDataItem"].str.upper()
          df_3["Report Name"] = os.path.basename(file)
          df_3["Report Name"] = df_3["Report Name"].apply(lambda x: x[:-5])
          df_3 = df_3[["Report Name", "staticValue/refDataItem","Value","Data Object"]]
          dfs_prompt_page.append(df_3)
          
          #For extracting Measure from Measures sheet\
          df_2 = pd.read_excel(file, sheet_name="Report Pages", usecols=cols_to_extract_Pages)
          df_2["staticValue/refDataItem"] = df_2["staticValue/refDataItem"].str.upper()
          df_2["Value"] = df_2["value"].str.upper()
          df_2["Data Object"] = df_2["mappedRefDataItem"].str.upper()
          df_2["Report Name"] = os.path.basename(file)
          df_2["Report Name"] = df_2["Report Name"].apply(lambda x: x[:-5])
          df_2 = df_2[["Report Name", "staticValue/refDataItem","Value","Data Object"]]
          dfs_report_page.append(df_2)

      # concatenate all dataframes into a single dataframe
      final_df_queryDataItems = pd.concat(dfs_query_data_items, ignore_index=True)
      final_df_data_expressions = final_df_queryDataItems[["Report Name", "Expression"]]
      final_df_dataItemNames = final_df_queryDataItems[["Report Name", "Data Item Name"]]
      final_df_dataObjects = final_df_queryDataItems[["Report Name", "Data Object"]]


      final_df_promptPage = pd.concat(dfs_prompt_page, ignore_index=True)
      final_df_reportPage = pd.concat(dfs_prompt_page, ignore_index=True)
      final_df_page = pd.concat([final_df_promptPage, final_df_reportPage])

      #static elements used in report and prompt pages
      final_df_reportstaticElements = final_df_page.loc[final_df_page['staticValue/refDataItem'] == "STATICVALUE", ['Report Name', 'Value']]
      #data elements used in report and prompt pages
      final_df_reportdataElements = final_df_page.loc[final_df_page['staticValue/refDataItem'] == "REFDATAITEM", ['Report Name', 'Data Object']]
      # print the final dataframe
  return(final_df_data_expressions,final_df_dataItemNames,final_df_dataObjects,final_df_reportstaticElements,final_df_reportdataElements)

def editDistanceBasedSimilarity(final_df,document_name_column,comparing,threshold):
  grouped_measure = final_df.groupby([document_name_column])[comparing].apply(lambda x: set(x.dropna())).reset_index()
  grouped_measure = grouped_measure.sort_values(by=[document_name_column])

  measure_similarity_list = []
  pairs = list(itertools.combinations(grouped_measure[document_name_column].unique(), 2))
  for pair in pairs:
      a1, a2 = pair
      b1 = grouped_measure.loc[grouped_measure[document_name_column] == a1, comparing].iloc[0]
      b2 = grouped_measure.loc[grouped_measure[document_name_column] == a2, comparing].iloc[0]
      doc_b1 = a1
      doc_b2 = a2    
      result = DocRepScore(b1, b2,threshold)
      measure_similarity_list.append((doc_b1,doc_b2,result))

  similarity_df = pd.DataFrame(measure_similarity_list, columns = ['Report','Compared Report','Similarity'])
  return similarity_df

def setTheoryBasedSimilarity(df_universe,document_name_column,comparing):
  grouped = df_universe.groupby(document_name_column)[comparing].agg(set).reset_index()
  pairs = list(itertools.combinations(grouped[document_name_column].unique(), 2))
  similarity_list = []
  for pair in pairs:
      a1, a2 = pair
      b1 = grouped.loc[grouped[document_name_column] == a1, comparing].iloc[0]
      b2 = grouped.loc[grouped[document_name_column] == a2, comparing].iloc[0]
      result = MatchFormulae(b1, b2)
      similarity_list.append((a1,a2,result))

  similarity_df = pd.DataFrame(similarity_list, columns = ['Report','Compared Report','Similarity'])
  return similarity_df



def similarityCode(outputPath):

    output_complexity_workbook_name ="COGNOS Output.xlsx"
    path=outputPath
    final_df_data_expressions,final_df_dataItemNames,final_df_dataObjects,final_df_reportstaticElements,final_df_reportdataElements = dataExtraction(path)
    print("asdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasdasdasdasdasdadsadassadasdasd")
    print(final_df_data_expressions)
    df_data_expression_similarity = editDistanceBasedSimilarity(final_df_data_expressions,'Report Name','Expression',0.9)
    df_dataObjects_similarity = editDistanceBasedSimilarity(final_df_dataObjects,'Report Name','Data Object',0.9)
    df_dataItem_names_similarity = setTheoryBasedSimilarity(final_df_dataItemNames,'Report Name','Data Item Name')
    df_reportstaticElement_similarity = setTheoryBasedSimilarity(final_df_reportstaticElements,'Report Name','Value')
    df_reportdataElement_similarity = editDistanceBasedSimilarity(final_df_reportdataElements,'Report Name','Data Object',0.9)
    concatenated_df = pd.concat([df_data_expression_similarity,df_dataObjects_similarity,df_dataItem_names_similarity,df_reportstaticElement_similarity,df_reportdataElement_similarity])
    mean_df = concatenated_df.groupby(['Report', 'Compared Report'])['Similarity'].mean().reset_index()    
    createExcel.save_similarity_in_Complexity_Sheet(outputPath,mean_df,df_data_expression_similarity,df_dataObjects_similarity,df_dataItem_names_similarity,df_reportstaticElement_similarity,df_reportdataElement_similarity)