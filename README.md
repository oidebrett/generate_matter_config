# generate matter config
Utility project to help generate matter configuration for a Matter dashboard frontend

### Generate device types from matter-devices.xml.

This script reads the xml cluster and device type definitions from the Matter SDK 

from this link:

project-chip/connectedhomeip/src/app/zap-templates/zcl/data-model/chip/*.xml

and produces jabascript object structures that can be used with a Nodejs front end application

the structure will contain mapping of clusters and attributes and commands

1. (only do this once) Create a Python Virtual Env

```bash
python3 -m venv build_env
```

2. Activate the Env

```bash
source build_env/bin/activate
```

3. Generate the command lis
```bash
(build_env) $ python3 generate_matter_config.py
```


4. When finished, get out of the env. Here’s how you deactivate a virtual environment:

```bash
(build_env) $ deactivate
```
