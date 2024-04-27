"""Generate device types from matter-devices.xml."""

import pathlib
import json
import xmltodict

REPO_ROOT = pathlib.Path(__file__).parent

CHIP_ROOT = REPO_ROOT / "../connectedhomeip"
ALL_XML = CHIP_ROOT / "src/app/zap-templates/zcl/data-model/all.xml"
BASE_CLUSTER_XML = CHIP_ROOT / "src/app/zap-templates/zcl/data-model/"

OUTPUT_JSON = REPO_ROOT / "out/clusterAttributeDefns.sql"

output = [
'''
--- Sql to populate the cluster and attribute defintions
--- This file is auto generated from `connectedhomeip/src/app/zap-templates/zcl/data-model/all.xml`
--- Run this script using $ python3 generate_cluster_defs_sql.py 
--- Do not override!

--- Cluster Definitions

INSERT INTO "ClusterDefn" (code,"name") VALUES'''
]

output2 = [
'''

--- Attribute Definitions

INSERT INTO "AttributeDefn" (code,"name",side,"clusterDefnCode") VALUES'''
]

def to_camelcase_string(input_string):
  #takes a string with underscores like START_UP_ON_OFF
  #and transforms to StartUpOnOff

  # Split the input string into individual words
  words = input_string.split('_')

  # Capitalize the first letter of each word except the first one
  camelcase_words = [words[0].capitalize()] + [word.capitalize() for word in words[1:]]

  # Join the CamelCase words together
  camelcase_string = ''.join(camelcase_words)

  return camelcase_string


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

        clusterSqlStr = """
	 ({cluster_code},'{cluster_name}'),""".format(cluster_name=clusterName,cluster_code=clusterCode)

        output.append(clusterSqlStr)

        if 'attribute' not in cluster: 
            break #skip if there are no attributes

        if not isinstance(cluster['attribute'], list):
            cluster['attribute'] = [cluster['attribute']]

        for attribute in cluster['attribute']:
            print(attribute)
            try: 
              if attribute['@side'] == 'server': #only take server commands

                  if '#text' in attribute: 
                      attribute_name = attribute['#text']
                  else:
                      attribute_name = to_camelcase_string(attribute['@define'])

                  attributeSqlStr =  """  
  ({attribute_code},'{attribute_name}','server',{cluster_code}),""".format(attribute_code=int(attribute['@code'],0), attribute_name=attribute_name,cluster_code=clusterCode)

                  output2.append(attributeSqlStr)

            except:
                print("An exception occurred")


                #put in the standard attributes in every cluster
        attributeSqlStr =  """
  (65528,'GeneratedCommandList','server',{cluster_code}),
  (65529,'AcceptedCommandList','server',{cluster_code}),
  (65530,'EventList','server',{cluster_code}),
  (65531,'AttributeList','server',{cluster_code}),
  (65532,'FeatureMap','server',{cluster_code}),
  (65533,'ClusterRevision','server',{cluster_code}),""".format(cluster_code=clusterCode)
        output2.append(attributeSqlStr)

    #Concatentate the cluster definition SQL
    formattedClusterSql = "".join(output)
    # Find the index of the last comma
    last_comma_index = formattedClusterSql.rfind(',')
    # Replace the last comma with a semicolon
    formattedClusterSql = formattedClusterSql[:last_comma_index] + ' ON CONFLICT (code) DO NOTHING;' + formattedClusterSql[last_comma_index + 1:]
    print(formattedClusterSql)

    #Concatentate the attribute definition SQL
    formattedAttributeSql = "".join(output2)
    # Find the index of the last comma
    last_comma_index = formattedAttributeSql.rfind(',')
    # Replace the last comma with a semicolon
    formattedAttributeSql = formattedAttributeSql[:last_comma_index] + ' ON CONFLICT DO NOTHING;' + formattedAttributeSql[last_comma_index + 1:]
    print(formattedAttributeSql)

    
    OUTPUT_JSON.write_text(formattedClusterSql+formattedAttributeSql)




def main():
    """Generate  types from all.xml."""
    data = xmltodict.parse(ALL_XML.read_text())

    for clusterData in data['all']['xi:include']:
        clusterHref = clusterData['@href']
        CLUSTER_XML = BASE_CLUSTER_XML / clusterHref
        processClusterXML(CLUSTER_XML)
        #When testing we use a break to get the first file
        #break


if __name__ == "__main__":
    main()