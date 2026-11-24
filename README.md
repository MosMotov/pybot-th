<p align="center"><img src="assets/banner.png" alt="PyBot: no weights, no training, just rules" width="100%"></p>

<div align="center">
  <a href="https://huggingface.co/spaces/HuggingFaceSwarms/PyBot" target="_blank">
    <img alt="Hugging Face Space: PyBot demo" src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Demo-ffc107?color=ffc107&logoColor=white" />
  </a>
</div>

# PyBot: can Python be a chatbot?

## คุยกับ PyBot เป็นภาษาไทย

เปิดเทอร์มินัลในโฟลเดอร์โปรเจกต์ แล้วรันคำสั่งนี้เพื่อเริ่มแชตพร้อมเมนูภาษาไทย

```sh
python -m pybot --lang th
```

PyBot เลือกภาษาของคำตอบตามข้อความแต่ละรอบ คุณจึงสลับไทยกับอังกฤษกลางบทสนทนาได้
และใช้ `/รีเซ็ต` หรือ `/reset` เพื่อเริ่มใหม่ ตัวอย่างเช่น

```text
ผู้ใช้: สวัสดีค่ะ ฉันชื่อน้ำฝน
บอต: ยินดีที่ได้รู้จัก คุณน้ำฝน
ผู้ใช้: จำชื่อฉันได้ไหมคะ
บอต: คุณชื่อน้ำฝน
```

ถ้าต้องการถามครั้งเดียว ให้รัน `python -m pybot -p "เมืองหลวงของญี่ปุ่นคืออะไร"`
หรือส่งข้อความหลายบรรทัดผ่าน stdin เพื่อคุยต่อเนื่อง โหมดภาษาไทยทำงานออฟไลน์ด้วยกฎและชุดคำตอบ
รองรับการทักทาย จำชื่อ คำนวณ แปลงหน่วย บอกวันเวลา แปลคำศัพท์พื้นฐาน และตอบคำถามความรู้ทั่วไปบางหัวข้อ
ลองถามว่า `แมวภาษาอังกฤษเรียกว่าอะไร` หรือ `ต้มไข่กี่นาที` เมื่ออยู่นอกหัวข้อที่รองรับ บอตจะแจ้งให้ทราบเป็นภาษาไทย

## About the upstream project

LLMs drive today’s chatbots and agents, but chatbots long predate them. Sixty years ago, [ELIZA](https://en.wikipedia.org/wiki/ELIZA) held conversations by matching patterns in what the user typed and answering with predefined templates. It could seem insightful, but its repertoire was narrow, and expanding it meant writing more rules by hand. How far could a rule-based chatbot go if a swarm of agents did that work instead?

We challenged a swarm of over 1,000 agents to build a chatbot entirely in Python: no weights, no training, just if-else branches, regex patterns and lookup tables. The agents wrote and evaluated over 5,000 versions, and the chatbot’s win rate on [SmolTalkBench](https://huggingface.co/datasets/HuggingFaceSwarms/SmolTalkBench), where an LLM judge compares each reply with a reference answer, climbed from 0% to 26%. That puts it on par with SmolLM-360M-Instruct, which just a few years ago was state of the art for models under 1B parameters.

![PyBot's win rate over the evaluated commits on a log scale: every commit as a dot and the best so far as a line, with three SmolLM baselines as dashed lines, and its lines of Python code in grey on the right axis](assets/progress.png)

The result is PyBot: around 640k lines of code that can answer everyday questions, backed by 550k lines of tests the agents wrote themselves.

## Try it out

Run this checkout in your terminal for Thai and English chat. The [upstream browser demo](https://huggingface.co/spaces/HuggingFaceSwarms/PyBot) shows the original PyBot and the module that produced each reply.

PyBot needs Python 3.8 or newer and nothing else: no packages to install and no model to download.

```sh
python -m pybot
```

That starts a chat in your terminal:

```text
    ____        ____        __
   / __ \__  __/ __ )____  / /_
  / /_/ / / / / __  / __ \/ __/
 / ____/ /_/ / /_/ / /_/ / /_
/_/    \__, /_____/\____/\__/
      /____/

A chatbot written in plain Python. No weights, no training, just rules.
Type a message and press Enter. /reset starts a new conversation, /exit quits.

user: hi, i'm Sam
pybot: Nice to meet you, Sam. What can I help with?

user: my kettle is full of limescale, how do i get rid of it?
pybot: Half fill the kettle with equal parts water and white vinegar, or a sachet of citric acid, boil it and leave it half an hour, then tip it out and boil fresh water twice before you use it again. In a hard-water area do it every couple of months: the scale forms because hard water leaves calcium behind as it boils, and a thick layer makes the kettle slow and puts a scum on the tea.

user: how long does that take
pybot: Half an hour.

user: what's my name?
pybot: You're Sam.
```

Type `/reset` to clear the screen and start a new conversation, and `/exit` to quit. PyBot takes a few seconds to start, because Python has about 640,000 lines of code to load, and about a second to reply.

To ask one question and exit, or to pipe messages in and get one reply per line:

```sh
python -m pybot -p "Why do onions make you cry?"
echo "how long should i boil an egg" | python -m pybot
```

| Option | What it does |
|---|---|
| `-p TEXT`, `--prompt TEXT` | reply to this one message and exit |
| `-i`, `--interactive` | with `-p`, keep chatting after the first reply |
| `-s N`, `--seed N` | fix PyBot's choice of wording, to get the same replies again |
| `-v`, `--verbose` | after each reply, show the module that produced it and the time it took |
| `--lang en\|th` | choose English or Thai for the interactive terminal labels and commands (default: `en`) |

For a `pybot` command you can run from anywhere, install the clone with `pip install .`.

## What is in this repository

| Path | What it holds |
|---|---|
| `bot/` | The upstream PyBot engine and the Thai conversation, arithmetic and knowledge rules |
| `pybot.py` | the command line shown above. It contains no chatbot logic |
| `tests/` | Tests for the command line and Thai replies: `python -m unittest discover -s tests` |
| `assets/` | the banner and the chart |

Every turn, each module in `bot/modules/` may propose a reply, and an arbiter (`bot/modules/arbiter.py`) picks the one you get. The modules build on four shared parts:

| Part | Where | Lines |
|---|---|---:|
| Understanding engine: what you typed and meant, with typos, chat-speak, the topic and what "it" refers to | `bot/understanding/` | 25,000 |
| Memory store: what you and PyBot have said so far | `bot/memory/` | 109,000 |
| Knowledge base: facts about the world, kept as data | `bot/knowledge/` | 317,000 |
| Response composer: how a reply is phrased, and what to say when nothing fits | `bot/compose/` | 104,000 |

The modules themselves are another 81,000 lines.

## License

Apache License 2.0. See [LICENSE](LICENSE).
