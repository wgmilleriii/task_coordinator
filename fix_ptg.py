import yaml
import glob
import os

priority_map = {"HIGH": "P1", "MEDIUM": "P2", "LOW": "P3"}

for filepath in glob.glob("tasks/active/T-PTG-11*.yaml"):
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    
    if 'repository' in data:
        data['repo'] = data.pop('repository')
    if data.get('repo') == 'pmtnm-resources':
        data['repo'] = 'newmexicoptg.org'
        
    if data.get('priority') in priority_map:
        data['priority'] = priority_map[data['priority']]
        
    if data.get('lane') == 'FEATURE':
        data['lane'] = 'ANY'
        
    if 'description' in data:
        desc = data.pop('description')
        data['scope'] = [line.strip() for line in desc.split('\n') if line.strip()]
        
    if 'created_at' not in data:
        data['created_at'] = '2026-08-27T12:00:00Z'
        
    if 'definition_of_done' in data and isinstance(data['definition_of_done'], str):
        data['definition_of_done'] = [line.strip().lstrip('- ') for line in data['definition_of_done'].split('\n') if line.strip()]
    elif 'definition_of_done' not in data:
        data['definition_of_done'] = ["Feature is fully implemented and tested."]
        
    with open(filepath, 'w') as f:
        yaml.dump(data, f, sort_keys=False)
