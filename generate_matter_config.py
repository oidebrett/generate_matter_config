"""Generate device types from matter-devices.xml."""

import pathlib
import json
import xmltodict

#REPO_ROOT = pathlib.Path(__file__).parent.parent
REPO_ROOT = pathlib.Path(__file__).parent

CHIP_ROOT = REPO_ROOT / "../connectedhomeip"
ALL_XML = CHIP_ROOT / "src/app/zap-templates/zcl/data-model/all.xml"
BASE_CLUSTER_XML = CHIP_ROOT / "src/app/zap-templates/zcl/data-model/"

OUTPUT_JSON = REPO_ROOT / "out/commandsList.json"

output = [
    '''
"""
Definitions for all known Device types.

This file is auto generated from `connectedhomeip/src/app/zap-templates/zcl/data-model/all.xml`
Do not override!
"""

'''
]

def processClusterXML(clusterXmlFile):
    #clusterXmlFile = BASE_CLUSTER_XML / "chip/chip-ota.xml"
    #clusterXmlFile = BASE_CLUSTER_XML / "chip/onoff-cluster.xml"
    #clusterXmlFile = BASE_CLUSTER_XML / "chip/scene.xml"
    print(clusterXmlFile)

    try:     
        """Generate  types from each xml file"""
        data = xmltodict.parse(clusterXmlFile.read_text())
    except:
        return #return if we cant open or parse the xml file

    if 'configurator' not in data: 
        return #skip if there are no configurator in the xml file

    if 'cluster' not in data['configurator']: 
        return #skip if there are no clusters in the xml file

    if not isinstance(data['configurator']['cluster'], list):
        data['configurator']['cluster'] = [data['configurator']['cluster']]

    for cluster in data['configurator']['cluster']:
        clusterName = cluster['name']
        clusterCode = int(cluster['code'], 0) #decode the hex string to an int

        if 'command' not in cluster: 
            break #skip if there are no commands

        if not isinstance(cluster['command'], list):
            cluster['command'] = [cluster['command']]

        for command in cluster['command']:

            try: 
                if command['@source'] == 'client': #only take client commands

                    command_payload = {}
                    #find out if there are any args
                    if 'arg' in command:
                        if not isinstance(command['arg'], list):
                            command['arg'] = [command['arg']]
                        for arg in command['arg']:
                            if 'int16u' == arg['@type']:
                                command_payload[arg['@name']] = 0
                            elif 'bitmap' in arg['@type'].lower():
                                command_payload[arg['@name']] = 0
                            elif 'enum' in arg['@type'].lower():
                                command_payload[arg['@name']] = 0
                            else:
                                command_payload[arg['@name']] = 0

                    command_payload = json.dumps(command_payload)
                    command_description = " ".join(command['description'].split())
                    command_description = command_description.replace('"', '\'')

                    commandJsonStr =  """,{{
"cluster":"{cluster_name}",
"clusterCode":"{cluster_code}",
"command":"{command_name}",
"code": {command_code},
"description":"{command_description}",
"jsonCommand": {{
"message_id" : "1000000000",
"command": "device_command",
"args": {{
    "endpoint_id":  1000000000,
    "node_id":  10000000000,
    "cluster_id": {cluster_code},
    "command_name": "{command_name}",
    "payload":{command_payload}
    }}
}}
}}""".format(
cluster_name=clusterName,
command_name=command['@name'],
command_code=int(command['@code'], 0), #decode the hex string to an int
cluster_code=clusterCode,
command_description=command_description,
command_payload=command_payload,
)
                    
                    print(commandJsonStr)

                    output.append(commandJsonStr)

            except:
                print("An exception occurred")

            formatted = "".join(output)
            
            OUTPUT_JSON.write_text(formatted)



def main():
    """Generate  types from all.xml."""
    data = xmltodict.parse(ALL_XML.read_text())

    for clusterData in data['all']['xi:include']:
        clusterHref = clusterData['@href']
        CLUSTER_XML = BASE_CLUSTER_XML / clusterHref
        processClusterXML(CLUSTER_XML)
        #break


if __name__ == "__main__":
    main()