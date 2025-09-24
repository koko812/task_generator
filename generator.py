
import os
from datetime import datetime
from openai import OpenAI

# APIキーは環境変数から読み込み
# export OPENAI_API_KEY="your_api_key"
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# ===== 固定の In-Context Examples =====
IN_CONTEXT_EXAMPLES = """
## Example question-answer pair: 1
### Input
You are given a question on high school macroeconomics. You are also given 4 answer options (associated with 'A', 'B', 'C',
'D'), out of which only one is correct. You need to answer the question by selecting the correct option. You should only
answer with the choice letter, not the whole answer.
Input: Allocative efficiency (A)means that no inferior products will be produced. (B)implies that the economy's output is
distributed evenly. (C)means that those who work hardest will get more. (D)implies that resources are used to produce
the goods and services society desires in just the right amounts.
Output:
### Expected output
D
### Plausible descriptions
Description 1: Your job is to analyze the provided question about economics. Use your understanding of economic
principles to guide your choice.
Description 2: Utilize your economic understanding to determine which choice is right. The correct answer will be the one
that best aligns with economic principles.

## Example question-answer pair: 2
### Input
In this task, you are given a country name and you need to return the capital city of the given country.
Input: Senegal
Output:
### Expected output
Dakar
### Plausible descriptions
Description 1: Given the name of a country, your job is to provide its capital city.
Description 2: For each country listed, determine and state its capital city. This requires familiarity with global locations
and capitals.
"""

# ===== タスクごとに差し替える Q-A ペア =====
QA_PAIRS = """
Here are some examples of the tasks you will be asked to solve.

## Example 1
Instruction: Write a function to find the shared elements from the given two lists. Your code should statisfy the following assertions:
```python
assert set(similar_elements((3, 4, 5, 6),(5, 7, 4, 10))) == set((4, 5))
assert set(similar_elements((1, 2, 3, 4),(5, 4, 3, 7))) == set((3, 4))
assert set(similar_elements((11, 12, 14, 13),(17, 15, 14, 13))) == set((13, 14))
```

```python
def similar_elements(test_tup1, test_tup2):
    res = tuple(set(test_tup1) & set(test_tup2))
    return (res)
```

## Example 2
Instruction: Write a python function to identify non-prime numbers. Your code should statisfy the following assertions:
```python
assert is_not_prime(2) == False
assert is_not_prime(10) == True
assert is_not_prime(35) == True
assert is_not_prime(37) == False
```

```python
import math
def is_not_prime(n):
    result = False
    for i in range(2,int(math.sqrt(n)) + 1):
        if n % i == 0:
            result = True
    return result
```

## Example 3
Instruction: Write a function to find the n largest integers from a given list of numbers, returned in descending order. Your code should statisfy the following assertions:
```python
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65]
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75]
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35]
```

```python
import heapq as hq
def heap_queue_largest(nums,n):
    largest_nums = hq.nlargest(n, nums)
    return largest_nums
```
"""

# ===== プロンプトを構築 =====
PROMPT = f"""
Given the following question-response pairs, please give a short description of the task describing what the task is.

{IN_CONTEXT_EXAMPLES}

Now, you must describe the task based on the following question-response pairs.
{QA_PAIRS}

Please use the information in the question-answer pairs and example description and come up with several descriptions
that explain the task. Each description should be written in plain text, with the following format.
Description 1: DESCRIPTION_1
Description 2: DESCRIPTION_2
...
You should also be creative and vary the structure and the length of the descriptions such that they'll be diverse and
cover various writing styles. You should ignore the specific question-answer pairs and focus on the high-level concept
and topic of the task in general.

**DO NOT** describe that there are multiple choice options or the format of the answer.
**DO NOT** include the answer format, e.g., 'choose the correct option', 'answer with only one word', etc.
**DO NOT** describe how to answer the question, but rather what the task is about and the skills and knowledge
required.

Response with 20 descriptions. Use simple words and please be clear and diverse in your descriptions.
"""

def main():
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a creative and helpful assistant."},
            {"role": "user", "content": PROMPT},
        ],
        temperature=0.8,
    )

    output_text = response.choices[0].message.content

    print("=== Model Output ===")
    print(output_text)

    # 保存先ファイル名（日付時刻入り）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"task_descriptions_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(output_text)

    print(f"\n>>> 保存しました: {filename}")

if __name__ == "__main__":
    main()

