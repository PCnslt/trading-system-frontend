import re

with open('progress-tracker.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find the API Keys block
pattern = r'### API Keys Configured.*?(?=### |$)'
# Replace with redacted version
replacement = '### API Keys Configured\n**All APIs are FREE tier** – no cost, rate‑limited usage.\n\n```\nHUGGINGFACE_API_KEY=***\nOPENAI_API_KEY=***\nGROQ_API_KEY=***\nSERPER_API_KEY=***\nALPHA_VANTAGE_API_KEY=***\nFMP_API_KEY=***\nNEWS_API_KEY=***\nCOINMARKETCAP_API_KEY=***\nBINANCE_API_KEY=***\nBINANCE_SECRET_KEY=***\nTWITTER_API_KEY=***\nTWITTER_API_SECRET=***\nTWITTER_ACCESS_TOKEN=***\nTWITTER_ACCESS_SECRET=***\n```'

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('progress-tracker.md', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Secrets redacted in progress-tracker.md')