import json

# Assume you have a json file named 'data.json'
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract the messages
messages = data['messages']

alpaca_format_data = {'dialogue': []}
for i in range(len(messages) - 1):
    # If a message starts with '!chat', include this message and the next one (assumed to be from 'DMaster')
    if messages[i]['content'].startswith('!chat') and messages[i+1]['author']['name'] == 'DMaster':
        user_content = messages[i]['content'].replace('!chat', '', 1).replace('!chat1', '', 1).replace('!chat2', '', 1).strip()
        alpaca_format_data['dialogue'].append({'role': 'user', 'content': user_content})
        
        bot_content = messages[i+1]['content']
        alpaca_format_data['dialogue'].append({'role': 'assistant', 'content': bot_content})

# Save the converted data
with open('alpaca_format_data.json', 'w', encoding='utf-8') as f:
    json.dump(alpaca_format_data, f, ensure_ascii=False, indent=4)
