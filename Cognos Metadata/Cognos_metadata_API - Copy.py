import requests
import json

cognos_analytics_server = "https://us3.ca.analytics.ibm.com" #input("Enter Cognos Analytics Server link: ")
login_key = "AWk1NUZBNUU4ODc4NEY0MDgyODhCQkM2MUFFOTlEMzU1QV7O4/X+HXmGgOoN9FB2X0VTZfaO" #input("Enter CAMAPILoginKey: ")
session_key = ""

report_names = []
folder_ids = []
report_count = 0
dataSource_names = []
dataSource_ids = []
datasource_count = 0
connection_names = []
connection_ids = []
connection_string = []
connection_count = 0
data_conn_map = {}

signons_names = []
signons_ids = []
signons_count = 0


def get_session(cognos_analytics_server, login_key):
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
        response_objects = {
            "IBM-BA-Authorization": f"CAM {response.cookies._cookies['us3.ca.analytics.ibm.com']['/api']['cam_passport'].value}"
        }
        # print(response_objects)
        print("\nAuthentication Successful.")
        return response_objects
        # print(response_data)
        # session_key = response_data.get("session_key")
        # print(f"Authentication successful. Session Key: {session_key}")
    else:
        print(f"Authentication failed. Status Code: {response.status_code}")


def get_content(cognos_analytics_server, response_objects):
    print("\nFetching Reports...")
    global report_names, report_count, folder_ids
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
                    folder_ids.append(d['id'])
                elif d['type'] == 'report':
                    report_names.append(d['defaultName'])
                    report_count = report_count + 1

            idx = 0
            while(True):
                if(idx==len(folder_ids)):
                    break
                # print(idx)
                # print(folder_ids[idx])
                item = f"{cognos_analytics_server}/api/v1/content/{folder_ids[idx]}/items"
                # print(item)
                response = requests.get(item, headers=headers)
                item_response = response.json()
                # print(item_response)
                for d in item_response['content']:
                    if(d['type']=='folder'):
                        folder_ids.append(d['id'])
                    elif(d['type']=='report'):
                        report_names.append(d['defaultName'])
                        report_count = report_count + 1
                # print(folder_ids)
                # print()
                idx = idx + 1
            # print(report_count)
            # print("Report Names: ")
            # for report_name in report_names:
            #     print(report_name)

        else:
            print("Unsuccessful")

    except Exception as e:
        print(e)


def get_datasources(cognos_analytics_server):
    print("\nFetching DataSources...")
    global datasource_count
    try:
        datasources = f"{cognos_analytics_server}/api/v1/datasources"
        headers = {
            "Content-Type": "application/json",
            "IBM-BA-Authorization": f"{response_objects['IBM-BA-Authorization']}"
        }
        response = requests.get(datasources, headers=headers)
        datasources_reponse = response.json()

        if response.status_code == 200:
            print("Successfully fetched dataSources")
            for d in datasources_reponse['dataSources']:
                # print("Data Source ID:", d['id'])
                # print("Data Source Type:", d['type'])
                # print("Data Source Name:", d['defaultName'])
                dataSource_names.append(d['defaultName'])
                dataSource_ids.append(d['id'])
                if(d['type']=='dataSource'):
                    datasource_count = datasource_count + 1


            print(dataSource_names)
            print(dataSource_ids)
            return dataSource_ids

        else:
            print("Unsuccessful")

    except Exception as e:
        print(e)


def get_connections(cognos_analytics_server, datasource_ids):
    print("\nFetching Connections...")
    # print(datasource_ids)
    global connection_count
    try:
        for datasource_id in datasource_ids:
            # print(datasource_id)
            connections = f"{cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections"
            headers = {
                "Content-Type": "application/json",
                "IBM-BA-Authorization": f"{response_objects['IBM-BA-Authorization']}"
            }
            response = requests.get(connections, headers=headers)
            connection_response = response.json()
            # print(response.status_code)

            if response.status_code == 200:
                print("Successfully fetched connections")
                l1 = []
                for d in connection_response['connections']:
                    # print("Data Source ID:", d['id'])
                    # print("Data Source Type:", d['type'])
                    # print("Data Source Name:", d['defaultName'])
                    connection_names.append(d['defaultName'])
                    connection_ids.append(d['id'])
                    l1.append(d['id'])
                    connection_string.append(d['connectionString'])
                    if (d['type'] == 'dataSourceConnection'):
                        connection_count = connection_count + 1
                data_conn_map[datasource_id] = l1

            else:
                print("Unsuccessful")

        print(connection_names)
        print(connection_ids)
        print(connection_string)
        print(connection_count)

        return connection_ids

    except Exception as e:
        print(e)


def get_signons(cognos_analytics_server):
    print(data_conn_map)
    print("\nFetching Signons...")
    global signons_count
    try:
        for datasource_id, connection_id1 in data_conn_map.items():
            for connection_id in connection_id1:
                print(datasource_id, connection_id)
                signons = f"{cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections/{connection_id}/signons"
                headers = {
                    "Content-Type": "application/json",
                    "IBM-BA-Authorization": f"{response_objects['IBM-BA-Authorization']}"
                }
                response = requests.get(signons, headers=headers)
                signon_response = response.json()

                if response.status_code == 200:
                    print("Successfully fetched signons")
                    for s in signon_response['signons']:
                        # print("Data Source ID:", d['id'])
                        # print("Data Source Type:", d['type'])
                        # print("Data Source Name:", d['defaultName'])
                        signons_names.append(s['defaultName'])
                        signons_ids.append(s['id'])

                        if (s['type'] == 'dataSourceSignon'):
                            signons_count = signons_count + 1

                else:
                    print("Unsuccessful")
                print(signons_names)
                print(signons_ids)
                print(signons_count)

    except Exception as e:
        print(e)


def get_schemas(cognos_analytics_server, datasource_id, connection_id, signon_id):
    try:
        schemas = f"{cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections/{connection_id}/signons/{signon_id}/schemas"
        headers = {
            "IBM-BA-Authorization": f"{session_key}",
            "Content-Type": "application/xml"
        }
        response = requests.get(schemas, headers=headers)

        if response.status_code == 200:
            print("Successfully fetched schemas")
        else:
            print("Unsuccessful")

    except Exception as e:
        print(e)


def get_tables(cognos_analytics_server, datasource_id, connection_id, signon_id):
    try:
        tables = f"{cognos_analytics_server}/api/v1/datasources/{datasource_id}/connections/{connection_id}/signons/{signon_id}/schemas/tables"
        headers = {
            "IBM-BA-Authorization": f"{session_key}",
            "Content-Type": "application/xml"
        }
        response = requests.get(tables, headers=headers)

        if response.status_code == 200:
            print("Successfully fetched tables")
        else:
            print("Unsuccessful")

    except Exception as e:
        print(e)


def get_modules(cognos_analytics_server):
    try:
        modules = f"{cognos_analytics_server}/api/v1/modules"
        headers = {
            "IBM-BA-Authorization": f"{session_key}",
            "Content-Type": "application/xml"
        }
        response = requests.get(modules, headers=headers)

        if response.status_code == 200:
            print("Successfully fetched modules")
        else:
            print("Unsuccessful")

    except Exception as e:
        print(e)


def get_files(cognos_analytics_server):
    try:
        files = f"{cognos_analytics_server}/api/v1/files"
        headers = {
            "IBM-BA-Authorization": f"{session_key}",
            "Content-Type": "application/xml"
        }
        response = requests.get(files, headers=headers)

        if response.status_code == 200:
            print("Successfully fetched files")
        else:
            print("Unsuccessful")

    except Exception as e:
        print(e)




datasource_id = ""
connection_id = ""
signon_id = ""


response_objects = get_session(cognos_analytics_server, login_key)
# get_content(cognos_analytics_server, response_objects)
datasource_ids = get_datasources(cognos_analytics_server)
connection_ids1 = get_connections(cognos_analytics_server, datasource_ids)
get_signons(cognos_analytics_server)
# get_schemas(cognos_analytics_server, datasource_id, connection_id, signon_id)
# get_tables(cognos_analytics_server, datasource_id, connection_id, signon_id)
# get_modules(cognos_analytics_server)
# get_files(cognos_analytics_server)
