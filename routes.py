import json
import boto3

def lambda_handler(event, context):

    def add_route(rt,gw,reg,dest_prefix):
        #useful for debugging to prove the function run
        print("function adding route")
        #create boto3 resource in the correct region
        ec2 = boto3.resource('ec2', region_name=reg)
        #gets the route table into a variable
        route_table = ec2.RouteTable(rt)
        #creates the static route to the Transit Gateway
        route_table.create_route(
        DestinationCidrBlock=dest_prefix,
        TransitGatewayId= gw
        )

    def delete_route(rt,gw,reg,dest_prefix):
        #useful for debugging to prove the function run
        print ("function deleting route")
        #create boto3 resource in the correct region
        ec2 = boto3.resource('ec2', region_name=reg)
        #gets the relevant route
        route = ec2.Route(rt,dest_prefix)
        #deletes the route stored in route variable
        route.delete()

    def check_route(rt,reg,origin,dest_prefix):
        #Creates boto3 client session, this is required for the descibe_route_tables which isn't available in resources
        ec2_client = boto3.client('ec2', region_name=reg)
        #gets all routes in the current route table
        routes = ec2_client.describe_route_tables(RouteTableIds=[rt])
        #Convoluted loop due to what we get back from the boto3 client
        for x in range(len(routes['RouteTables'][0]['Routes'])):
            #Puts the relevant values into a dict
            current_route = {'Destination': (routes['RouteTables'][0]['Routes'][x]['DestinationCidrBlock']), 'Origin': (routes['RouteTables'][0]['Routes'][x]['Origin'])}
            #Tests if the rotue exists with the correct origin specified when the function was called (either static or dynamic)
            if current_route['Destination'] == dest_prefix and current_route['Origin'] == origin:
                return True

#======================================================================================================================

#Nested Dict of Route Tables and the Transit Gatewaqy the rotue should point at.
    route_tables = {'London-1': {'rt': 'rtb-03037d64a067051df', 'gw': 'tgw-0e05cb0cc8b5343c5', 'reg': 'eu-west-2'},
    'London-2' : {'rt': 'rtb-06b53b7ca44627078', 'gw': 'tgw-0e05cb0cc8b5343c5', 'reg': 'eu-west-2'}}

#Destination prefix of route to be added/deleted
    dest_prefix = '172.16.8.0/24'
#======================================================================================================================

#loop through all of the route-tables and check the status of the route table, then add/delete the route as required
    for loc, dict in route_tables.items():
        gw = dict['gw']
        rt = dict['rt']
        reg = dict['reg']
        print(rt)
        #Checks for the presence of the dynamic route, meaning Direct Connect is up
        dynamic = check_route(rt,reg,'EnableVgwRoutePropagation',dest_prefix)
        print("dynamic = {}".format(dynamic))
        #Checks for the Presence of the Static route, indicating we have failed over
        static = check_route(rt,reg,'CreateRoute',dest_prefix)
        print("static = {}".format(static))
        #Tests for scenario where direct connect has failed and we still need to failover i.e. no route present
        if dynamic == None and static == None:
            print("Failure detected - Adding Static")
            add_route(rt,gw,reg,dest_prefix)
            #Scenario where DC is back online and we need to fail back i.e. both a dynamic and a static route present
        if dynamic == True and static == True:
            print("Dynamic and Static Route detected - Deleting Static")
            delete_route(rt,gw,reg,dest_prefix)
    #        all other scenarios i.e. DC up static not present and DC down Static Present, do nothing.
    return None
