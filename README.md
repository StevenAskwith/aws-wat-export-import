# aws-wat-export-import
AWS Well Architected Tool Export and Import Scripts

# Usage
## Setup
```
python -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

## Run
Authenticate at the CLI with the account you want to export a milestoe from  
**Note:** Region is hard coded in script
```
python3 wat-export-milestone.py
```

Create a new report in the account you want to import the milestone into using the AWS Console i.e. manually.
Authenticate at the CLI with the account you want to import to  
**Note:** Region is hard coded in script
```
python3 wat-import-milestone.py
```
