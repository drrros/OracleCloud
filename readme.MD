# Script for auto-generating A1 Flex instance

This script is used to continously (every 5 minutes) try to launch A1 Flex instance in Oracle Cloud.
Generated configuration is maximum for 24\7 usage on free tier (4 core \ 24 Gigs of RAM) with last version of Oracle Linux Cloud Developer.
To use script, you need first to get config file from Orace Cloud (Login to cloud console - Profile - 
Capabilities - View configuration file - copy and paste config to file within the same folder) - you need
to provide config file name as first parameter for script.
And then generate private key file in "API keys" section of Profile. Private key file should also be
placed in the same folder and file name should be provided as the second parameter for script.

After running the script you should provide:
- Public key for pasting to authorized_keys file on server


There is only one dependency for this script: oci package.

Within virtual environment:


`pip install -r requirements.txt`

or  

`pip install oci`

**Usage: python generate_a1_instance.py config_filename private_key_filename**