# 2miner-monitoring
simple python script to harvest 2miners and push data to elasticsearch

This script harvest data from 2miners API (https://apidoc.2miners.com/#/)

It send the data to an elasticsearch and on my case grafana is used to retrieves visualisation

To get Credentials ask Mozquito at contact@ether-source.fr or on discord.

To get etherscan api, please resgister at https://etherscan.io/.

## How to run it

### Config file

You have ton configure the config.yaml file (default is sample/config.yaml). All field is currently mandatory.

```yaml
---
wallet: "enter your eth wallet adresse"  
elasticsearch_user: "enter the user given by mozquito"
elasticsearch_password: "enter the password given by mozquito"
elasticsearch_host: "https://grafana.ether-source.fr"
elasticsearch_port: 9201
api_token_etherscan: "register at https://etherscan.io/ and put your token api here"
log_level: INFO
ca_path: "../ssl/autority_chain.pem"


# This part is to harvest correct information on your rig. This is an experimental way to collectd rig information
# I Do not have ay rig actually, i'm building my own, so i'm gonna improve this part

rig: This si the main struct of your rigs
- rig_name: "DESKTOP-TFG67DF"   Set the name of your rig (should be the same as worker in 2miners)
  cards: ["3060TI"]  list of cards in rig. Set a list of cards inside of the rig ["3060TI", "3070"]
  owners:             dict of owner of the rig. 
   - name: "Mozquito"   name of the owner. Set here the list of owner, if you are alone just set yourself or whatever.
     ratio: 100         % of ownership. Set here The % of ownership of this uer
- rig_name: "Rig_chamber":
  cards: ["3070", "3070", "3070", "3070"]
  owners:
   - name: "Mozquito"
     ratio: 73
   - name: "Baby Mozquito"
     ratio: 23
```

### Install requirement

You must run `pip install -r requirements.txt` to install python library

### Run the binary

This has been released and designed for windows at the begining, so if you're a windows user, use `python_monitor.bat`.
If you're on linux, simply run `python 2miner-monitoring/2miner-monitoring/__main__.py`


