import re

with open('progress-tracker.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Patterns to redact
patterns = [
    (r'HUGGINGFACE_API_KEY=.*', 'HUGGINGFACE_API_KEY=***'),
    (r'OPENAI_API_KEY=.*', 'OPENAI_API_KEY=***'),
    (r'GROQ_API_KEY=.*', 'GROQ_API_KEY=***'),
    (r'SERPER_API_KEY=.*', 'SERPER_API_KEY=***'),
    (r'ALPHA_VANTAGE_API_KEY=.*', 'ALPHA_VANTAGE_API_KEY=***'),
    (r'FMP_API_KEY=.*', 'FMP_API_KEY=***'),
    (r'NEWS_API_KEY=.*', 'NEWS_API_KEY=***'),
    (r'COINMARKETCAP_API_KEY=.*', 'COINMARKETCAP_API_KEY=***'),
    (r'BINANCE_API_KEY=.*', 'BINANCE_API_KEY=***'),
    (r'BINANCE_SECRET_KEY=.*', 'BINANCE_SECRET_KEY=***'),
    (r'TWITTER_API_KEY=.*', 'TWITTER_API_KEY=***'),
    (r'TWITTER_API_SECRET=.*', 'TWITTER_API_SECRET=***'),
    (r'TWITTER_ACCESS_TOKEN=.*', 'TWITTER_ACCESS_TOKEN=***'),
    (r'TWITTER_ACCESS_SECRET=.*', 'TWITTER_ACCESS_SECRET=***'),
]

new_lines = []
for line in lines:
    new_line = line
    for pattern, replacement in patterns:
        new_line = re.sub(pattern, replacement, new_line)
    new_lines.append(new_line)

with open('progress-tracker.md', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Secrets redacted line-by-line.')