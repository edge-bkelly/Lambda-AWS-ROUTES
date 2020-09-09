import json
import boto3

def lambda_handler(event, context):

    def add_route(rt,gw,reg):
           ec2 = boto3.resource('ec2', region_name=reg)
           route_table = ec2.RouteTable(rt)
           route_table.create_route(
           DestinationCidrBlock='1.1.1.1/32',
           GatewayId= gw
           )

    routes = {'London-1': {'rt': 'rtb-058532a752007b308', 'gw': 'igw-0a372839e84ff8920', 'reg': 'eu-west-2'},
    'London-2' : {'rt': 'rtb-06b53b7ca44627078', 'gw': 'igw-0a372839e84ff8920', 'reg': 'eu-west-2'},
    'Ohio' : {'rt': 'rtb-c875aaa3', 'gw': 'igw-5c2a9a34', 'reg': 'us-east-2'}}

    for loc, dict in routes.items():
        gw = dict['gw']
        rt = dict['rt']
        reg = dict['reg']
        add_route(rt,gw,reg)

    return None
