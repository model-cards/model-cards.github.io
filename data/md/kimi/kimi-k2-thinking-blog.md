<!-- page 1 -->

KIMI

- ProductsProducts
Products

Kimi Kimi Work Kimi Code Kimi Browser Extension Kimi Office Extension Downloads
All products

- APIAPI ↗

- BusinessBusiness

Kimi BusinessBusiness plansContact sales

- ResearchResearch

Kimi K3PerceptionBenchKimi K2.6Agent SwarmWorldVQAKimi K2.5Kimi Vendor VerifierKimi K2
ThinkingKimi K2

<!-- page 2 -->

All research

- HelpHelp
- PricingPricing
- DownloadDownload

Download

Download Try Kimi

1. <

<!-- page 3 -->

2. Research

# Introducing Kimi K2 Thinking

Today, we are introducing **Kimi K2 Thinking**, our best open-source thinking model.

Built as a **thinking agent**, it reasons step by step *while* using tools, achieving state-of-the-art performance on Humanity's Last Exam (HLE), BrowseComp, and other benchmarks, with major gains in reasoning, agentic search, coding, writing, and general capabilities.

Kimi K2 Thinking can execute up to **200 – 300 sequential tool calls** without human interference, reasoning coherently across hundreds of steps to solve complex problems.

It marks our latest efforts in **test-time scaling**, by scaling both thinking tokens and tool calling steps.

K2 Thinking is now live on kimi.com under the chat mode [1], with its full agentic mode available soon. It is also accessible through the Kimi K2 Thinking API.

## Evaluations

Kimi K2 Thinking sets new records across benchmarks that assess reasoning, coding, and agent capabilities. K2 Thinking achieves 44.9% on HLE with tools, 60.2% on BrowseComp, and 71.3% on SWE-Bench Verified, demonstrating strong generalization as a state-of-the-art thinking agent model.

## Agentic Reasoning

K2 Thinking demonstrates outstanding reasoning and problem-solving abilities. On Humanity's Last Exam (HLE)—a rigorously crafted, closed-ended benchmark—spanning thousands of expert-level questions across more than 100 subjects, K2 Thinking achieved **a state-of-the-art score of 44.9%**, with search, python, and web-browsing tools, establishing new records in multi-domain expert-level reasoning performance.

<!-- page 4 -->

By reasoning while actively using a diverse set of tools, K2 Thinking is capable of **planning, reasoning, executing, and adapting across hundreds of steps** to tackle some of the most challenging academic and analytical problems. In one instance, it successfully solved a **PhD-level mathematics problem** through **23 interleaved reasoning and tool calls**, exemplifying its capacity for deep, structured reasoning and long-horizon problem solving:

## Agentic Coding

K2 Thinking exhibits substantial gains in coding and software development tasks. It achieves scores of 61.1% on SWE-Multilingual, 71.3% on SWE-Bench Verified, and 47.1% on Terminal-Bench, showcasing strong generalization across programming languages and agent scaffolds.

The model delivers notable improvements on HTML, React, and component-intensive front-end tasks—translating ideas into fully functional, responsive products. In agentic coding settings, it reasons while invoking tools, integrating fluidly into software agents to execute complex, multi-step development workflows with precision and adaptability.

Here are some examples that Kimi K2 Thinking has built from a single prompt:

Component-heavy Website

Word clone

Example 1

Example 2

Example 3

Example 4

Example 5

## Welcome to WebWord

This is a feature-rich document editor with many capabilities similar to Microsoft Word. Start typing to create your document.

**Features include:**

Rich text formatting (bold, italic, underline, etc.)

## Agentic Search and Browsing

K2 Thinking demonstrates strong performance in agentic search and browsing scenarios. On BrowseComp—a challenging benchmark designed to evaluate models' ability to **continuously browse, search, and reason over hard-to-find real-world web information**—K2 Thinking achieved a score of **60.2%**, significantly outperforming the human baseline of 29.2%. This result highlights K2 Thinking's superior capability for goal-directed, web-based reasoning and its robustness in dynamic, information-rich environments.

K2 Thinking can execute **200–300 sequential tool calls**, driven by **long-horizon planning** and **adaptive reasoning**. It performs dynamic cycles of *think* → *search* → *browser use* → *think* → *code*, continually generating and refining hypotheses, verifying evidence, reasoning, and constructing coherent answers. This interleaved reasoning allows it to decompose ambiguous, open-ended problems into clear, actionable subtasks.

<!-- page 5 -->

Here's one example of what **Kimi K2 Thinking** has researched from just a single prompt:

## General Capabilities

**Creative Writing:** K2 Thinking delivers improvements in completeness and richness. It shows stronger command of style and instruction, handling diverse tones and formats with natural fluency. Its writing becomes more vivid and imaginative—poetic imagery carries deeper associations, while stories and scripts feel more human, emotional, and purposeful. The ideas it expresses often reach greater thematic depth and resonance.

**Practical Writing:** K2 Thinking demonstrates marked gains in reasoning depth, perspective breadth, and instruction adherence. It follows prompts with higher precision, addressing each requirement clearly and systematically—often expanding on every mentioned point to ensure thorough coverage. In academic, research, and long-form analytical writing, it excels at producing rigorous, logically coherent, and substantively rich content, making it particularly effective in scholarly and professional contexts.

**Personal & Emotional:** When addressing personal or emotional questions, K2 Thinking responds with more empathy and balance. Its reflections are thoughtful and specific, offering nuanced perspectives and actionable next steps. It helps users navigate complex decisions with clarity and care—grounded, practical, and genuinely human in tone.

<!-- page 6 -->

## Inference Efficiency

Low-bit quantization is an effective way to reduce inference latency and GPU memory usage on large-scale inference servers. However, thinking models use excessive decoding lengths, and thus quantization often results in substantial performance drops.

To overcome this challenge, we adopt Quantization-Aware Training (QAT) during the post-training phase, applying INT4 weight-only quantization to the MoE components. It allows K2 Thinking to support native INT4 inference with a roughly 2x generation speed improvement while achieving state-of-the-art performance. All benchmark results are reported under INT4 precision.

## Full Evaluations [2]

The table below shows that Kimi K2 Thinking matches or surpasses the latest open-source and frontier models across a wide range of tasks, excelling on benchmarks for reasoning, agentic search, and coding.

|  Benchmark | Intro | K2 Thinking | GPT-5 (High) | Claude Sonnet 4.5 (Thinking) | K2 0905 | DeepSeek-V3.2 | Grok-4  |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  Reasoning Tasks  |   |   |   |   |   |   |   |
|  Humanity's Last Exam (Text-only) | no tools | 23.9 | 26.3[3.b] | 19.8* | 7.9 | 19.8 | 25.4[3.b]  |
|   |  w/ tools [4] | 44.9 | 41.7[3.b] | 32.0* | 21.7 | 20.3* | 41.0[3.b]  |
|   |  heavy [6] | 51.0 | 42.0 | — | — | — | 50.7  |

<!-- page 7 -->

|  Benchmark | Intro | K2 Thinking | GPT-5 (High) | Claude Sonnet 4.5 (Thinking) | K2 0905 | DeepSeek-V3.2 | Grok-4  |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  AIME 2025 | no tools | 94.5 | 94.6 | 87.0 | 51.0 | 89.3 | 91.7  |
|   |  w/ python | 99.1 | 99.6 | 100.0 | 75.2 | 58.1* | 98.8  |
|   |  heavy [6] | 100.0 | 100.0 | — | — | — | 100.0  |
|  HMMT 2025 | no tools | 89.4 | 93.3 | 74.6* | 38.8 | 83.6 | 90.0  |
|   |  w/ python | 95.1 | 96.7 | 88.8* | 70.4 | 49.5* | 93.9  |
|   |  heavy [6] | 97.5 | 100.0 | — | — | — | 96.7  |
|  IMO-AnswerBench | no tools | 78.6 | 76.0*[3.c] | 65.9* | 45.8 | 76.0* | 73.1  |
|  GPQA-Diamond | no tools | 84.5 | 85.7 | 83.4 | 74.2 | 79.9 | 87.5  |
|  General Tasks  |   |   |   |   |   |   |   |
|  MMLU-Pro | no tools | 84.6 | 87.1 | 87.5 | 81.9 | 85.0 | —  |
|  MMLU-Redux | no tools | 94.4 | 95.3 | 95.6 | 92.7 | 93.7 | —  |
|  Longform Writing | no tools | 73.8 | 71.4 | 79.8 | 62.8 | 72.5 | —  |
|  HealthBench | no tools | 58.0 | 67.2 | 44.2 | 43.8 | 46.9 | —  |
|  Agentic Search Tasks [4]  |   |   |   |   |   |   |   |
|  BrowseComp | w/ tools | 60.2 | 54.9 | 24.1 | 7.4 | 40.1 | —  |
|  BrowseComp-ZH | w/ tools | 62.3 | 63.0* | 42.4* | 22.2 | 47.9 | —  |
|  Seal-0 | w/ tools | 56.3 | 51.4* | 53.4* | 25.2 | 38.5* | —  |
|  FinSearchComp-T3 | w/ tools | 47.4 | 48.5* | 44.0* | 10.4 | 27.0* | —  |
|  Frames | w/ tools | 87.0 | 86.0* | 85.0* | 58.1 | 80.2* | —  |
|  Coding Tasks [5]  |   |   |   |   |   |   |   |
|  SWE-bench Verified | w/ tools | 71.3 | 74.9 | 77.2 | 69.2 | 67.8 | —  |
|  SWE-bench Multilingual | w/ tools | 61.1 | 55.3* | 68.0 | 55.9 | 57.9 | —  |
|  Multi-SWE-bench | w/ tools | 41.9 | 39.3* | 44.3 | 33.5 | 30.6 | —  |
|  SciCode | no tools | 44.8 | 42.9 | 44.7 | 30.7 | 37.7 | —  |
|  LiveCodeBench v6 | no tools | 83.1 | 87.0* | 64.0* | 56.1* | 74.1 | —  |
|  OJ-Bench(cpp) | no tools | 48.7 | 56.2* | 30.4* | 25.5* | 38.2* | —  |
|  Terminal-Bench | w/ simulated tools (JSON) | 47.1 | 43.8 | 51.0 | 44.5 | 37.7 | —  |

### Footnotes

1. To ensure a fast, lightweight experience, we selectively employ a subset of tools and reduce the number of tool call turns under the chat mode on kimi.com. As a result, chatting on kimi.com may not reproduce our benchmark scores. Our agentic mode will be updated soon to reflect the full capabilities of K2 Thinking.
2. Testing Details: a. All benchmarks were evaluated at temperature = 1.0 and 256 k context length for K2 Thinking, except for SciCode, for which we followed the official temperature setting of 0.0. b. HLE (no tools), AIME25, HMMT25, and GPQA were capped at a 96k thinking-token budget, while IMO-Answer Bench, LiveCodeBench and OJ-Bench were capped at a 128k thinking-token budget. Longform Writing was capped at a 32k completion-token budget. c. For AIME and HMMT (no tools), we report the average of 32 runs (avg@32). For AIME and HMMT (with Python), we report the average of 16 runs (avg@16). For IMO-AnswerBench, we report the average of 8 runs (avg@8).
3. Baselines: a. GPT-5, Claude-4.5-sonnet, Grok-4 results and DeepSeek-V3.2 results are quoted from the GPT-5 post, GPT-5 for Developers post, GPT-5 system card, claude-sonnet-4-5, grok-4, deepseek-v3.2, the public Terminal-Bench leaderboard (Terminus-2), the public Vals AI leaderboard and the artificialanalysis. Benchmarks for which no available public scores were re-tested under the same conditions used for k2

<!-- page 8 -->

thinking and are marked with an asterisk(*). For the GPT-5 test, we set the reasoning effort to high. b. The GPT-5 and Grok-4 on the HLE full set with tools are 35.2 and 38.6 from their official posts. In our internal evaluation on the HLE text-only subset, GPT-5 scores 41.7 and Grok-4 scores 38.6 (Grok-4's launch cited 41.0 on the text-only subset). For GPT-5's HLE text-only w/o tool, we use score from Scale.ai, and the official GPT-5 score on the HLE full set (no tools) is 24.8. c. For IMO-AnswerBench: GPT-5 scored 65.6 in the benchmark paper. We re-evaluated GPT-5 with official API and obtained a score of 76.

4. For HLE (w/ tools) and the agentic-search benchmarks: a. K2 Thinking was equipped with search, code-interpreter, and web-browsing tools. b. BrowseComp-ZH, Seal-0, FinSearchComp-T3 were run 4 times independently and the average is reported (avg@4). c. The evaluation used o3-mini as judge, configured identically to the official HLE setting; judge prompts were taken verbatim from the official repository. d. On HLE, the maximum step limit was 120, with a 48 k-token reasoning budget per step; on agentic-search tasks, the limit was 300 steps with a 24 k-token reasoning budget per step. e. When tool execution results cause the accumulated input to exceed the model's context limit (256k), we employ a simple context management strategy that hides all previous tool outputs. f. The web access to Hugging Face may lead to data leakage in certain benchmark tests, such as HLE. K2 Thinking can achieve a score of 51.3 on HLE without blocking Hugging Face. To ensure a fair and rigorous comparison, we blocked access to Hugging Face during testing.
5. For Coding Tasks: a. Terminal-Bench scores were obtained with the default agent framework (Terminus-2) and the provided JSON parser. b. For other coding tasks, the result was produced with our in-house evaluation harness. The harness is derived from SWE-agent, but we clamp the context windows of the Bash and Edit tools and rewrite the system prompt to match the task semantics. c. All reported scores of coding tasks are averaged over 5 independent runs.
6. Heavy Mode: K2 Thinking Heavy Mode employs an efficient parallel strategy: it first rolls out eight trajectories simultaneously, then reflectively aggregates all outputs to generate the final result. Heavy mode for GPT-5 denotes the official GPT-5 Pro score.

*[figure]*

*[figure]*

### Products

KimiKimi WorkKimi CodeKimi Browser ExtensionKimi PlatformDownloadsAll products

### Pricing

IndividualBusinessAPI

### Business

Kimi BusinessContact sales

### Research

Kimi K3 tech blogKimi K2.6 tech blogKimi K2.5 tech blogPerceptionBenchAgent SwarmWorldVQAAll research

<!-- page 9 -->

## Company

About usMoonshot AIBrand guidelinesTerms of ServicePrivacy Policy

© 2026 Moonshot AI|京ICP备2023011302号-14|京B2-20240852|京公网安备11010802043150号
