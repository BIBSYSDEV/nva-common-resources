import boto3

client = boto3.client('lambda', region_name='eu-west-1')


def lambda_handler(event, context):
    functions_paginator = client.get_paginator('list_functions')
    version_paginator = client.get_paginator('list_versions_by_function')

    for function_page in functions_paginator.paginate():
        for function in function_page['Functions']:
            aliases = client.list_aliases(FunctionName=function['FunctionArn'])
            alias_versions = [alias['FunctionVersion'] for alias in aliases['Aliases']]
            for version_page in version_paginator.paginate(FunctionName=function['FunctionArn']):
                for version in version_page['Versions']:
                    arn = version['FunctionArn']
                    if version['Version'] != function['Version'] and version['Version'] not in alias_versions:
                        print('  🥊 {}'.format(arn))
                        client.delete_function(FunctionName=arn)
