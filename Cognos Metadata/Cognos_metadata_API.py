
import requests
import json

class CognosApiClient:
    def __init__(self, cognos_analytics_server, login_key):
        self.cognos_analytics_server = cognos_analytics_server
        self.login_key = login_key
        self.session_key = ""
        self.response_objects = {}
        self.report_names = []
        self.folder_ids = []
        self.report_count = 0
        self.dataSource_names = []
        self.dataSource_ids = []
        self.dataSource_count = 0
        self.connection_names = []
        self.connection_ids = []
        self.connection_string = []
        self.connection_count = 0
        # self.data_conn_map = {}
        self.signons_names = []
        self.signons_ids = []
        self.signons_count = 0
        self.schema_ids = []
        self.schema_schemas = []
        self.schema_names = []
        self.schema_schemaTypes = []
        self.schema_count = 0



    def get_session(self, cognos_analytics_server, login_key):
        print("\nAuhenticating...")
        # Define the headers
        headers = {
            'Content-Type': 'application/json'
        }

        # Set the Authentication API URL
        authentication_url = f"{cognos_analytics_server}/api/v1/session"

        data = {
            "parameters": [
                {
                    "name": "CAMAPILoginKey",
                    "value": login_key
                }
            ]
        }

        # Convert the data to JSON
        data_json = json.dumps(data)

        # Send the POST request
        response = requests.put(authentication_url, headers=headers, data=data_json)

        # Check the response
        if response.status_code == 201:
            # Authentication successful
            response_data = response.json()
            # print(response.status_code)
            self.response_objects = {
                "IBM-BA-Authorization": f"CAM {response.cookies._cookies['us3.ca.analytics.ibm.com']['/api']['cam_passport'].value}"
            }
            # print(response_objects)
            print("\nAuthentication Successful.")
            # return response_objects
            # print(response_data)
            # session_key = response_data.get("session_key")
            # print(f"Authentication successful. Session Key: {session_key}")
        else:
            print(f"Authentication failed. Status Code: {response.status_code}")


    def get_content(self, cognos_analytics_server, response_objects):
        print("\nFetching Reports...")

        try:
            content = f"{cognos_analytics_server}/api/v1/content"
            # print(content)
            headers = {
                "Content-Type": "application/json",
                "IBM-BA-Authorization": f"{response_objects['IBM-BA-Authorization']}"
            }
            response = requests.get(content, headers=headers)
            content_response = response.json()
            # print(content_response)
            # print(response)

            if response.status_code == 200:
                print("\nSuccessfully fetched Reports")

                for d in content_response['content']:
                    if(d['type']=='folder'):
                        self.folder_ids.append(d['id'])
                    elif d['type'] == 'report':
                        report_names.append(d['defaultName'])
                        self.report_count = self.report_count + 1

                idx = 0
                while(True):
                    if(idx==len(self.folder_ids)):
                        break
                    print(idx)
                    # print(folder_ids[idx])
                    item = f"{cognos_analytics_server}/api/v1/content/{self.folder_ids[idx]}/items"
                    # print(item)
                    response = requests.get(item, headers=headers)
                    item_response = response.json()
                    print(item_response)
                    for d in item_response['content']:
                        if(d['type']=='folder'):
                            self.folder_ids.append(d['id'])
                        elif(d['type']=='report'):
                            self.report_names.append(d['defaultName'])
                            self.report_count = self.report_count + 1
                    # print(self.folder_ids)
                    # print()
                    idx = idx + 1
                print(self.report_count)
                print("Report Names: ")
                for report_name in self.report_names:
                    print(report_name)

            else:
                print("Unsuccessful")

        except Exception as e:
            print(e)


    def get_datasources(self, cognos_analytics_server):
        print("\nFetching DataSources...")
        try:
            datasources = f"{cognos_analytics_server}/api/v1/datasources"
            headers = {
                "Content-Type": "application/json",
                "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
            }
            response = requests.get(datasources, headers=headers)
            datasources_reponse = response.json()

            if response.status_code == 200:
                print("Successfully fetched dataSources")
                for d in datasources_reponse['dataSources']:
                    # print("Data Source ID:", d['id'])
                    # print("Data Source Type:", d['type'])
                    # print("Data Source Name:", d['defaultName'])
                    self.dataSource_names.append(d['defaultName'])
                    self.dataSource_ids.append(d['id'])
                    if(d['type']=='dataSource'):
                        self.dataSource_count = self.dataSource_count + 1
                    self.get_connections(cognos_analytics_server, d['id'])


                # print(self.dataSource_names)
                # print(self.dataSource_ids)
                # return self.dataSource_ids

            else:
                print("Unsuccessful")

        except Exception as e:
            print(e)

        print("Datasources")
        print(self.dataSource_names)
        print(self.dataSource_ids)
        print("Connections")
        print(self.connection_names)
        print(self.connection_ids)
        print(self.connection_string)
        print("Signons")
        print(self.signons_names)
        print(self.signons_ids)
        print(self.signons_count)
        print("Schemas")
        print(self.schema_ids)
        print(self.schema_names)
        print(self.schema_schemas)
        print(self.schema_schemaTypes)
        print(self.schema_count)


    def get_connections(self, cognos_analytics_server, datasource_id):
        print("\nFetching Connections...")
        # print(datasource_ids)
        try:
            # print(datasource_id)
            connections = f"{cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections"
            headers = {
                "Content-Type": "application/json",
                "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
            }
            response = requests.get(connections, headers=headers)
            connection_response = response.json()
            # print(response.status_code)

            if response.status_code == 200:
                print("Successfully fetched connections")
                # l1 = []
                for c in connection_response['connections']:
                    # print("Data Source ID:", d['id'])
                    # print("Data Source Type:", d['type'])
                    # print("Data Source Name:", d['defaultName'])
                    self.connection_names.append(c['defaultName'])
                    self.connection_ids.append(c['id'])
                    # l1.append(d['id'])
                    self.connection_string.append(c['connectionString'])
                    if (c['type'] == 'dataSourceConnection'):
                        self.connection_count = self.connection_count + 1
                    self.get_signons(cognos_analytics_server, datasource_id, c['id'])
                # data_conn_map[datasource_id] = l1
            else:
                print("Unsuccessful")

            # print(self.connection_names)
            # print(self.connection_ids)
            # print(self.connection_string)
            # print(self.connection_count)

            # return self.connection_ids

        except Exception as e:
            print(e)


    def get_signons(self, cognos_analytics_server, datasource_id, connection_id):
        # print(data_conn_map)
        print("\nFetching Signons...")
        global signons_count
        try:
            # print(datasource_id, connection_id)
            signons = f"{cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections/{connection_id}/signons"
            headers = {
                "Content-Type": "application/json",
                "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
            }
            response = requests.get(signons, headers=headers)
            signon_response = response.json()

            if response.status_code == 200:
                print("Successfully fetched signons")
                for s in signon_response['signons']:
                    # print("Data Source ID:", d['id'])
                    # print("Data Source Type:", d['type'])
                    # print("Data Source Name:", d['defaultName'])
                    self.signons_names.append(s['defaultName'])
                    self.signons_ids.append(s['id'])
                    if (s['type'] == 'dataSourceSignon'):
                        self.signons_count = self.signons_count + 1
                    self.get_schemas(cognos_analytics_server, datasource_id, connection_id, s['id'])
                    self.get_tables(cognos_analytics_server, datasource_id, connection_id, s['id'])

            else:
                print("Unsuccessful")
            # print(self.signons_names)
            # print(self.signons_ids)
            # print(self.signons_count)

        except Exception as e:
            print(e)


    def get_schemas(self, cognos_analytics_server, datasource_id, connection_id, signon_id):
        print("\nFetching Schemas...")
        try:
            schemas = f"{cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections/{connection_id}/signons/{signon_id}/schemas"
            headers = {
                "Content-Type": "application/json",
                "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
            }
            response = requests.get(schemas, headers=headers)
            schemas_response = response.json()

            if response.status_code == 200:
                print("Successfully fetched schemas")
                for sch in schemas_response['schemas']:
                    self.schema_ids.append(sch['id'])
                    self.schema_schemas.append(sch['schema'])
                    self.schema_names.append(sch['defaultName'])
                    self.schema_schemaTypes.append('schemaType')
                    self.schema_count = self.schema_count + 1
            else:
                print("Unsuccessful")

        except Exception as e:
            print(e)


    def get_tables(self, cognos_analytics_server, datasource_id, connection_id, signon_id):
        print("\nFetching Tables...")
        try:
            tables = f"{cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections/{connection_id}/signons/{signon_id}/schemas/tables"
            headers = {
                "Content-Type": "application/json",
                "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
            }
            response = requests.get(tables, headers=headers)

            if response.status_code == 200:
                print("Successfully fetched tables")

            else:
                print("Unsuccessful")

        except Exception as e:
            print(e)


    # def get_modules(self, cognos_analytics_server):
    #     try:
    #         modules = f"{cognos_analytics_server}/api/v1/modules"
    #         headers = {
    #             "IBM-BA-Authorization": f"{session_key}",
    #             "Content-Type": "application/xml"
    #         }
    #         response = requests.get(modules, headers=headers)
    #
    #         if response.status_code == 200:
    #             print("Successfully fetched modules")
    #         else:
    #             print("Unsuccessful")
    #
    #     except Exception as e:
    #         print(e)
    #
    #
    # def get_files(self, cognos_analytics_server):
    #     try:
    #         files = f"{cognos_analytics_server}/api/v1/files"
    #         headers = {
    #             "IBM-BA-Authorization": f"{session_key}",

    #             "Content-Type": "application/xml"
    #         }
    #         response = requests.get(files, headers=headers)
    #
    #         if response.status_code == 200:
    #             print("Successfully fetched files")
    #         else:
    #             print("Unsuccessful")
    #
    #     except Exception as e:
    #         print(e)



def main():
    cognos_analytics_server = "https://us3.ca.analytics.ibm.com"  # input("Enter Cognos Analytics Server link: ")
    login_key = "AWk1NUZBNUU4ODc4NEY0MDgyODhCQkM2MUFFOTlEMzU1QV7O4/X+HXmGgOoN9FB2X0VTZfaO"  # input("Enter CAMAPILoginKey: ")

    cognos_client = CognosApiClient(cognos_analytics_server, login_key)
    cognos_client.get_session(cognos_analytics_server, login_key)
    # cognos_client.get_content(cognos_analytics_server, response_objects)
    cognos_client.get_datasources(cognos_analytics_server)

if __name__ == "__main__":
    main()




# import requests
# import json
#
# # Define DataSource class
# class DataSource:
#     def __init__(self, name, type):
#         self.name = name
#         self.type = type
#         self.connections = Connection  # List to store Connection objects
#
#     def add_connection(self, connection):
#         self.connections.append(connection)
#
# # Define Connection class
# class Connection:
#     def __init__(self, name, type, connection_string):
#         self.name = name
#         self.type = type
#         self.connection_string = connection_string
#         self.sign_ons = [] # List to store Signon objects
#
# # Define Signon class
# class Signon:
#     def __init__(self, name):
#         self.name = name
#         self.schemas = []  # List to store Schema objects
#
# # Define Schema class
# class Schema:
#     def __init__(self, name, schema, schema_type):
#         self.name = name
#         self.schema = schema
#         self.schema_type = schema_type
#
# class CognosApiClient:
#     def __init__(self, cognos_analytics_server, login_key):
#         self.cognos_analytics_server = cognos_analytics_server
#         self.login_key = login_key
#         self.session_key = ""
#         self.response_objects = {}
#         self.report_names = []
#         self.folder_ids = []
#         self.report_count = 0
#         self.dataSource_names = []
#         self.dataSource_ids = []
#         self.dataSource_count = 0
#         self.connection_names = []
#         self.connection_ids = []
#         self.connection_string = []
#         self.connection_count = 0
#         # self.data_conn_map = {}
#         self.signons_names = []
#         self.signons_ids = []
#         self.signons_count = 0
#         self.schema_ids = []
#         self.schema_schemas = []
#         self.schema_names = []
#         self.schema_schemaTypes = []
#         self.schema_count = 0
#
#         self.data_sources = []  # List to store DataSource objects
#         self.connections = []  # List to store Connection objects
#         self.signons = []  # List to store Signon objects
#         self.schemas = []  # List to store Schema objects
#
#
#
#
#     def get_session(self, cognos_analytics_server, login_key):
#         print("\nAuhenticating...")
#         # Define the headers
#         headers = {
#             'Content-Type': 'application/json'
#         }
#
#         # Set the Authentication API URL
#         authentication_url = f"{cognos_analytics_server}/api/v1/session"
#
#         data = {
#             "parameters": [
#                 {
#                     "name": "CAMAPILoginKey",
#                     "value": login_key
#                 }
#             ]
#         }
#
#         # Convert the data to JSON
#         data_json = json.dumps(data)
#
#         # Send the POST request
#         response = requests.put(authentication_url, headers=headers, data=data_json)
#
#         # Check the response
#         if response.status_code == 201:
#             # Authentication successful
#             response_data = response.json()
#             # print(response.status_code)
#             self.response_objects = {
#                 "IBM-BA-Authorization": f"CAM {response.cookies._cookies['us3.ca.analytics.ibm.com']['/api']['cam_passport'].value}"
#             }
#             # print(response_objects)
#             print("\nAuthentication Successful.")
#             # return response_objects
#             # print(response_data)
#             # session_key = response_data.get("session_key")
#             # print(f"Authentication successful. Session Key: {session_key}")
#         else:
#             print(f"Authentication failed. Status Code: {response.status_code}")
#
#
#     def get_content(self, cognos_analytics_server, response_objects):
#         print("\nFetching Reports...")
#
#         try:
#             content = f"{cognos_analytics_server}/api/v1/content"
#             # print(content)
#             headers = {
#                 "Content-Type": "application/json",
#                 "IBM-BA-Authorization": f"{response_objects['IBM-BA-Authorization']}"
#             }
#             response = requests.get(content, headers=headers)
#             content_response = response.json()
#             # print(content_response)
#             # print(response)
#
#             if response.status_code == 200:
#                 print("\nSuccessfully fetched Reports")
#
#                 for d in content_response['content']:
#                     if(d['type']=='folder'):
#                         self.folder_ids.append(d['id'])
#                     elif d['type'] == 'report':
#                         report_names.append(d['defaultName'])
#                         self.report_count = self.report_count + 1
#
#                 idx = 0
#                 while(True):
#                     if(idx==len(self.folder_ids)):
#                         break
#                     print(idx)
#                     # print(folder_ids[idx])
#                     item = f"{cognos_analytics_server}/api/v1/content/{self.folder_ids[idx]}/items"
#                     # print(item)
#                     response = requests.get(item, headers=headers)
#                     item_response = response.json()
#                     print(item_response)
#                     for d in item_response['content']:
#                         if(d['type']=='folder'):
#                             self.folder_ids.append(d['id'])
#                         elif(d['type']=='report'):
#                             self.report_names.append(d['defaultName'])
#                             self.report_count = self.report_count + 1
#                     # print(self.folder_ids)
#                     # print()
#                     idx = idx + 1
#                 print(self.report_count)
#                 print("Report Names: ")
#                 for report_name in self.report_names:
#                     print(report_name)
#
#             else:
#                 print("Unsuccessful")
#
#         except Exception as e:
#             print(e)
#
#
#     def get_datasources(self, cognos_analytics_server):
#         print("\nFetching DataSources...")
#         try:
#             datasources = f"{cognos_analytics_server}/api/v1/datasources"
#             headers = {
#                 "Content-Type": "application/json",
#                 "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
#             }
#             response = requests.get(datasources, headers=headers)
#             datasources_reponse = response.json()
#
#             if response.status_code == 200:
#                 print("Successfully fetched dataSources")
#                 for d in datasources_reponse['dataSources']:
#                     # print("Data Source ID:", d['id'])
#                     # print("Data Source Type:", d['type'])
#                     # print("Data Source Name:", d['defaultName'])
#                     self.dataSource_names.append(d['defaultName'])
#                     self.dataSource_ids.append(d['id'])
#
#                     data_source = DataSource(
#                         name=d['defaultName'],
#                         type=d['type']
#                     )
#                     self.data_sources.append(data_source)
#
#                     if(d['type']=='dataSource'):
#                         self.dataSource_count = self.dataSource_count + 1
#                     self.get_connections(cognos_analytics_server, d['id'])
#
#
#                 # print(self.dataSource_names)
#                 # print(self.dataSource_ids)
#                 # return self.dataSource_ids
#
#             else:
#                 print("Unsuccessful")
#
#         except Exception as e:
#             print(e)
#
#         print("Datasources")
#         print(self.dataSource_names)
#         print(self.dataSource_ids)
#         print("Connections")
#         print(self.connection_names)
#         print(self.connection_ids)
#         print(self.connection_string)
#         print("Signons")
#         print(self.signons_names)
#         print(self.signons_ids)
#         print(self.signons_count)
#         print("Schemas")
#         print(self.schema_ids)
#         print(self.schema_names)
#         print(self.schema_schemas)
#         print(self.schema_schemaTypes)
#         print(self.schema_count)
#
#
#     def get_connections(self, cognos_analytics_server, datasource_id):
#         print("\nFetching Connections...")
#         # print(datasource_ids)
#         try:
#             # print(datasource_id)
#             connections = f"{cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections"
#             headers = {
#                 "Content-Type": "application/json",
#                 "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
#             }
#             response = requests.get(connections, headers=headers)
#             connection_response = response.json()
#             # print(response.status_code)
#
#             if response.status_code == 200:
#                 print("Successfully fetched connections")
#                 # l1 = []
#                 for c in connection_response['connections']:
#                     # print("Data Source ID:", d['id'])
#                     # print("Data Source Type:", d['type'])
#                     # print("Data Source Name:", d['defaultName'])
#                     self.connection_names.append(c['defaultName'])
#                     self.connection_ids.append(c['id'])
#                     # l1.append(d['id'])
#                     self.connection_string.append(c['connectionString'])
#
#                     connection = Connection(
#                         name=c['defaultName'],
#                         type=c['type'],
#                         connection_string=c['connectionString']
#                     )
#
#
#                     # Append the connection to the current data source
#                     self.data_sources.append(connection)
#
#                     if (c['type'] == 'dataSourceConnection'):
#                         self.connection_count = self.connection_count + 1
#                     # self.get_signons(cognos_analytics_server, datasource_id, c['id'])
#                 # data_conn_map[datasource_id] = l1
#             else:
#                 print("Unsuccessful")
#
#             # print(self.connection_names)
#             # print(self.connection_ids)
#             # print(self.connection_string)
#             # print(self.connection_count)
#
#             # return self.connection_ids
#
#         except Exception as e:
#             print(e)
#
#
#     def get_signons(self, cognos_analytics_server, datasource_id, connection_id):
#         # print(data_conn_map)
#         print("\nFetching Signons...")
#         global signons_count
#         try:
#             # print(datasource_id, connection_id)
#             signons = f"{cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections/{connection_id}/signons"
#             headers = {
#                 "Content-Type": "application/json",
#                 "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
#             }
#             response = requests.get(signons, headers=headers)
#             signon_response = response.json()
#
#             if response.status_code == 200:
#                 print("Successfully fetched signons")
#                 for s in signon_response['signons']:
#                     # print("Data Source ID:", d['id'])
#                     # print("Data Source Type:", d['type'])
#                     # print("Data Source Name:", d['defaultName'])
#                     self.signons_names.append(s['defaultName'])
#                     self.signons_ids.append(s['id'])
#                     if (s['type'] == 'dataSourceSignon'):
#                         self.signons_count = self.signons_count + 1
#                     self.get_schemas(cognos_analytics_server, datasource_id, connection_id, s['id'])
#                     self.get_tables(cognos_analytics_server, datasource_id, connection_id, s['id'])
#
#             else:
#                 print("Unsuccessful")
#             # print(self.signons_names)
#             # print(self.signons_ids)
#             # print(self.signons_count)
#
#         except Exception as e:
#             print(e)
#
#
#     def get_schemas(self, cognos_analytics_server, datasource_id, connection_id, signon_id):
#         print("\nFetching Schemas...")
#         try:
#             schemas = f"{cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections/{connection_id}/signons/{signon_id}/schemas"
#             headers = {
#                 "Content-Type": "application/json",
#                 "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
#             }
#             response = requests.get(schemas, headers=headers)
#             schemas_response = response.json()
#
#             if response.status_code == 200:
#                 print("Successfully fetched schemas")
#                 for sch in schemas_response['schemas']:
#                     self.schema_ids.append(sch['id'])
#                     self.schema_schemas.append(sch['schema'])
#                     self.schema_names.append(sch['defaultName'])
#                     self.schema_schemaTypes.append('schemaType')
#                     self.schema_count = self.schema_count + 1
#             else:
#                 print("Unsuccessful")
#
#         except Exception as e:
#             print(e)
#
#
#     def get_tables(self, cognos_analytics_server, datasource_id, connection_id, signon_id):
#         print("\nFetching Tables...")
#         try:
#             tables = f"{cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections/{connection_id}/signons/{signon_id}/schemas/tables"
#             headers = {
#                 "Content-Type": "application/json",
#                 "IBM-BA-Authorization": f"{self.response_objects['IBM-BA-Authorization']}"
#             }
#             response = requests.get(tables, headers=headers)
#
#             if response.status_code == 200:
#                 print("Successfully fetched tables")
#
#             else:
#                 print("Unsuccessful")
#
#         except Exception as e:
#             print(e)
#
#
#
#
# def main():
#     cognos_analytics_server = "https://us3.ca.analytics.ibm.com"  # input("Enter Cognos Analytics Server link: ")
#     login_key = "AWk1NUZBNUU4ODc4NEY0MDgyODhCQkM2MUFFOTlEMzU1QV7O4/X+HXmGgOoN9FB2X0VTZfaO"  # input("Enter CAMAPILoginKey: ")
#
#     cognos_client = CognosApiClient(cognos_analytics_server, login_key)
#     cognos_client.get_session(cognos_analytics_server, login_key)
#     # cognos_client.get_content(cognos_analytics_server, response_objects)
#     cognos_client.get_datasources(cognos_analytics_server)
#
#     data_sources = cognos_client.data_sources
#     for data_source in data_sources:
#         print(f"Data Source: {data_source.name} ({data_source.type})")
#         print(data_source.connections)
#         for connection in data_source.connections:
#             print(f"- Connection: {connection.name} ({connection.type})")
#             print(f"  Connection String: {connection.connection_string}")
#
# if __name__ == "__main__":
#     main()
#
#
