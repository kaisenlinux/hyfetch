import json
from collections import Counter
from pathlib import Path

from openai import OpenAI

client = OpenAI()

if __name__ == '__main__':
    # Read reddit data
    # data = json.loads(Path('reddit.json').read_text('utf-8'))
    data = json.loads(Path('reddit_opinions.json').read_text('utf-8'))

    # Testing: Print all comments
    for cmt in data:
        print()
        print(f"{cmt['author']}")
        print(f"- {cmt['content']}")

    # Loop through each comment, ask GPT-4o to generate a verdict on
    # whether this comment support or oppose adding the flag
    opinions = []
    for cmt in data:
        if 'opinion' in cmt:
            opinions.append(cmt)
            continue

        out = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a data analyst asked to read reddit comments on a thread collecting "
                                              "opinions on adding the Hypersexual flag into a LGBT+ system information tool."},
                # One-shot learning example
                {"role": "user", "content": "Does the following comment support or oppose adding the flag? Please answer 'support' or 'oppose' or 'neutral'.\n\n"
                                            "Author: azaneko • 1d ago\nComment: I'd like a flag"},
                {"role": "system", "content": "Support"},
                # Asking the actual data
                {"role": "user", "content": "Does the following comment support or oppose adding the flag? Please answer 'support' or 'oppose' or 'neutral'.\n\n"
                                            f"Author: {cmt['author']}\nComment: {cmt['content']}"},
            ],
        )

        # Print the result
        res = out.choices[0].message.content.lower().strip()
        print("\n")
        print("Author:", cmt['author'])
        print("Comment:", cmt['content'])
        print("Opinion:", res)
        opinions.append({**cmt, 'opinion': res})
        Path('reddit_opinions.json').write_text(json.dumps(opinions, indent=2))

    # Count opinions and upvotes
    counter = Counter()
    for cmt in opinions:
        counter[cmt['opinion']] += cmt.get('upvotes') or 0

    print("\n")
    print("Opinions:")
    for k, v in counter.items():
        print(f"{k}: {v}")
