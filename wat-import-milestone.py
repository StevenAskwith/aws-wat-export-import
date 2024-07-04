import simplejson as json
from datetime import date, datetime
import boto3
import inquirer
import os

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))

## Region
os.system('clear')
account_client = boto3.client('account')
response = account_client.list_regions(MaxResults=50)

regions = []
for region in response['Regions']:
    if region['RegionOptStatus'] == 'ENABLED' or region['RegionOptStatus'] == 'ENABLED_BY_DEFAULT':
        regions = regions + [region['RegionName']]
questions = [
  inquirer.List('region',
                message="Region",
                choices=regions,
            ),
]        
region = inquirer.prompt(questions)
print(region)

client = boto3.client('wellarchitected', region_name=region['region'])

## Workload

# Clearing the Screen
os.system('clear')

workloads = client.list_workloads()['WorkloadSummaries']
workload_names = []
for o in workloads:
    workload_names = workload_names + [o['WorkloadName']]

questions = [
  inquirer.List('WorkloadName',
                message="Workload",
                choices=workload_names,
            ),
]
answer = inquirer.prompt(questions)
selected_workload = next((x for x in workloads if x['WorkloadName'] == answer['WorkloadName']), None)

# read JSON from file
with open('answers.json', 'r') as json_file:
    data=json_file.read()
    answers = json.loads(data)
    for answer in answers:
        print("{}: {}".format(answer['PillarId'], answer['QuestionTitle']))
        formated_choice_answers = {}
        for i in range(0, len(answer['ChoiceAnswers'])):
            if answer['ChoiceAnswers'][i]['Status'] == "SELECTED":
                continue # skip 
            elif answer['ChoiceAnswers'][i]['Reason'] == "":
                answer['ChoiceAnswers'][i]['Reason'] = "NONE"
            formated_choice_answers[answer['ChoiceAnswers'][i]['ChoiceId']] = {
                'Status': answer['ChoiceAnswers'][i]['Status'],
                'Reason': answer['ChoiceAnswers'][i]['Reason'],
                'Notes': answer['ChoiceAnswers'][i]['Notes']
            }
    
        if "Notes" not in answer:
            answer['Notes'] = ""

        if "Reason" not in answer:
            answer['Reason'] = "NONE"

        response = client.update_answer(
            WorkloadId=selected_workload['WorkloadId'],
            LensAlias=answer['LensAlias'],
            QuestionId=answer['QuestionId'],
            SelectedChoices=answer['SelectedChoices'],
            ChoiceUpdates=formated_choice_answers,
            Notes=answer['Notes'],
            IsApplicable=answer['IsApplicable'],
            Reason=answer['Reason']
        )
    # print(json.dumps(answers, default=json_serial, indent=4))