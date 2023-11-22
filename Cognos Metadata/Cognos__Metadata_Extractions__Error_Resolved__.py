import requests
import json
import pandas as pd
import time
import os
import openpyxl
import urllib3
import maskpass
from urllib.parse import urlparse
class CognosApiClient:
    def __init__(self, cognos_analytics_server):
        self.cognos_analytics_server = cognos_analytics_server
        self.session_key = ""
        self.response_objects = {}
        self.report_names = []
        self.report_ids = []
        self.folder_ids = []
        self.report_count = 0
        self.datasources_dict = {}
        self.dataSource_names = []
        self.dataSource_ids = []
        self.dataSource_count = 0
        self.connections_dict = {}
        self.connection_names = []
        self.connection_ids = []
        self.connection_string = []
        self.connection_count = 0
        self.data_conn_map = {}
        self.signons_dict = {}
        self.signons_names = []
        self.signons_ids = []
        self.signons_count = 0
        self.schemas_dict = {}
        self.schema_ids = []
        self.schema_schemas = []
        self.schema_names = []
        self.schema_schemaTypes = []
        self.schema_catalog=[]
        self.schema_count = 0
        self.check=0
        self.length_Ds=0
        self.datasource_df = pd.DataFrame()
        self.report_df = pd.DataFrame()

        



    def get_session(self,CAMNamespace,CAMUsername,CAMPassword):
        print("\nAuhenticating")
        # Define the headers
        headers = {
            'Content-Type': 'application/json'
        }

        # Disable SSL verification warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


        # Set the Authentication API URL
        authentication_url = f"{self.cognos_analytics_server}/api/v1/session"

        data = {
            "parameters": [
                {
                    "name": "CAMNamespace",
                    "value": CAMNamespace
                },
                {
                    "name": "CAMUsername",
                    "value": CAMUsername
                },
                {
                     "name": "CAMPassword",
                    "value": CAMPassword
                 }
            ]
        }

       

        # Convert the data to JSON
        data_json = json.dumps(data)

        # Send the POST request
        response = requests.put(authentication_url, headers=headers, data=data_json,verify= False)

        # Check the response
        if response.status_code == 201:
            # Authentication successful
            print("Auth API hit successfull.")
            response_data = json.loads(response.text)
            parsed_url = urlparse(self.cognos_analytics_server)
            domain = parsed_url.netloc + parsed_url.path
            
            
            self.response_objects = {
                "IBM-BA-Authorization": response_data["session_key"]

            }
            
            print("Authentication Successfull.")
            self.check=1
            return self.check
            
        else:
            print(f"Authentication failed. Status Code: {response.status_code}")
            return self.check


    def get_content(self):
        print("\nFetching Reports")

        try:
            content = f"{self.cognos_analytics_server}/api/v1/content"
            
            headers = {
                "Content-Type": "application/json",
                "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
            }
            response = requests.get(content, headers=headers)
            content_response = response.json()
            

            if response.status_code == 200:
                report_val = []
                report_val.append(["Report Name","Report ID"])
                for d in content_response['content']:
                    if(d['type']=='folder'):
                        self.folder_ids.append(d['id'])
                    elif d['type'] == 'report':
                        
                        self.report_names.append(d['defaultName'])
                        report_val.append([d['defaultName'], d['id']])
                        self.report_count = self.report_count + 1
                        

                idx = 0
                while(True):
                    if(idx==len(self.folder_ids)):
                        break
                    
                    item = f"{self.cognos_analytics_server}/api/v1/content/{self.folder_ids[idx]}/items"
                    
                    response = requests.get(item, headers=headers)
                    item_response = response.json()
                   
                    for d in item_response['content']:
                        if(d['type']=='folder'):
                            self.folder_ids.append(d['id'])
                        elif(d['type']=='report'):
                            self.report_ids.append(d['id'])
                            self.report_names.append(d['defaultName'])
                            report_val.append([d['defaultName'], d['id']])                            
                            self.report_count = self.report_count + 1
                    
                    idx = idx + 1
                
                self.report_df = pd.DataFrame(report_val)
                self.report_df.columns = self.report_df.iloc[0]
                self.report_df = self.report_df[1:]
                self.report_df = self.report_df.reset_index(drop=True)

                print("\nFetched Reports Successfully.")
                print("\nReport Count:", self.report_count)
                

            else:
                print("Unsuccessful")

        except Exception as e:
            print(e)

        

    def get_datasources(self):
        print("\nFetching DataSources")
        try:
            datasources = f"{self.cognos_analytics_server}/api/v1/datasources"
            headers = {
                "Content-Type": "application/json",
                "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
            }
            response = requests.get(datasources, headers=headers)
            datasources_reponse = response.json()

            if response.status_code == 200:
                print("\nSuccessfully fetched Datasources")
                
                for d in datasources_reponse['dataSources']:
                    
                    self.dataSource_names.append(d['defaultName'])
                    self.dataSource_ids.append(d['id'])
                    self.datasources_dict[d['id']]=[d['defaultName']]
                    if(d['type']=='dataSource'):
                        self.dataSource_count = self.dataSource_count + 1
                    self.length_Ds = len(datasources_reponse['dataSources'])
                    
                    self.get_connections(d['id'])



            else:
                print("Unable to fetch DataSources")

            

        except Exception as e:
            print(e)

        

        return self.dfs()


    def get_connections(self, datasource_id):
        
        print("\nFetching connection for datasource " + str(self.dataSource_count) + " / " + str(self.length_Ds))
        try:
            
            connections = f"{self.cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections"
            headers = {
                "Content-Type": "application/json",
                "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
            }
            response = requests.get(connections, headers=headers)
            connection_response = response.json()
            

            if response.status_code == 200:
                print("\nFetched Connections Successfully.")
                l1 = {}
                for c in connection_response['connections']:
                    
                    self.connection_names.append(c['defaultName'])
                    self.connection_ids.append(c['id'])
                    l1[c['id']] = ''
                    self.connection_string.append(c['connectionString'])
                    self.connections_dict[c['id']]=[c['defaultName'],c['connectionString']]
                    if (c['type'] == 'dataSourceConnection'):
                        self.connection_count = self.connection_count + 1
                   
                    
                self.data_conn_map[datasource_id] = l1
                for val in l1:
                    
                    self.get_signons(datasource_id,val)

            else:
                print("Unable to fetch Connections for datasource " + str(self.dataSource_count) + " / " + str(self.length_Ds))

            

        except Exception as e:
            print(e)


    def get_signons(self, datasource_id, connection_id):
        
        print("\nFetching Signon for datasource " + str(self.dataSource_count) + " / " + str(self.length_Ds))
        
        try:
            
            signons = f"{self.cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections/{connection_id}/signons"
            headers = {
                "Content-Type": "application/json",
                "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
            }
            response = requests.get(signons, headers=headers)
            signon_response = response.json()

            if response.status_code == 200:
                
                s_id = {}
                if len(signon_response['signons'])==0:
                    print("\nNo Signon Present.")
                    print("\nCannot fetch tables from the datasource as no signon is present")
                else:
                    print("\nFetched signons Successfully.")    
                for s in signon_response['signons']:
                    
                    self.signons_names.append(s['defaultName'])
                    self.signons_ids.append(s['id'])

                    
                    s_id[s['id']] = ''
                    self.signons_dict[s['id']]=[s['defaultName']]

                    if (s['type'] == 'dataSourceSignon'):
                        self.signons_count = self.signons_count + 1
                    
                if datasource_id in self.data_conn_map:
                    
                    if connection_id in self.data_conn_map[datasource_id]:
                        
                        self.data_conn_map[datasource_id][connection_id]=s_id

                for val in s_id:
                     
                     self.get_schemas(datasource_id, connection_id, val)
                     self.get_tables(datasource_id, connection_id, val)


                

            else:
                print("Unable to fetch Signons for datasource " + str(self.dataSource_count) + " / " + str(self.length_Ds))
           

        except Exception as e:
            print(e)


    def get_schemas(self, datasource_id, connection_id, signon_id):
       
        print("\nFetching Schemas for datasource " + str(self.dataSource_count) + " / " + str(self.length_Ds))
        try:
            schemas = f"{self.cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections/{connection_id}/signons/{signon_id}/schemas"
            headers = {
                "Content-Type": "application/json",
                "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
            }
            response = requests.get(schemas, headers=headers)
            schemas_response = response.json()

            sch_dict= {}

            if response.status_code == 200:
                print("\nFetched Schemas Successfully.")
                for sch in schemas_response['schemas']:
                    self.schema_ids.append(sch['id'])
                    self.schema_schemas.append(sch['schema'])
                    self.schema_names.append(sch['defaultName'])
                    self.schema_schemaTypes.append(sch['schemaType'])
                    self.schema_catalog.append(sch['catalog'])
                    sch_dict[sch['id']] = ''
                    self.schemas_dict[sch['id']]=[sch['defaultName'],sch['catalog']]   

                    self.schema_count = self.schema_count + 1
                    

                if datasource_id in self.data_conn_map:
                    if connection_id in self.data_conn_map[datasource_id]:
                        if signon_id in self.data_conn_map[datasource_id][connection_id] :
                            self.data_conn_map[datasource_id][connection_id][signon_id] = sch_dict
     
                

                

            else:
                print("Unable to fetch Schemas for datasource " + str(self.dataSource_count) + " / " + str(self.length_Ds))

           
        except Exception as e:
            print(e)


    def get_tables(self, datasource_id, connection_id, signon_id):
        
        print("\nFetching Tables for datasource " + str(self.dataSource_count) + " / " + str(self.length_Ds))
        try:
            tables = f"{self.cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections/{connection_id}/signons/{signon_id}/schemas/tables"
            headers = {
                "Content-Type": "application/json",
                "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
            }
            response = requests.get(tables, headers=headers)

            if response.status_code == 200:
                print("\nFetched Tables Successfully.")
                pass

            else:
                print("\nUnable to fetch tables for datasource " + str(self.dataSource_count) + " / " + str(self.length_Ds))

        except Exception as e:
            print(e)


    def dfs(self):
        value_data = self.data_conn_map
        list_val = []
        list_val.append(["Datasource_ID","Datasource_Name","Connection_Id","Connection_Name","Connection_String","Signon_Id","Signon_Name","Schema_Id","Schema_Name","Schema_Catalog"])

        for datasource in self.data_conn_map:
            
            datasource_name = self.datasources_dict[datasource][0]
            if(len(self.data_conn_map[datasource]) > 0):
                for connection in self.data_conn_map[datasource]:
                    
                    connection_name =self.connections_dict[connection][0]
                    connection_string =self.connections_dict[connection][1]
                    if(len(self.data_conn_map[datasource][connection]) > 0):
                        for signon in self.data_conn_map[datasource][connection]:
                            
                            signon_name =self.signons_dict[signon][0]
                            if(len(self.data_conn_map[datasource][connection][signon]) > 0):
                                for schema in self.data_conn_map[datasource][connection][signon] :
                                    
                                    schema_name =self.schemas_dict[schema][0]
                                    schema_catalog=self.schemas_dict[schema][1]
                                    
                                    list_val.append([datasource,datasource_name,connection,connection_name,connection_string,signon,signon_name,schema,schema_name,schema_catalog])
                            else:
                                 list_val.append([datasource,datasource_name,connection,connection_name,connection_string,signon,signon_name,"","",""])

                    else:
                       list_val.append([datasource,datasource_name,connection,connection_name,connection_string,"","","","",""])
            else:
                list_val.append([datasource,datasource_name,"","","","","","","",""])
                
            

        self.datasource_df = pd.DataFrame(list_val)
        
        self.datasource_df.columns = self.datasource_df.iloc[0]
        self.datasource_df = self.datasource_df[1:]
        self.datasource_df = self.datasource_df.reset_index(drop=True)
        


    def export_to_excel(self):

        writer = pd.ExcelWriter('Output.xlsx', engine='openpyxl')

        # Write each dataframe to a separate sheet
        self.report_df.to_excel(writer, sheet_name='Report', index=False)
        self.datasource_df.to_excel(writer, sheet_name='Data Source', index=False)

        print()
        print("Successfully written to excel.")
        os.chdir(os.path.dirname(__file__))
        print("Excel Path: ", os.path.dirname(__file__))

        writer.close()

def main():
    check=0
    cognos_analytics_server = input("Enter Cognos Analytics Server link: ")
    CAMNamespace = input("Enter CAMNamespace: ")
    CAMUsername = input("Enter CAMUsername: ")
    CAMPassword = maskpass.askpass(prompt="Enter CAMPassword: ", mask="#")    

    cognos_client = CognosApiClient(cognos_analytics_server)
    try:
        check = cognos_client.get_session(CAMNamespace,CAMUsername,CAMPassword)
    except Exception as e:
            print(e)
    
    if (check==1):
        cognos_client.get_datasources()
        cognos_client.get_content()
        cognos_client.export_to_excel()
        
        

if __name__ == "__main__":
    main()
    time.sleep(60)