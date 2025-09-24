# task_description_gen.py
import os
import argparse
from datetime import datetime
from openai import OpenAI

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def build_prompt(in_context: str, qa_pairs: str, tail: str) -> str:
    # f-string / .format を使わず、素直に連結。外部ファイル内の { } に触れません。
    parts = [
        "Given the following question-response pairs, please give a short description of the task describing what the task is.",
        "",
        in_context,
        "",
        "Now, you must describe the task based on the following question-response pairs.",
        qa_pairs,
        "",
        tail
    ]
    return "\n".join(parts)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-context", default="prompts/in_context.txt")
    ap.add_argument("--qa-pairs", default="prompts/task_examples/boolq.txt")
    ap.add_argument("--tail", default="prompts/tail_instructions.txt",
                    help="末尾の制約・書式などの共通指示を入れるファイル")
    ap.add_argument("--model", default="gpt-4o-mini")
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--outfile-prefix", default="task_descriptions")
    args = ap.parse_args()

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    in_context = read_text(args.in_context)
    qa_pairs   = read_text(args.qa_pairs)
    tail       = read_text(args.tail)

    prompt = build_prompt(in_context, qa_pairs, tail)

    resp = client.chat.completions.create(
        model=args.model,
        messages=[
            {"role": "system", "content": "You are a creative and helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=args.temperature,
    )

    text = resp.choices[0].message.content

    print("=== Model Output ===")
    print(text)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outpath = os.path.join(args.outdir, f"{args.outfile_prefix}_{ts}.txt")
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(text)

    #print(f"\n>>> 保存しました: {outpath}")

if __name__ == "__main__":
    main()

