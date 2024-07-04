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

## Milestone

# Clearing the Screen
os.system('clear')

milestones = client.list_milestones(WorkloadId=selected_workload['WorkloadId'])['MilestoneSummaries']
milestone_names = []
for o in milestones:
    milestone_names = milestone_names + [o['MilestoneName']]

questions = [
  inquirer.List('MilestoneName',
                message="Milestone",
                choices=milestone_names,
            ),
]
answer = inquirer.prompt(questions)
selected_milestone = next((x for x in milestones if x['MilestoneName'] == answer['MilestoneName']), None)
# print(json.dumps(selected_milestone, default=json_serial, indent=4))

## Pillars
lens_review = client.get_lens_review(
    WorkloadId=selected_milestone['WorkloadSummary']['WorkloadId'],
    LensAlias=selected_milestone['WorkloadSummary']['Lenses'][0],
    MilestoneNumber=selected_milestone['MilestoneNumber'],
)['LensReview']['PillarReviewSummaries']
pillars = []
for o in lens_review:
    pillars = pillars + [o['PillarId']]
# print(json.dumps(pillars, default=json_serial, indent=4))

## Answers
list_answers = []
for pillar in pillars:
    pillar_answers = client.list_answers(
        WorkloadId=selected_milestone['WorkloadSummary']['WorkloadId'],
        LensAlias=selected_milestone['WorkloadSummary']['Lenses'][0],
        MilestoneNumber=selected_milestone['MilestoneNumber'],
        PillarId=pillar
    )['AnswerSummaries']
    list_answers = list_answers + pillar_answers

answers = []
for list_answer in list_answers:
    answer = client.get_answer(
        WorkloadId=selected_milestone['WorkloadSummary']['WorkloadId'],
        LensAlias=selected_milestone['WorkloadSummary']['Lenses'][0],
        QuestionId=list_answer['QuestionId'],
        MilestoneNumber=selected_milestone['MilestoneNumber'],
    )
    # print(json.dumps(answer['Answer'], default=json_serial, indent=4))
    answer['Answer']['LensAlias'] = selected_milestone['WorkloadSummary']['Lenses'][0]
    answers = answers + [answer['Answer']]
    print("{}: {}".format(answer['Answer']['PillarId'], answer['Answer']['QuestionTitle']))

# write to file
with open('answers.json', 'w') as f:
    f.write(json.dumps(answers, default=json_serial, indent=4))