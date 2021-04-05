import json

import data

with open("goals.json", "w", encoding='utf-8') as f:
    json.dump(data.goals, f)
with open("teachers.json", "w", encoding='utf-8') as f:
    json.dump(data.teachers, f)

#with open("goals.json", "r", encoding='utf-8') as f:
#    goals = json.load(f)
#with open("teachers.json", "r", encoding='utf-8') as f:
#    teachers = json.load(f)


