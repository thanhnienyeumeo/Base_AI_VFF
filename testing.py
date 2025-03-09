path = 'data.json'
import json
with open(path, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)
while "\\\\" in raw_data:  
    raw_data = raw_data.replace("\\\\", "\\")
data = json.loads(raw_data)
print(len(data))
first_data = json.loads(data[0]['Content'])

blocks = first_data['blocks']
print(len(blocks))
for block in blocks:
    print(block['type'])
    print(block['data'])
    print('---')

