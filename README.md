# generate matter config
Utility project to help generate matter configuration for a Matter dashboard frontend

### Generate device types from matter-devices.xml.

This script reads the xml cluster and device type definitions from the Matter SDK 

from this link:

project-chip/connectedhomeip/src/app/zap-templates/zcl/data-model/chip/*.xml

and produces jabascript object structures that can be used with a Nodejs front end application

the structure will contain mapping of clusters and attributes and commands
