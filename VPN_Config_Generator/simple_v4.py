≠≠=from jinja2 import Template
from ncclient.manager import Manager, connect
import yaml
import csv
import getpass
import netmiko
import paramiko
import time

def yaml_loader(filepath):
    with open(filepath,"r") as file_descriptor:
        data = yaml.full_load(file_descriptor)
    return data

def connect_router(host,username,password):
    conn = connect(
                    host = host,
                    port = 830,
                    username = username,
                    password = password,
                    hostkey_verify = False,
                    device_params = {'name':'csr'}
                    )
    return conn

def netconf_enable(host_access,username_access,password_access):
    ssh_session = netmiko.ConnectHandler(device_type='cisco_ios', ip=host_access,
                                                     username=username_access, password=password_access)

    ssh_session.send_command("terminal length 0")
    ssh_session.send_config_set("netconf-yang")
   
    config_commands = ['ip access-list extended 100', '10 permit ip 10.0.0.0 0.0.255.255 10.0.0.0 0.0.255.255'] 
    ssh_session.send_config_set(config_commands)
    ssh_session.disconnect()

    
def vpn_config(a_peerip,cnt):
    vpn_template = Template(open('vpn2.xml').read())
    vpn_rendered = vpn_template.render( 
        PEER_IPADD = a_peerip 
    )
    print('\n')
    print('Configuring VPN ......')
    print('\n')
    result = cnt.edit_config(target='running', config=vpn_rendered)
    return(result)

def device_config(access,a_device,a_peerip):
    for i in range(len(access)):
            
            if a_device == access[i]['name']:
                name_access= access[i]['name']
                host_access= access[i]['host']
                username_access= access[i]['username']
                password_access= access[i]['password']
                
                print('Connecting to '+name_access+' ......')
                netconf_enable(host_access,username_access,password_access)
                time.sleep(40)
  
                cnt = connect_router(host_access,username_access,password_access) 

                print('Connected !!!!')

                vpn_config(a_peerip,cnt)

                print('VPN Configured on '+name_access+' !!!!!!')


#**************Main Body***************        

customer_data = yaml_loader('customer_data.yaml')
access = customer_data['router']

with open('interface_vpn_v3.csv') as interface_file: 
    interface_data = csv.DictReader(interface_file)
    idata=interface_data
    
    for k in idata:
        a_device= k['adev']
        a_peerip= k['aippeer']
        b_device= k['bdev']
        b_peerip= k['bippeer']

        device_config(access,a_device,a_peerip)
        device_config(access,b_device,b_peerip)
        


            
    
    
    
    
    
