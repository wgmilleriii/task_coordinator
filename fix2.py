import yaml
import datetime

task_file = 'tasks/active/T-INTY-017.yaml'
with open(task_file, 'r') as f:
    data = yaml.safe_load(f)

for k, v in data.items():
    if isinstance(v, datetime.datetime):
        data[k] = v.isoformat().replace('+00:00', 'Z')
        
if 'events' in data:
    for event in data['events']:
        for k, v in event.items():
            if isinstance(v, datetime.datetime):
                event[k] = v.isoformat().replace('+00:00', 'Z')

with open(task_file, 'w') as f:
    yaml.dump(data, f, sort_keys=False)
