<!-- page 1 -->

arXiv:2604.26752v3 [cs.CV] 12 May 2026

# GLM-5V-Turbo: Toward a Native Foundation Model for Multimodal Agents

GLM-5V-Turbo Team

Z.ai & Tsinghua University

(For the complete list of authors, please refer to the Contribution section)

## Abstract

We present GLM-5V-Turbo, a step toward native foundation models for multimodal agents. As foundation models are increasingly deployed in real environments, agentic capability depends not only on language reasoning, but also on the ability to perceive, interpret, and act over heterogeneous contexts such as images, videos, webpages, documents, GUIs. GLM-5V-Turbo is built around this objective: multimodal perception is integrated as a core component of reasoning, planning, tool use, and execution, rather than as an auxiliary interface to a language model. This report summarizes the main improvements behind GLM-5V-Turbo across model design, multimodal training, reinforcement learning, toolchain expansion, and integration with agent frameworks. These developments lead to strong performance in multimodal coding, visual tool use, and framework-based agentic tasks, while preserving competitive text-only coding capability. More importantly, our development process offers practical insights for building multimodal agents, highlighting the central role of multimodal perception, hierarchical optimization, and reliable end-to-end verification.

## 1 Overview

Recent advances in foundation models have driven a shift from language understanding to agentic real-world interaction  \( [4; 28; 49] \) , opening up substantial opportunities for productivity gains in domains such as knowledge work  \( [12; 27; 22] \) , software engineering  \( [20] \) , and tasks that require interacting with graphical user interfaces  \( [16; 43] \) . A general-purpose agentic model requires not only advanced intelligence, but also the ability to natively process complex multimodal context—including images, videos, text, webpages, and documents—and to integrate these heterogeneous inputs into a unified process of perception, reasoning, and decision-making  \( [12; 5; 37] \) .

Toward this goal, we introduce a set of coordinated advances in model design, training, and infrastructure to enable more native multimodal modeling. In model design, we develop CogViT, a new vision encoder tailored for multimodal fine-grained understanding, and propose Multimodal Multi-Token Prediction, which supports both text-only and multimodal inputs while remaining friendly to large-scale infrastructure. In training, we deeply integrate vision and language throughout pre-training and supervised fine-tuning, and further perform joint reinforcement learning over more than 30 task categories spanning perception, reasoning, and agentic capabilities, supported by an optimized infrastructure stack for large-scale multimodal RL. Building on these advances, we further expand GLM-5V-Turbo's multimodal agentic capabilities through toolchain extension, framework integration, and ecosystem development. We present a vision-centric deep search benchmark ImageMining that evaluates models' ability to "think and deep search with image".

These developments endow GLM-5V-Turbo with native multimodal agentic capability, while retaining strong text-based agentic and coding performance relative to its language-only base model GLM-5-Turbo. This is reflected both in benchmark results and in its effectiveness in practical agentic

<!-- page 2 -->

settings, including chatbot-style environments such as Z.ai and framework-based scenarios such as Claude Code [3] and OpenClaw [29]. GLM-5V-Turbo achieves strong results on multimodal agentic benchmarks, including multimodal tool use (30.7 on ImageMining, 51.9 on BrowseComp-VL [10], 72.9 on MMSearch [18], and 78.2 on SimpleVQA [7]), GUI agent tasks (75.7 on AndroidWorld [30] and 62.3 on OSWorld [44]), and Claw-based evaluations (87.0/80.7 on PinchBench [1], 57.7/75.0 on ClawEval [46], and 57.6 on ZClawBench [2]). GLM-5V-Turbo also demonstrates strong coding performance in both multimodal and text-only settings. For the multimodal setting, GLM-5V-Turbo achieves 94.8 on Design2Code [31], outperforming Claude Opus 4.6 [4]; for the text-only setting, GLM-5V-Turbo preserves the coding capability of its language-only base model GLM-5-Turbo and even surpasses it on CC-Backend (22.8), CC-Frontend (68.4), and CC-RepoExploration (72.2) [49].

Developing GLM-5V-Turbo also surfaced several broader lessons for agentic model development. Perception remains foundational to higher-level multimodal capability, while agentic competence is often acquired more effectively through hierarchical optimization than through monolithic end-to-end training. In addition, end-to-end agent tasks require clear specification, reliable verification, and carefully controlled evaluation for effective construction, assessment, and optimization. In this report, we summarize the main practices and lessons from developing GLM-5V-Turbo to inform future work on native multimodal agents.

## 2 Model, Training, and Infrastructure

### 2.1 CogViT Vision Encoder

We develop CogViT, a novel parameter-efficient vision encoder tailored for multimodal perception and downstream agent-oriented tasks. It delivers strong capabilities in general object recognition, fine-grained understanding, as well as geometric and spatial perception. As illustrated in Figure 1, CogViT achieves competitive performance across these domains. To balance representation learning with cross-modal alignment, we employ a two-stage pretraining recipe.

*[figure]*

Figure 1: Performance comparison of CogViT with other state-of-the-art vision encoders across general and fine-grained multimodal tasks.

In the first stage, we use distillation-based masked image modeling to strengthen visual representations. Specifically, we train the student ViT to reconstruct the masked regions (35% masking ratio,  \( 224 \times 224 \)  resolution) in the feature spaces of dual teacher models: SigLIP2 [39] for semantic representations and DINOv3 [32] for texture features. The training data follows a quality-aware mixture strategy: 80% high-quality natural images, 10% instruction-following data, and 10% scientific imagery. We optimize with Muon [21] optimizer with a cosine decay schedule. Additionally, we introduce QK-Norm [15] to normalize query and key vectors before attention computation, effectively mitigating logit explosion and ensuring stability at scale.

The second stage shifts to contrastive image-text pretraining to align visual and textual features in a shared embedding space. Compared to the first stage, we introduce three key upgrades: (1) replacing

2

<!-- page 3 -->

the fixed  \( 224 \times 224 \)  resolution with the NaFlex [39] scheme to process variable-size inputs while preserving original aspect ratios; (2) scaling the global batch size to 64K using the sigmoid-based SigLIP loss, combined with a bidirectional distributed implementation for efficiency; and (3) utilizing an 8-billion bilingual (Chinese-English) image-text corpus to enhance cross-lingual understanding. We continue to optimize with Muon, assigning module-specific learning rates and decay schedules to the vision, text, and projection components.

### 2.2 Multimodal Multi-Token Prediction

We propose Multimodal Multi-Token Prediction (MMTP), a multimodal extension of multi-token prediction (MTP) [11], designed to support both text-only and multimodal inputs while remaining friendly to large-scale infrastructure. The goal is to preserve acceptable length as well as training and inference efficiency in multimodal settings. In standard text-only MTP, prefix tokens can be passed into the MTP head directly through token IDs and embedded with the word embedding layer. Once MTP is extended to multimodal inputs, however, a central question arises: how should image tokens be passed to the MTP head? To answer this, we systematically compare three alternatives: The first directly passes the visual embeddings from the LLM backbone input to the MTP head; The second masks out all visual tokens at the MTP head input, reducing the design to text-only MTP; The third preserves visual positional information, but replaces all visual tokens with a shared learnable \(<|image|>\) special token as the visual input representation.

Considering both optimization behavior and system efficiency, GLM-5V-Turbo ultimately adopts the third design. Compared with directly passing visual embeddings to the MTP head, using the \(<|image|>\) token removes the need to propagate visual embeddings across pipeline-parallel stages, substantially reducing communication complexity while improving system scalability and engineering maintainability. Empirically, according to the ablation study on a 0.5B model, the \(<|image|>\)-based design achieves lower training loss and more stable convergence than directly using visual embeddings. We hypothesize that this is because the MTP head is typically lightweight, and may not have sufficient modeling capacity to effectively absorb visual representations whose distribution differs substantially from that of text embeddings; by contrast, the \(<|image|>\) token presents the input in a more uniform form and thus alleviates this optimization difficulty. At the same time, compared with fully masking out visual tokens, this design remains naturally compatible with existing partitioning strategies such as sequence parallelism and context parallelism, without requiring additional handling for visual-embedding partitioning, alignment, or offset mapping, which reduces implementation complexity. Overall, the design gives GLM-5V-Turbo a more balanced trade-off among multimodal modeling capability, training stability, and system efficiency.

*[figure]*

Figure 2: Illustration of our multimodal multi-token prediction (MMTP) design. Bottom-left: Training loss curves comparing Option 1 and Option 3, where the adopted design achieves lower loss.

3

<!-- page 4 -->

### 2.3 Broad training across perception, reasoning, and agent capability

The practical performance of multimodal agents depends on the joint development of perception, reasoning, planning, and execution, making narrow, domain-specific optimization insufficient. To improve these capabilities, we deeply integrate vision and language starting from the pretraining stage, strengthening the model's native ability to represent and process multimodal context. During the pre-training phase, we utilize a mixture of plain text and multimodal data to foster a balanced development of diverse capabilities. The multimodal datasets encompass a wide array of categories, including world knowledge, interleaved image-text, OCR, coding, GUI, video, multimodal tool-use, spatial perception, grounding, and academic problem-solving. We place particular emphasis on multimodal coding data to better align visual understanding with code generation and to improve the model's performance in multimodal agentic tasks.

GLM-5V-Turbo further undergoes joint RL optimization over more than 30 task categories. We adopt several technical improvements such as relative visual policy optimization in UI-to-code tasks [45]. This broad training setup yields gains at multiple levels: on the perceptual side, the model improves on tasks such as 2D image grounding and pointing (compared to SFT, the RL stage achieves improvements of \(4.8\%\) and \(3.2\%\) On RefCOCO-avg [23] and PointBench [6] respectively), video understanding \((+5.6\%\) on MVBench [24]), 3D grounding \((+7.7\%\) on SUNRGBD [33]), OCR \((+4.2\%\) on OCRBench [25]), and chart understanding \((+7.7\%\) on CharXiv [40]); on reasoning-heavy tasks such as STEM \((+1.8\%\) on MMMU_Val [47], MMMU_Pro [48], MathVista [26] and LogicVista [42]), it exhibits greater stability in problem solving; and in agentic settings—including GUI agents \((+4.9\%\) on OSWorld [43]), coding agents \((+0.2\%\) on CC-Backend [49]), and general tool use \((+3.5\%\) on MMSearch [19] which demonstrates improved planning and execution). Importantly, these gains are not confined to a single task family, but remain relatively consistent across a broad set of tasks.

This multi-task RL setting also exhibits several properties that we have consistently observed in earlier explorations such as GLM-4.1V-Thinking and GLM-4.5V [37]. Compared with the cross-domain trade-offs often seen in SFT, RL tends to show weaker interference across domains, allowing multiple domains to improve together with stable gains. Interestingly, in domains with narrower distributions where single-task RL is often prone to oscillation, collaborative training can make optimization more stable by exposing the model to a richer distribution of strategies and steering it toward more robust solutions. Beyond this, we observe some transfer of thinking patterns across tasks: reasoning behaviors acquired in one domain can sometimes carry over to another and produce measurable benefits there as well. This suggests that the value of multi-task RL lies not only in covering a broader range of tasks, but also in inducing deeper sharing at the level of strategy patterns.

At the same time, broad coverage in joint optimization does not mean that the problem is fully resolved. We do observe that capabilities left uncovered during RL can sometimes decline after post-training, especially those more orthogonal to the trained task distribution. One plausible explanation is that, as RL proceeds, both model capacity and learned thinking patterns become increasingly concentrated around the sampled task distribution, weakening the model's ability to retain performance in under-represented domains. This suggests that the scope of task coverage during RL is itself an important factor shaping the model's eventual generalization boundary. Even when a target capability cannot be easily formulated directly as an RL task, semantically or structurally related proxy tasks may provide useful optimization signals. For example, RL on single-turn UI-to-code generation can support more complex multi-turn coding ability. Taken together, these observations suggest that multi-task collaborative RL, including on-policy distillation, is not merely a tool for improving individual capabilities, but a central path toward shaping a more unified multimodal capability structure over a broader agentic distribution.

### 2.4 Multimodal RL at Scale

In the agent era, training infrastructure faces much stricter demands on both efficiency and stability, especially in large-scale multi-task multimodal reinforcement learning (RL). Compared with conventional training, this setting must handle wide variation in prompt and response lengths, support both single-step and multi-step tasks, and coordinate one or more rule-based or model-based verifiers for each task. To address these challenges, we systematically redesign the training stack along four dimensions: unified task and reward abstraction, end-to-end asynchrony and stage overlap, fine-grained memory management for multimodal workloads, and topology-aware partitioning and load balancing for visual inputs.

4

<!-- page 5 -->

Unified task and reward abstraction. We build a unified VLM RL Gym that provides a consistent environment interface for both single-step and multi-step tasks, so that heterogeneous task types can be handled within the same training framework. In parallel, we introduce an independent reward system that centrally orchestrates multiple verifiers. Rule-based verifiers are executed locally and synchronously, while model-based judges are invoked asynchronously through APIs; their outputs are then combined into rewards through configurable aggregation strategies, without entangling verifier logic with the main training codepath. To improve observability in mixed-task training, each sample also carries a data-source tag, allowing source-specific metrics such as reward and pass@k to be aggregated across parallel groups and reported separately.

Full-pipeline decoupling, asynchrony, and stage overlap. We restructure the training pipeline to decouple rollout inference, reward evaluation, batch construction and weight transfer, to maximize overlap across these stages. Each inference request is registered with a completion callback, so reward computation can be triggered as soon as that request finishes, rather than waiting for the entire rollout batch to complete; this reduces pipeline idle time caused by long-tail requests. Batch construction is executed in parallel with CPU–GPU transfer of old-policy weights. For the reference model, parameters remain resident on CPU memory, are asynchronously prefetched to GPU immediately before reference forward, and are released right after use, allowing reference computation to overlap effectively with the main training step. The system also supports two early-abort modes, based on either completion count or time threshold. Aborted prompts can be cached and reused, which helps control long-tail latency without materially reducing data utilization.

Fine-grained runtime memory management for multimodal workloads. Standard recomputation schemes are largely designed around text-only training and do not adequately address the memory bottlenecks introduced by multimodal inputs. To address this, we design separate memory-management strategies for the vision-side ViT and projector modules, combining targeted recomputation with CPU offloading. This prevents activation memory from scaling linearly with the number of images in the naïve way, and substantially reduces runtime memory pressure while preserving overall computational efficiency.

Topology-aware partitioning and dynamic load balancing for visual inputs. For visual inputs such as long videos, where sequence lengths vary significantly, we further introduce a topology-aware partitioning and dynamic load-balancing scheme. In a conventional implementation, partitioning is performed during the forward pass, which means each rank must first hold the full patch tensor before redistribution, leading to unnecessary memory and communication overhead. To address this, we move CP and TP partitioning upstream into the data-loading stage and align partition boundaries with downsample groups, thereby eliminating the need for cross-rank patch aggregation. After load balancing across DP groups, precise dispatch is carried out through asynchronous all-to-all communication, so that each rank receives only the partition it actually needs. We further move large Python objects off the GPU communication path and onto the CPU path, which reduces GPU communication buffer overhead by about 7 GB in practice. For the variable-length sequences produced during rollout, we additionally perform joint bin-packing over both sequence length and ViT token count, leading to better-balanced micro-batches for both compute and memory pressure.

## 3 Multimodal Agent Capabilities and Ecosystem

### 3.1 Multimodal Toolchain Expansion

GLM-5V-Turbo further expands its multimodal toolchain \( ^{1} \) , enabling the model to support a fuller perception–planning–execution loop in more realistic environments. In addition to expanding its repertoire of visual tools, the model demonstrates a sophisticated ability to maintain long-horizon engagement, frequently switching between multimodal search, annotation, screenshotting, and multimodal webpage reading tools to achieve thorough task resolution. Consequently, coding and task execution are no longer confined to textual interfaces but are instead iteratively grounded in a comprehensive, vision-based understanding of the environment.

\( ^{1} \) The proprietary tools can be accessed and experienced through GLM-5V-Turbo model on https://chat.z.ai/.

5

<!-- page 6 -->

Table 1: Categorization of multimodal tools and processing functions based on application scenarios and tool sets. Tools prefixed with zai_ are proprietary developments, while the GLM-5V-Turbo model also maintains compatibility with other user-defined custom tools.

|  Scenarios | Tool Sets | Tool Names  |
| --- | --- | --- |
|  General | Recognition Tools | zai_recognize_plant zai_recognize_location zai_recognize_person  |
|   |  Multimodal Search | zai_search_web_text zai_search_web_by_image zai_search_similar_images zai_search_web_images zai_search_scholar  |
|   |  Browser Tools | zai_load_image_from_url zai_read_webpage  |
|   |  Image Processing | zai_crop_image zai_draw_image_bounding_boxes zai_draw_image_point_markers zai_draw_image_geometry zai_draw_image_3d_bounding_boxes zai_draw_video_objects_tracking  |
|  Creation | Web Creation | submit_plan apply_edits zai_generate_web_html zai_generate_web_outline  |
|   |  Slide Creation | zai_generate_slide_html zai_generate_outline_ppt  |
|  Deep Research | Multimodal DR Tools | zai_dr_python zai_dr_open_url_mm zai_dr_visit_img zai_dr_search zai_dr_images_search zai_dr_images_lens  |

These architectural advancements are validated by significant performance gains across specialized benchmarks. Compared to our recent model GLM-4.6V [37], GLM-5V-Turbo demonstrates a substantial leap in complex multimodal tasks; notably, it achieves a score of 30.0 on MMSearchPlus [35], nearly an eightfold improvement over the previous generation. Strong growth is also evident in BrowseComp-VL [10] (51.9) and ImageMining (30.7), which specifically test the model's ability to navigate web interfaces and extract deep visual insights. By matching or exceeding the performance of industry benchmarks like Kimi K-2.5 [36] and Claude Opus 4.6 [4] in these categories, GLM-5V-Turbo proves its capability to handle the high-dimensional reasoning required for modern agentic workflows.

This expansion is particularly important for multimodal agents. Many real-world tasks are not simply a matter of reading text and calling functions; they require the model to first interpret the visual environment, decide what to do next, and then continue adapting its behavior based on the outcome of its actions. For example, when reproducing a real website, the model can first use a multimodal GUI agent to explore the site through screenshots, interaction with page elements, and navigation across pages, building a richer understanding of layout, functionality, and interaction flow. It can then rely on its native UI-to-code capability to reproduce the site more faithfully. Likewise, when media assets such as images need to be incorporated, they can be processed directly through native tools such as cropping before being embedded into the final output.

6

<!-- page 7 -->

### 3.2 Integration with External Agent Frameworks: Claude Code and AutoClaw

A critical component of GLM-5V-Turbo's deployment strategy is its seamless integration with industry-standard external agent frameworks. By moving beyond isolated tool calls, the model serves as the cognitive core for systems like Claude Code and AutoClaw [50], bridging the gap between high-level reasoning and low-level system execution. The integration with Claude Code transforms GLM-5V-Turbo from a passive code generator into an active system-level collaborator. Within this framework, the model leverages its multimodal capabilities to navigate complex terminal environments and local file systems. While Claude Code handles the logic and environment, AutoClaw provides the "hands" for browser-based and GUI-centric automation. GLM-5V-Turbo acts as the vision-language controller for AutoClaw, enabling sophisticated agentic workflows.

The convergence of GLM-5V-Turbo with these frameworks facilitates a complete perception-planning-execution loop. By offloading specific execution logic to Claude Code and AutoClaw, the model can focus on high-dimensional reasoning. This transition marks a fundamental shift in the model's role: it is no longer just a text-based assistant, but a multimodal actor grounded in real-world environments, capable of autonomous task resolution across diverse digital interfaces.

### 3.3 ImageMining: A Self-Collected Vision-Centric Deep Search Benchmark

The core potential of a multimodal agent lies in anchoring reasoning within visual contexts—a paradigm we term “think with image, deep search with image.” To evaluate this, we introduce ImageMining \( ^{2} \) , a benchmark designed to test the integration of high-density visual understanding and autonomous multimodal search.

Unlike traditional VQA [10; 19; 35], ImageMining requires models to actively mine visual inputs through agentic behaviors. Success relies on multi-step tool calls, such as localized cropping or magnification of minute details to refine search queries. This “Deep-Wide-Search” spectrum evaluates models on their search breadth across sources and their depth in visual reasoning, where task performance correlates strongly with the precision of on-image tool usage.

ImageMining comprises 217 curated test cases derived from manually collected trace samples, spanning seven domains (Social, Entertainment, Products, Places, Rich Text, Nature, and Science) and five reasoning categories:

- Universal Recognition: Fine-grained identification of flora, fauna, and artifacts.
- Spatio-Temporal Reasoning: Geographic deduction grounded in visual cues.
- Event Reasoning: Comprehension of news events and product launches.
- Text-based Reasoning: Reasoning over embedded rich text (e.g., academic papers, reports).
- Visual Search: Cross-referencing visual inputs to retrieve specific artworks or imagery.

To equip GLM-5V-Turbo with these capabilities, we developed a multi-stage automated data pipeline covering knowledge discovery, QA reconstruction, and quality filtering. A pivotal constraint in this process is the "Visual Jump" (WEB_VISUAL): during discovery, intermediate reasoning hops must involve visual transitions, forcing the model to parse images rather than relying on textual shortcuts or parametric knowledge. Furthermore, we constructed specialized OCR Search data for charts, maps, and posters. This compels the model to perform entity isolation and localized cropping before initiating search chains, transforming images from static inputs into interactive environments for deep exploration.

### 3.4 Multimodal Deep Research and Content Creation

Leveraging its agentic capabilities, GLM-5V-Turbo facilitates a complete multimodal deep research workflow, encompassing iterative information gathering, evidence consolidation, and long-form synthesis from heterogeneous sources. Unlike traditional text-centric agents  \( [12; 27] \) , this workflow begins with open-ended objectives and proceeds through autonomous cycles of planning, multimodal reading, and state updating. By natively parsing visually rich webpages, charts, and structured documents, the model accesses high-value evidence—such as slides and figures—that is typically discarded in text-only pipelines.

\( ^{2} \) https://github.com/zai-org/ImageMining

7

<!-- page 8 -->

*[figure]*

(a)

*[figure]*

(b)

Figure 3: Examples of multimodal deep research and content creation. (a) A multimodal deep research report, where the visuals are harvested from the Internet via web search, and selected and complied by GLM-5V-Turbo (Query: Compare OpenClaw and Hermes agent systems and give a comprehensive report. Note that the output should be a text-image interleaved markdown.). (b) A technical blog excerpted from an academic paper [49], where the visual elements are cropped from the original paper and inserted into the output to compose a complete blog, fully automated by GLM-5V-Turbo.

A defining characteristic of this system is its integrated multimodal reasoning. Rather than treating images as peripheral data, GLM-5V-Turbo extracts textual and visual evidence (e.g., table regions, screenshots) in tandem. This is crucial for realistic research environments where key insights are often distributed across document layouts and visual artifacts rather than isolated within text paragraphs.

Beyond information acquisition, GLM-5V-Turbo supports diverse, presentation-oriented downstream formats:

- Interleaved Reports: Generating text-image interleaved outputs (see Fig. 3 (a)) where visual evidence is embedded alongside grounded explanations—ideal for comparative analysis and literature reviews.
- Deep Research to PPT: Synthesizing gathered materials into structured slide decks, including page allocation and multimodal content organization, to mirror professional presentation workflows.
- Document-Style Write-ups: Creating blog-like interpretations or structured notes (see Fig. 3(b)) that maintain the visual-textual integrity of the research findings.

These capabilities further extend to document-grounded generation. Users can provide complex source materials for the model to reorganize into structured slides or interleaved interpretations. By preserving the synergy between textual conclusions and supporting visual evidence, GLM-5V-Turbo marks a system-level transition from simple multimodal information retrieval to comprehensive multimodal transformation and presentation.

### 3.5 Official Skills

As a foundation model adept at agentic and coding tasks, GLM-5V-Turbo can be readily integrated into general and coding agent frameworks (such as OpenClaw [34], AutoClaw [50] and Claude Code [3]), which are becoming increasingly popular in the community. To make it easier for users to utilize GLM-5V-Turbo within these agent systems, and to better leverage its strengths, we provide a set of official skills, which fall into two categories: one is built upon the native capabilities of the GLM-5V-Turbo model, and the other wraps GLM-5V-Turbo as an external tool (in the form of a MaaS API) for OpenClaw, AutoClaw and Claude Code to invoke. Additionally, we have developed 5 skills based on the previously released specialized models, GLM-OCR [8] and GLM-Image [38], to support a wider range of scenarios and tasks. To help users better understand, install, and use the official skills, we also provide a unified master skill (https://clawhub.ai/jaredforreal/glm-master-skill).

The official skills are listed in Tab. 2 and more details can be found in the Github repository: https://github.com/zai-org/GLM-skills.

8

<!-- page 9 -->

Table 2: Overview of official skills supported by GLM-5V-Turbo.

|  Skill | Type | URL  |
| --- | --- | --- |
|  PDF-to-Web | Native | https://clawhub.ai/zai-org/glmv-pdf-to-web  |
|  PDF-to-PPT | Native | https://clawhub.ai/zai-org/glmv-pdf-to-ppt  |
|  Web Replication | Native | https://clawhub.ai/zai-org/glmv-web-replication  |
|  PRD-to-App | Native | https://clawhub.ai/zai-org/glmv-prd-to-app  |
|  Stock Analyst | Native | https://clawhub.ai/zai-org/glmv-stock-analyst  |
|  Image Captioning | External Tool | https://clawhub.ai/JaredforReal/glmv-caption  |
|  Visual Grounding | External Tool | https://clawhub.ai/jaredforreal/glmv-grounding  |
|  Doc-based Writing | External Tool | https://clawhub.ai/jaredforreal/glmv-doc-based-writing  |
|  Resume Screening | External Tool | https://clawhub.ai/JaredforReal/glmv-resume-screen  |
|  Prompt Generation | External Tool | https://clawhub.ai/JaredforReal/glmv-prompt-gen  |
|  General OCR | Specialized | https://clawhub.ai/JaredforReal/glmocr  |
|  Table Recognition | Specialized | https://clawhub.ai/JaredforReal/glmocr-table  |
|  Handwriting Recognition | Specialized | https://clawhub.ai/JaredforReal/glmocr-handwriting  |
|  Formula Recognition | Specialized | https://clawhub.ai/JaredforReal/glmocr-formula  |
|  Image Generation | Specialized | https://clawhub.ai/JaredforReal/glm-image-gen  |

## 4 Design Lenses from Development

Beyond the developments described above, the process of building GLM-5V-Turbo also led us to several practical lenses for agentic model development. We present them not as universal rules, but as design perspectives that repeatedly proved useful in our development process.

Lens 1: Perception remains foundational to higher-level multimodal capability.

Recent work has placed increasing emphasis on higher-level abilities such as planning, reasoning, and reflection. Our observation, however, is that further gains in multimodal capability still depend critically on perception. Even among the strongest current VLMs, errors in fine-grained perception and spatial understanding remain common, and these often propagate into downstream reasoning, decision-making, and execution. Many failures that appear high-level, in other words, begin with the model not seeing the environment accurately enough.

In our development, multimodal coding and grounding proved to be useful proxy tasks for perceptual learning. Tasks such as frontend or SVG coding require the model to capture layout, structure, relative position, and local detail, rather than relying only on coarse semantics. We found that adding paired data between subject-specific images and their SVG representations during pretraining contributed positively to downstream STEM problem solving, while strengthening grounding-related training during RL also improved GUI-agent performance. These observations suggest that some seemingly downstream structured tasks can in fact provide a useful route to better perception.

We also find that explicitly training the model to critique its own perception can help reduce hallucination during generation. In GUI-agent instruction tuning, we include a subset of critic data that targets errors in the reasoning process, such as misreading interface details, misidentifying target elements, and making incorrect decisions about the next action. This improves the model's observation quality on GUI details and reduces several recurring perception failure modes. More broadly, our view is that perception is not a low-level module that can simply be solved early and then left behind; it continues to shape the upper bound of higher-level multimodal capability.

Lens 2: Agent capability can be more efficiently built through hierarchical optimization.

Agent training is inherently resource-intensive: environment setup and task construction are costly, high-quality data is scarce, and reliable verification is often difficult. At the same time, agent tasks themselves are hard to optimize efficiently, since they typically involve complex compositions, long interaction trajectories, non-unique solution paths, and strong dependence on the evolving environment state. Under these conditions, a central question is how to maximize the return on data construction under limited resources.

9

<!-- page 10 -->

This led us to adopt a hierarchical optimization strategy. In our experience, agent capability is developed more effectively when optimization is distributed across multiple levels of the capability hierarchy, rather than concentrated primarily on high-level long-horizon tasks. In GUI-agent development, for example, this motivated us to build a multi-level task hierarchy spanning element perception, GUI grounding, single-step action prediction, and trajectory-level action prediction, and to use it in both SFT and RL. The appeal of this design is twofold: lower-level tasks are usually easier to construct, annotate, and verify than long-horizon ones under the same resource constraints; and when lower-level capabilities are still underdeveloped, pushing only on high-level tasks often fails to yield reliable gains and can instead make training less stable. Overall, hierarchical optimization serves not only as a way to improve efficiency, but also as a practical path toward more stable agent training.

Lens 3: The key to constructing, evaluating, and optimizing end-to-end long-horizon tasks lies in clear task specification, reliable outcome verification, and controlled evaluation procedures.

For multimodal agents, the real challenge is often not extending tasks to longer horizons, but making end-to-end tasks stable enough to serve as meaningful targets for evaluation and optimization. Many realistic agent settings are inherently open-ended, with underspecified goals, ambiguous execution boundaries, and outcomes that depend heavily on intermediate decisions. As a result, they are often difficult to compare consistently and even harder to turn into reusable optimization signals.

This led us to a broader view: the value of an end-to-end task depends not only on how realistic it is, but also on whether it can be specified clearly enough, verified reliably enough, and evaluated under sufficient procedural control to produce stable and reusable feedback. This perspective shaped how we think about data construction, evaluation, and downstream optimization. In multimodal agent settings, task definition often depends on multiple sources of constraint rather than a single prompt alone, while evaluation needs structure not only at the level of final outcomes but also at the level of the verification process itself. Under this view, task definition, verification design, and feedback structure should be considered together rather than in isolation.

Vision2Web [14], our benchmark for end-to-end visual website development, is one concrete instantiation of this view. Each task is grounded not just in a textual instruction, but in a richer specification that may include PRDs, mockups, reference pages, and resource assets, making the task definition better specified. On the evaluation side, rather than treating website development as a loosely specified open-ended problem, we use workflow-based verification so that execution is assessed through a controlled sequence of dependent steps rather than a single final state. This makes it easier to compare systems, attribute failures, and model different forms of signal separately — for example, functional correctness during interactive execution and visual consistency in a more isolated comparison setting. In this sense, Vision2Web is not only a benchmark, but also a concrete attempt to align task construction, verification, and feedback design in a way that better supports reliable evaluation and optimization.

## 5 Evaluation

We evaluate GLM-5V-Turbo across four categories:

- Multimodal Coding: Desing2Code [31], Flame-VLM-Code [9], Vision2Web [14];
- Multimodal ToolUse: ImageMining, BrowseComp-VL [10], MMSearch [18], MMSearchPlus [35], SimpleVQA [7], Facts [17], V* [41];
- GUI Agent: OSWorld [44], AndroidWorld [30], WebVoyager [13];
- Text-only Coding and Claw: CC-Bench-V2 [49], PinchBench [1], ClawEval [46], ZClawBench [2].

Across these dimensions, GLM-5V-Turbo exhibits a consistent pattern: it achieves strong performance on multimodal benchmarks for coding and agent-oriented tasks, while maintaining solid capability on text-only tasks. This balance aligns with our core objective for GLM-5V-Turbo: building foundational multimodal agentic capability without sacrificing the coding and reasoning ability required in text-first workflows.

On multimodal coding and tool-use benchmarks, GLM-5V-Turbo performs strongly on UI-to-code generation, visual website development, multimodal search, and visually grounded QA. It is also

10

<!-- page 11 -->

|  Benchmarks |   | GLM-5V-Turbo | Kimi K2.5 | Claude Opus 4.6  |
| --- | --- | --- | --- | --- |
|  Multimodal Coding | Design2Code | 94.8 | 91.3 | 77.3  |
|   |  Flame-VLM-Code | 93.8 | 88.8 | 98.8  |
|   |  Vision2Web | 31.0 | 33.2 | 43.5  |
|  Multimodal ToolUse | ImageMining | 30.7 | 24.4 | -  |
|   |  BrowseComp-VL | 51.9 | 42.9 | 35.9  |
|   |  MMSearch | 72.9 | 58.7 | 63.8  |
|   |  MMSearch-Plus | 30.0 | 25.6 | 25.6  |
|   |  SimpleVQA | 78.2 | 71.5 | 63.2  |
|   |  Facts | 58.6 | 57.8 | -  |
|   |  V* | 89.0 | 84.3 | 66.5  |
|  GUI Agent | OSWorld | 62.3 | 63.3 | 72.2  |
|   |  AndroidWorld | 75.7 | 43.1 | 62.0  |
|   |  WebVoyager | 88.5 | 84.3 | 88.0  |

Figure 4: Evaluation of GLM-5V-Turbo on multimodal coding, tool-use, and GUI agent benchmarks.

highly competitive on GUI-agent benchmarks such as AndroidWorld and WebVoyager, indicating that its visual understanding transfers effectively into grounded interaction and action. At the same time, on CC-Bench-V2 including CC-Backend, CC-Frontend, and CC-Repo-Exploration which evaluate model performance on Claude Code framework, the model remains solid in pure-text coding, suggesting that the addition of visual capability does not materially erode its underlying coding performance, which is a critical feature for the multimodal agentic foundations.

|  Benchmarks |   | GLM-5V-Turbo | GLM-5-Turbo | Kimi K2.5 | Claude Opus 4.6  |
| --- | --- | --- | --- | --- | --- |
|  Coding | CC-Backend | 22.8 | 20.5 | 25.3 | 26.9  |
|   |  CC-Frontend | 68.4 | 69.4 | 62.3 | 75.9  |
|   |  CC-Repo-Exploration | 72.2 | 68.9 | 66.7 | 74.4  |
|  Claw | PinchBench(Best/Avg) | 87.0 / 80.7 | 86.5 / 81.1 | 84.8 / 79.2 | 93.3 / 82.9  |
|   |  ClawEval(Pass*3/Pass@3) | 57.7 / 75.0 | 51.0 / 72.1 | 52.9 / 73.1 | 66.3 / 77.9  |
|   |  ZclawBench | 57.6 | 60.6 | 49.1 | 62.3  |

Figure 5: Evaluation of GLM-5V-Turbo on text coding and claw agent benchmarks.

We also find that GLM-5V-Turbo transfers effectively to vision-enabled general agent frameworks. In particular, when integrated into Claw agent frameworks, the model can natively perceive on-screen content and act on it more effectively, leading to strong results on execution-oriented evaluations such as PinchBench, ClawEval, and ZClawBench. While Claw is only one representative framework, these results provide further evidence that the model's multimodal capability is not limited to isolated benchmark gains, but carries over to realistic end-to-end agent execution.

## 6 Remaining Challenges

Despite the progress described above, several challenges remain central to future agentic model development. In our view, the hardest open problems increasingly lie not in isolated capability improvement, but in agentic strategy emergence, long-horizon multimodal context management, and the growing entanglement between model capability and harness design.

How to enable the emergence of better agentic strategies. Agent training still depends heavily on hand-crafted or strongly filtered cold-start trajectories. This is effective for initialization, but it also narrows the space of reasoning and action patterns the model is likely to explore, so later

11

<!-- page 12 -->

improvement often remains local: the model becomes better at executing familiar paths, without discovering genuinely better ones. In our experiments, we found that increasing trajectory diversity at the cold-start stage can partially loosen this constraint, making it easier for RL to uncover nearby but improved variants. This suggests that trajectory diversity is not merely a matter of broader data coverage, but may be one of the conditions for strategy emergence itself. Still, this is only a first step. The more fundamental goal is to enable models to discover better reasoning and agentic strategies on their own, rather than remaining confined to variations of human-provided starting patterns. Beyond that lies an even harder challenge: enabling models to discover richer organizational forms, such as sub-agent decomposition, multi-agent collaboration, and more flexible hierarchical decision structures.

**Multimodal context management remains a core bottleneck for long-horizon agents.** Compared with text, images and especially videos consume context budget much more aggressively, making them expensive to retain over long trajectories. In practice, many systems respond by dropping earlier visual observations as context grows. While being an understandable engineering compromise, it also discards information that may remain important for later reasoning, planning, or verification. The challenge becomes sharper as trajectories lengthen. In text-only settings, systems such as Claude Code often respond to growing context pressure by compacting or summarizing earlier interaction history once the context window starts to fill up; in multimodal settings, however, faithful compression is much harder, because what must be preserved is not only semantic content, but also visual detail that may later become important again, such as layout, spatial relations, or temporal change in video. Most current memory mechanisms remain fundamentally text-centric: they are better at compressing what was said than what was seen, or how visual states evolved over time. For long-horizon multimodal agents, simply adapting text memory mechanisms will therefore be insufficient. What is needed instead is a more multimodal-native approach to context and memory.

**Model and harness increasingly co-shape the system's capability boundary.** For agentic systems, the effective capability boundary is no longer determined by the model alone, but jointly shaped by the model and the harness around it. This greatly expands the design space: task decomposition, tool use, memory mechanisms, and verification loops can all affect what the system is able to do in practice. At the same time, it makes the development path substantially complex: the same model may behave very differently under different decomposition strategies, tool-use policies, memory designs, or verification workflows; conversely, what appears to be a model limitation may sometimes reflect a poor harness choice instead. More importantly, this dependence runs both ways: the usefulness of a harness often depends on the model's capability regime, and designs that are ineffective at one stage may become critical once the model crosses a threshold in reasoning, planning, or feedback utilization. This means the harness is not a stable external layer that can be optimized independently of the model. Its role, value, and optimal form shift as the model evolves. More broadly, this means that agentic model development can no longer be framed as model improvement alone: the effective capability boundary is increasingly co-shaped by the model and the harness, and so too are the objectives by which progress is optimized and evaluated.

12

<!-- page 13 -->

# 7 Contribution

The contributors' names are listed in reverse alphabetical order (Z to A) by first name.

## Core Contributors

Ziyang Pan, Zhen Yang, Yuting Wang, Yue Wang, Yuanchang Yue, Yu Wang, Yanling Wang, Yan Wang, Xijun Liu, Wenmeng Yu, Weihan Wang, Wei Li, Shuaiqi Duan, Sheng Yang, Ruiliang Lv, Mingdao Liu, Lihang Pan, Ke Ning, Junhui Ji, Jinjiang Wang, Jing Chen, Jiazheng Xu, Jiale Zhu, Jiale Cheng, Ji Qi, Guobing Gan, Guo Wang, Cong Yao

## Contributors

Zijun Dou, Zihao Zhou, Zihan Wang, Zhiqi Ge, Zhijie Li, Zhenyu Hou, Zhao Xue, Zehui Wang, Zehan Qi, Zehai He, Yutao Zhang, Yusen Liu, Yukuo Cen, Yuchen Li, Yuan Wang, Yu Yang, Yongbin Liu, Yijian Lu, Yifan Xu, Yanzi Wang, Yanxiao Zhao, Yanfeng Wang, Yadong Xue, Yabo Xu, Xinyu Zhang, Xinyu Liu, Xiao Liu, Wenyi Zhao, Wenkai Li, Tianyu Tong, Tianshu Zhang, Shudan Zhang, Shengdong Yan, Qinkai Zheng, Mingde Xu, Licheng Bao, lat Long long, Jiaxing Xu, Jiaxin Fan, Jiawen Qian, Jiali Chen, Jiahui Lin, Jiadai Sun, Haozhi Zheng, Haoran Wang, Haochen Li, Hanyu Lai, Han Xu, Fan Yang, Dan Zhang, Da Yin, Chuangxin Zhao, Chengcheng Wu, Boyan Shi, Bowen Lv, Bowei Jia, Bo Li, Bin Chen, Baoxu Wang

## Tech Leads

Wenyi Hong, Xiaotao Gu

## Academic Advisors

Peng Zhang, Debing Liu, Bin Xu, Juanzi Li, Minlie Huang, Yuxiao Dong, Jie Tang

13

<!-- page 14 -->

## References

[1] Pinchbench. https://github.com/pinchbench/skill.

[2] Zclawbench. https://huggingface.co/datasets/zai-org/ZClawBench.

[3] Anthropic. Claude code: Ai-powered coding assistant, 2025. CLI tool and IDE extension for AI-assisted software development.

[4] Anthropic. Introducing claude opus 4.6. https://www.anthropic.com/news/claude-opus-4-6, Feb. 2026. Accessed: 2026-04-15.

[5] ByteDance Seed. Seed2.0 model card: Towards intelligence frontier for real-world complexity. https://lf3-static.bytednsdoc.com/obj/eden-cn/lapzild-tss/ljhwZthlaukjlkulzlp/seed2/0214/Seed2.0%20Model%20Card.pdf, 2026. Technical report / model card, accessed 2026-04-15.

[6] L. Cheng, J. Duan, Y. R. Wang, H. Fang, B. Li, Y. Huang, E. Wang, A. Eftekhar, J. Lee, W. Yuan, et al. Pointarena: Probing multimodal grounding through language-guided pointing. arXiv preprint arXiv:2505.09990, 2025.

[7] X. Cheng, W. Zhang, S. Zhang, J. Yang, X. Guan, X. Wu, X. Li, G. Zhang, J. Liu, Y. Mai, et al. Simplevqa: Multimodal factuality evaluation for multimodal large language models. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pages 4637–4646, 2025.

[8] S. Duan, Y. Xue, W. Wang, Z. Su, H. Liu, S. Yang, G. Gan, G. Wang, Z. Wang, S. Yan, D. Jin, Y. Zhang, G. Wen, Y. Wang, Y. Zhang, X. Zhang, W. Hong, Y. Cen, D. Yin, B. Chen, W. Yu, X. Gu, and J. Tang. Glm-ocr technical report, 2026.

[9] T. Ge, Y. Liu, J. Ye, T. Li, and C. Wang. Advancing vision-language models in front-end development via data synthesis. arXiv preprint arXiv:2503.01619, 2025.

[10] X. Geng, P. Xia, Z. Zhang, X. Wang, Q. Wang, R. Ding, C. Wang, J. Wu, Y. Zhao, K. Li, Y. Jiang, P. Xie, F. Huang, and J. Zhou. Webwatcher: Breaking new frontier of vision-language deep research agent, 2025.

[11] F. Gloeckle, B. Y. Idrissi, B. Rozière, D. Lopez-Paz, and G. Synnaeve. Better & faster large language models via multi-token prediction. arXiv preprint arXiv:2404.19737, 2024.

[12] Google Workspace. The latest updates for Deep Research in Gemini. https://workspaceupdates.googleblog.com/2025/05/deep-research-updates-gemini-io-2025.html, May 2025. Accessed: 2026-04-15.

[13] H. He, W. Yao, K. Ma, W. Yu, Y. Dai, H. Zhang, Z. Lan, and D. Yu. Webvoyager: Building an end-to-end web agent with large multimodal models. arXiv preprint arXiv:2401.13919, 2024.

[14] Z. He, W. Hong, Z. Yang, Z. Pan, M. Liu, X. Gu, and J. Tang. Vision2web: A hierarchical benchmark for visual website development with agent verification. arXiv preprint arXiv:2603.26648, 2026.

[15] A. Henry, P. R. Dachapally, S. S. Pawar, and Y. Chen. Query-key normalization for transformers. In Findings of the Association for Computational Linguistics: EMNLP 2020, pages 4246–4253, 2020.

[16] W. Hong, W. Wang, Q. Lv, J. Xu, W. Yu, J. Ji, Y. Wang, Z. Wang, Y. Dong, M. Ding, et al. Cogagent: A visual language model for gui agents. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pages 14281–14290, 2024.

[17] A. Jacovi, A. Wang, C. Alberti, J. L. Connie Tao, K. Olszewska, L. Haas, M. Liu, N. Keating, A. Bloniarz, C. Saroufim, C. Fry, D. Marcus, D. Kukliansky, G. S. Tomar, J. Swirhun, J. Xing, L. Wang, M. Aaron, M. Ambar, R. Fellinger, R. Wang, R. Sims, Z. Zhang, S. Goldshtein, Y. Matias, and D. Das. Facts leaderboard. https://kaggle.com/facts-leaderboard, 2024. Google DeepMind, Google Research, Google Cloud, Kaggle.

14

<!-- page 15 -->

[18] D. Jiang, R. Zhang, Z. Guo, Y. Wu, J. Lei, P. Qiu, P. Lu, Z. Chen, C. Fu, G. Song, et al. Mmsearch: Benchmarking the potential of large models as multi-modal search engines. arXiv preprint arXiv:2409.12959, 2024.

[19] D. Jiang, R. Zhang, Z. Guo, Y. Wu, J. Lei, P. Qiu, P. Lu, Z. Chen, C. Fu, G. Song, et al. Mmsearch: Benchmarking the potential of large models as multi-modal search engines. arXiv preprint arXiv:2409.12959, 2024.

[20] C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. Narasimhan. Swe-bench: Can language models resolve real-world github issues? arXiv preprint arXiv:2310.06770, 2023.

[21] K. Jordan et al. Muon: An optimizer for hidden layers in neural networks. https://kellerjordan.github.io/posts/muon/, 2024.

[22] A. Karpathy. Autoresearch: Ai agents running research, March 2026. AI agents running research on single-GPU nanochat training automatically.

[23] S. Kazemzadeh, V. Ordonez, M. Matten, and T. Berg. Referitgame: Referring to objects in photographs of natural scenes. In Proceedings of the 2014 conference on empirical methods in natural language processing (EMNLP), pages 787–798, 2014.

[24] K. Li, Y. Wang, Y. He, Y. Li, Y. Wang, Y. Liu, Z. Wang, J. Xu, G. Chen, P. Luo, et al. Mvbench: A comprehensive multi-modal video understanding benchmark. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 22195–22206, 2024.

[25] Y. Liu, Z. Li, M. Huang, B. Yang, W. Yu, C. Li, X.-C. Yin, C.-L. Liu, L. Jin, and X. Bai. Ocrbench: on the hidden mystery of ocr in large multimodal models. Science China Information Sciences, 67(12):220102, 2024.

[26] P. Lu, H. Bansal, T. Xia, J. Liu, C. Li, H. Hajishirzi, H. Cheng, K.-W. Chang, M. Galley, and J. Gao. Mathvista: Evaluating mathematical reasoning of foundation models in visual contexts. arXiv preprint arXiv:2310.02255, 2023.

[27] OpenAI. Introducing deep research. https://openai.com/index/introducing-deep-research, February 2025. Accessed: 2026-04-15.

[28] OpenAI. Introducing gpt-5.4. https://openai.com/index/introducing-gpt-5-4/, Mar. 2026. Accessed: 2026-04-15.

[29] OpenClaw. Openclaw. https://github.com/openclaw/openclaw, 2026. GitHub repository, accessed 2026-04-15.

[30] C. Rawles, S. Clinckemaillie, Y. Chang, J. Waltz, G. Lau, M. Fair, A. Li, W. Bishop, W. Li, F. Campbell-Ajala, et al. Androidworld: A dynamic benchmarking environment for autonomous agents. arXiv:2405.14573, 2024.

[31] C. Si, Y. Zhang, R. Li, Z. Yang, R. Liu, and D. Yang. Design2code: Benchmarking multimodal code generation for automated front-end engineering. In Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers), pages 3956–3974, 2025.

[32] O. Siméoni, H. V. Vo, M. Seitzer, F. Baldassarre, M. Oquab, C. Jose, V. Khalidov, M. Szafraniec, S. Yi, M. Ramamonjisoa, et al. Dinov3. arXiv preprint arXiv:2508.10104, 2025.

[33] S. Song, S. P. Lichtenberg, and J. Xiao. Sun rgb-d: A rgb-d scene understanding benchmark suite. In Proceedings of the IEEE conference on computer vision and pattern recognition, pages 567–576, 2015.

[34] P. Steinberger. Openclaw: Open-source personal ai agent framework, 2026. Open-source AI agent platform for building autonomous agents.

[35] X. Tao, Y. Teng, X. Su, X. Fu, J. Wu, C. Tao, Z. Liu, H. Bai, R. Liu, and L. Kong. Mmsearch-plus: Benchmarking provenance-aware search for multimodal browsing agents. arXiv preprint arXiv:2508.21475, 2025.

15

<!-- page 16 -->

[36] K. Team, T. Bai, Y. Bai, Y. Bao, S. H. Cai, Y. Cao, Y. Charles, H. S. Che, C. Chen, G. Chen, H. Chen, J. Chen, J. Chen, J. Chen, J. Chen, K. Chen, L. Chen, R. Chen, X. Chen, Y. Chen, Y. Chen, Y. Chen, Y. Chen, Y. Chen, Y. Chen, Y. Chen, Y. Chen, Z. Chen, Z. Chen, D. Cheng, M. Chu, J. Cui, J. Deng, M. Diao, H. Ding, M. Dong, M. Dong, Y. Dong, Y. Dong, A. Du, C. Du, D. Du, L. Du, Y. Du, Y. Fan, S. Fang, Q. Feng, Y. Feng, G. Fu, K. Fu, H. Gao, T. Gao, Y. Ge, S. Geng, C. Gong, X. Gong, Z. Gongque, Q. Gu, X. Gu, Y. Gu, L. Guan, Y. Guo, X. Hao, W. He, W. He, Y. He, C. Hong, H. Hu, J. Hu, Y. Hu, Z. Hu, K. Huang, R. Huang, W. Huang, Z. Huang, T. Jiang, Z. Jiang, X. Jin, Y. Jing, G. Lai, A. Li, C. Li, C. Li, F. Li, G. Li, G. Li, H. Li, H. Li, J. Li, J. Li, J. Li, L. Li, M. Li, W. Li, W. Li, X. Li, X. Li, Y. Li, Y. Li, Y. Li, Z. Li, Z. Li, W. Liao, J. Lin, X. Lin, Z. Lin, Z. Lin, C. Liu, C. Liu, H. Liu, L. Liu, S. Liu, S. Liu, S. Liu, T. Liu, T. Liu, W. Liu, X. Liu, Y. Liu, Y. Liu, Y. Liu, Y. Liu, Z. Liu, Z. Liu, E. Lu, H. Lu, Z. Lu, J. Luo, T. Luo, Y. Luo, L. Ma, Y. Ma, S. Mao, Y. Mei, X. Men, F. Meng, Z. Meng, Y. Miao, M. Ni, K. Ouyang, S. Pan, B. Pang, Y. Qian, R. Qin, Z. Qin, J. Qiu, B. Qu, Z. Shang, Y. Shao, T. Shen, Z. Shen, J. Shi, L. Shi, S. Shi, F. Song, P. Song, T. Song, X. Song, H. Su, J. Su, Z. Su, L. Sui, J. Sun, J. Sun, T. Sun, F. Sung, Y. Tai, C. Tang, H. Tang, X. Tang, Z. Tang, J. Tao, S. Teng, C. Tian, P. Tian, A. Wang, B. Wang, C. Wang, C. Wang, C. Wang, D. Wang, D. Wang, D. Wang, F. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang, H. Wang

[37] V. Team, W. Hong, W. Yu, X. Gu, G. Wang, G. Gan, H. Tang, J. Cheng, J. Qi, J. Ji, L. Pan, S. Duan, W. Wang, Y. Wang, Y. Cheng, Z. He, Z. Su, Z. Yang, Z. Pan, A. Zeng, B. Wang, B. Chen, B. Shi, C. Pang, C. Zhang, D. Yin, F. Yang, G. Chen, J. Xu, J. Zhu, J. Chen, J. Chen, J. Chen, J. Lin, J. Wang, J. Chen, L. Lei, L. Gong, L. Pan, M. Liu, M. Xu, M. Zhang, Q. Zheng, S. Yang, S. Zhong, S. Huang, S. Zhao, S. Xue, S. Tu, S. Meng, T. Zhang, T. Luo, T. Hao, T. Tong, W. Li, W. Jia, X. Liu, X. Zhang, X. Lyu, X. Fan, X. Huang, Y. Wang, Y. Xue, Y. Wang, Y. Wang, Y. An, Y. Du, Y. Shi, Y. Huang, Y. Niu, Y. Wang, Y. Yue, Y. Li, Y. Zhang, Y. Wang, Y. Wang, Y. Zhang, Z. Xue, Z. Hou, Z. Du, Z. Wang, P. Zhang, D. Liu, B. Xu, J. Li, M. Huang, Y. Dong, and J. Tang. Glm-4.5v and glm-4.1v-thinking: Towards versatile multimodal reasoning with scalable reinforcement learning, 2025.

[38] Z. A. Team. Glm-image: Auto-regressive for dense-knowledge and high-fidelity image generation. Technical blog, Zhipu AI (Z.ai), January 2026. First open-source industrial-grade discrete autoregressive image generation model with hybrid AR+Diffusion architecture.

[39] M. Tschannen, A. Gritsenko, X. Wang, M. F. Naeem, I. Alabdulmohsin, N. Parthasarathy, T. Evans, L. Beyer, Y. Xia, B. Mustafa, et al. Siglip 2: Multilingual vision-language encoders with improved semantic understanding, localization, and dense features. arXiv preprint arXiv:2502.14786, 2025.

[40] Z. Wang, M. Xia, L. He, H. Chen, Y. Liu, R. Zhu, K. Liang, X. Wu, H. Liu, S. Malladi, et al. Charxiv: Charting gaps in realistic chart understanding in multimodal llms. Advances in Neural Information Processing Systems, 37:113569–113697, 2024.

[41] P. Wu and S. Xie. V*: Guided visual search as a core mechanism in multimodal llms, 2023.

[42] Y. Xiao, E. Sun, T. Liu, and W. Wang. Logicvista: Multimodal llm logical reasoning benchmark in visual contexts. arXiv preprint arXiv:2407.04973, 2024.

16

<!-- page 17 -->

[43] T. Xie, D. Zhang, J. Chen, X. Li, S. Zhao, R. Cao, T. J. Hua, Z. Cheng, D. Shin, F. Lei, et al. Osworld: Benchmarking multimodal agents for open-ended tasks in real computer environments. Advances in Neural Information Processing Systems, 37:52040–52094, 2024.

[44] T. Xie, D. Zhang, J. Chen, X. Li, S. Zhao, R. Cao, J. H. Toh, Z. Cheng, D. Shin, F. Lei, et al. Osworld: Benchmarking multimodal agents for open-ended tasks in real computer environments. Advances in Neural Information Processing Systems, 37:52040–52094, 2025.

[45] Z. Yang, W. Hong, M. Xu, X. Fan, W. Wang, J. Cheng, X. Gu, and J. Tang. Ui2code n: Ui-to-code generation as interactive visual optimization. arXiv preprint arXiv:2511.08195, 2025.

[46] B. Ye, R. Li, Q. Yang, Y. Liu, L. Yao, H. Lv, Z. Xie, C. An, L. Li, L. Kong, et al. Claw-eval: Toward trustworthy evaluation of autonomous agents. arXiv preprint arXiv:2604.06132, 2026.

[47] X. Yue, Y. Ni, K. Zhang, T. Zheng, R. Liu, G. Zhang, S. Stevens, D. Jiang, W. Ren, Y. Sun, et al. Mmmu: A massive multi-discipline multimodal understanding and reasoning benchmark for expert agi. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pages 9556–9567, 2024.

[48] X. Yue, T. Zheng, Y. Ni, Y. Wang, K. Zhang, S. Tong, Y. Sun, B. Yu, G. Zhang, H. Sun, et al. Mmmu-pro: A more robust multi-discipline multimodal understanding benchmark. In Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 15134–15186, 2025.

[49] A. Zeng, X. Lv, Z. Hou, Z. Du, Q. Zheng, B. Chen, D. Yin, C. Ge, C. Huang, C. Xie, et al. Glm-5: from vibe coding to agentic engineering. arXiv preprint arXiv:2602.15763, 2026.

[50] Zhipu AI Team. Autoclaw. https://autoglm.zhipuai.cn/autoclaw/, 2026. AI Assistant Tool Supporting Windows & macOS, Model Hot-Swapping, 50+ Skills, AutoGLM Browser Automation, accessed 2026-04-15.

17

<!-- page 18 -->

## A Demo Cases

We demonstrate the capabilities and advantages of GLM-5V-Turbo through typical qualitative examples from various scenarios.

### A.1 In Combination with Agent Systems and Skills

*[figure]*

Figure 6: A case showing the application of GLM-5V-Turbo to stock analysis, with OpenClaw and the official skill glmv-stock-analyst \( ^{3} \) . It gathers relevant information from multiple sources and produces a professional analysis report, including technical analysis, fundamental analysis, analyst sentiment and action plan. Query: Analyze NVIDIA's stock and give a English report.

\( ^{3} \) URL: https://clawhub.ai/zai-org/glmv-stock-analyst

18

<!-- page 19 -->

*[figure]*

Figure 7: A case showing the application of GLM-5V-Turbo to URL-based GUI exploration, asset collection, and webpage recreation, with Claude Code and the official skill glmv-web-replication \( ^{4} \) .

Query: Given a target website URL: https://webflow-path-three.webflow.io/, please explore it via GUI, collect the necessary assets, and recreate the webpage in HTML code with high visual fidelity and functional completeness.

*[figure]*

Figure 8: A case showing the application of GLM-5V-Turbo to PRD-driven website generation, with Claude Code and the official skill glmv-prd-to-app \( ^{5} \) . Given a product requirements document and the project contents under the act folder, the model uses the PRD skill to design and implement a website in the working directory ./act_workspace. Query: Based on my PRD document, please use your PRD skills to build a website for the project in the act folder. The working directory is ./act_workspace.

\( ^{4} \) URL: https://clawhub.ai/zai-org/glmv-web-replication

\( ^{5} \) URL: https://clawhub.ai/zai-org/glmv-prd-to-app

19

<!-- page 20 -->

### A.2 Multimodal Coding

*[figure]*

Prompt: You are a master of frontend recreation and web design. Please complete the following design tasks and implement everything in HTML code. 1. Recreate all pages of such a shopping website, using valid image URLs. 2. Create a welcome page and then transition into the shopping interface. 3. On the "About Brand" page, use parallax scrolling to tell the brand story, allowing text to appear rhythmically as the image background moves. 4. Design a color scheme that preserves a premium aesthetic in dark mode and resolves the issue of product images blending into dark backgrounds. 5. Design a one-page checkout interface to reduce user drop-off, including dynamic shipping calculation and address autocomplete. In addition to the above, also implement all button functionalities, such as Home, Products, About Brand, and Checkout.

*[figure]*

Figure 9: A case showing the application of GLM-5V-Turbo to full-stack e-commerce website design and implementation, using our official website z.ai \( ^{6} \) . Given a high-level product design request, the model generates a complete HTML-based shopping website with multiple functional pages, including a welcome page, shopping interface, brand-story page with parallax scrolling, dark-mode visual design, and a one-page checkout interface with dynamic shipping calculation and address suggestion. The model also completes interactive button behaviors across key pages such as Home, Products, About Brand, and Checkout. Query: You are a master of frontend recreation and web design. Please complete the following design tasks and implement everything in HTML code. 1. Recreate all pages of such a shopping website, using valid image URLs. 2. Create a welcome page and then transition into the shopping interface. 3. On the “About Brand” page, use parallax scrolling to tell the brand story, allowing text to appear rhythmically as the image background moves. 4. Design a color scheme that preserves a premium aesthetic in dark mode and resolves the issue of product images blending into dark backgrounds. 5. Design a one-page checkout interface to reduce user drop-off, including dynamic shipping calculation and address autocomplete. In addition to the above, also implement all button functionalities, such as Home, Products, About Brand, and Checkout.

\( ^{6} \) URL: https://chat.z.ai/

20

<!-- page 21 -->

*[figure]*

Prompt: Please recreate the mobile app interface based on the provided image, and additionally mock several possible follow-up pages or user interactions that fit the same product design and functionality.

*[figure]*

Figure 10: A case showing the application of GLM-5V-Turbo to UI recreation and mock interface generation, using our official website z.ai. Given a reference image of a mobile mood-tracking application, the model reconstructs the interface in executable web code and further mocks additional plausible pages and interactions in a consistent visual style. Query: Please recreate the mobile app interface based on the provided image, and additionally mock several possible follow-up pages or user interactions that fit the same product design and functionality.

*[figure]*

Prompt: Please recreate the webpage based on the reference screenshot, output the result in HTML, and retrieve the image assets appearing in the screenshot.

*[figure]*

Figure 11: A case showing the application of GLM-5V-Turbo to agentic UI recreation, using our official website z.ai. Given a reference screenshot of a webpage, the model reconstructs the page in HTML while automatically retrieving the image assets appearing in the screenshot. This example highlights the agentic framework's ability to jointly perform visual understanding, asset collection, and faithful UI recreation. Query: Please recreate the webpage based on the reference screenshot, output the result in HTML, and retrieve the image assets appearing in the screenshot.

21

<!-- page 22 -->

*[figure]*

Figure 12: A case showing the application of GLM-5V-Turbo to automatic website generation for research paper, using our official website z.ai. Given the paper GLM-5: from Vibe Coding to Agentic Engineering, the model generates an English website that presents the paper's motivation, core ideas, system design, and key results in a clear and visually organized format with interleaved text and figures. Query: I am preparing an introduction website for the paper GLM-5: from Vibe Coding to Agentic Engineering. Please generate an English website that clearly presents the paper's background, methodology, main findings, and contributions.

22

<!-- page 23 -->

*[figure]*

Figure 13: A case showing the application of GLM-5V-Turbo to automatic PowerPoint generation from a research paper, using our official website z.ai. Given the paper Attention Is All You Need, the model generates an English slide deck that summarizes the main motivation, method, architecture, and key findings in a presentation-ready format with interleaved text and figures. Query: I am preparing a presentation based on the paper Attention Is All You Need. Please generate an English PowerPoint that summarizes the paper clearly and professionally.

23

<!-- page 24 -->

### A.3 Multimodal Deep Research

*[figure]*

Figure 14: A case showing the application of GLM-5V-Turbo to image materials collection, using our official website z.ai. Note that the original source for each of the chosen images is cited. Query: I am preparing a feature report on Apple Wearables. Please help me collect image assets, ensuring the sources are authoritative and the image quality is high. Requirements: 1. Output in English. 2. Organize into an illustrated report with interleaved images and text.

24

<!-- page 25 -->

### A.4 Document-Based Writing

*[figure]*

(a)

*[figure]*

(b)

Figure 15: A case showing the ability of document-based writing. (a) A travel guide of Beijing (in Chinese, 103 pages in total). (b) The commentary introducing must-visit attractions in Beijing. Query: Read this travel guide, summarize ten must-visit attractions for foreigners and write the commentary.

25

<!-- page 26 -->

### A.5 OCR and Document Parsing

*[figure]*

(a)

*[figure]*

(b)

Figure 16: A case showing the ability of multilingual OCR. (a) Original image. (b) Recognized words/phrases and corresponding language type. Prompt: Recognize each word in the image and identify the language.

*[figure]*

(a)

*[figure]*

(b)

Figure 17: A case showing the ability of accurate document transcription. (a) Original page from a physics textbook. (b) Transcribed result, including text, table and figures, in Markdown format.

26

<!-- page 27 -->

### A.6 Visual Search and Reasoning

*[figure]*

Figure 18: A case showing the ability of utilizing the information from the image and multimodal searching tools to solve a complex question, using our official website z.ai. Query: There is a novel written by a British author whose title contains a location where the animal shown in the image is distributed. This author has also written other novels featuring animal names—among them, one whose animal is relatively small in size and not part of the Chinese zodiac, how many people appear on the poster displayed on the Douban page for the film adaptation of this work?

*[figure]*

Figure 19: A case showing the ability of locating the input image and search local hotel prices on specific dates provided by the user, using our official website z.ai. Query: I would like to book a hotel room from 5.1-5.5 in this town, give me a list of 3 hotels in order of total price, with total price, reviews, experience suggestion.

27

<!-- page 28 -->

### A.7 Visual Recognition and Grounding

*[figure]*

*[figure]*

*[figure]*

Figure 20: A case showing the ability of video objects tracking. Prompt: Output the per-second object tracking results for all people playing basketball in the video. Use valid JSON format, where each key is the second number, and the value is a list of detected objects in that frame.

*[figure]*

*[figure]*

*[figure]*

Figure 21: A case showing the ability of video objects tracking. Prompt: Based on the description of the objects appearing in the video "person committing crime", please track the objects corresponding to this description at every second (tracks per second) of the given video, and provide the bounding box and a globally consistent label for each object.

*[figure]*

(a)

*[figure]*

(b)

Figure 22: A case demonstrating recognition capability based on grounding and search tools. (a) Person recognition. Prompt: Box out all people and their names. (b) Prompt: This is a screenshot of a GPU circuit board. Search this image, frame each component along with its name, and write a parameter comparison report comparing it with the H100.

28

<!-- page 29 -->

2022—2023 学年度上学期期末教学质量测查六年级科学试卷

|  考生注意:  |   |   |   |   |   |   |   |   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  1. 考试时间:60分钟。  |   |   |   |   |   |   |   |   |
|  2. 去年6月4日大题,总分100分。  |   |   |   |   |   |   |   |   |
|  题号 | 一 | 二 | 三 | 四 | 五 | 六 | 总分 | 部分人  |
|  部分 |  |  |  |  |  |  |  |   |

*[figure]*

1. 放大镜的强片又是1.2.1.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.2.

2. 同一个微小的物体在两眼、放大镜和显微镜下观察到的图像大小及视野是 \( \boxed{1} \) 的。

3. 细胞是生物体最基本的  \( \boxed{1} \)  等位
4. 在水中生活着形态各异的微小  \( \boxed{2} \)  的它们具有  \( \boxed{1} \)  的特征。[{"box_2d": [203, 322, 463, 361], "label": "text", "caption": "5. 通过制作地球模型，我们了解了地球的内部圈层结构，知道地球内部层分为 \\( \\boxed{1} \\) 、 \\( \\boxed{2} \\) 、地幔和 \\( \\boxed{3} \\) 、地球外部包围着厚厚的 \\( \\boxed{4} \\) 、 \\( \\boxed{5} \\) 、 \\( \\boxed{6} \\) 、 \\( \\boxed{7} \\) 、 \\( \\boxed{8} \\) 、 \\( \\boxed{9} \\) 、 \\( \\boxed{10} \\) 、 \\( \\boxed{11} \\) 、 \\( \\boxed{12} \\) 、 \\( \\boxed{13} \\) 、 \\( \\boxed{14} \\) 、 \\( \\boxed{15} \\) 、 \\( \\boxed{16} \\) 、 \\( \\boxed{17} \\) 、 \\( \\boxed{18} \\) 、 \\( \\boxed{19} \\) 、 \\( \\boxed{20} \\) 、 \\( \\boxed{21} \\) 、 \\( \\boxed{22} \\) 、 \\( \\boxed{23} \\) 、 \\( \\boxed{24} \\) 、 \\( \\boxed{25} \\) 、 \\( \\boxed{26} \\) 、 \\( \\boxed{27} \\) 、 \\( \\boxed{28} \\) 、 \\( \\boxed{29} \\) 、 \\( \\boxed{30} \\) 、 \\( \\boxed{31} \\) 、 \\( \\boxed{32} \\) 、 \\( \\boxed{33} \\) 、 \\( \\boxed{34} \\) 、 \\( \\boxed{35} \\) 、 \\( \\boxed{36} \\) 、 \\( \\boxed{37} \\) 、 \\( \\boxed{38} \\) 、 \\( \\boxed{39} \\) 、 \\( \\boxed{40} \\) 、 \\( \\boxed{41} \\) 、 \\( \\boxed{42} \\) 、 \\( \\boxed{43} \\) 、 \\( \\boxed{44} \\) 、 \\( \\boxed{45} \\) 、 \\( \\boxed{46} \\) 、 \\( \\boxed{47} \\) 、 \\( \\boxed{48} \\) 、 \\( \\boxed{49} \\) 、 \\( \\boxed{50} \\) 、 \\( \\boxed{51} \\) 、 \\( \\boxed{52} \\) 、 \\( \\boxed{53} \\) 、 \\( \\boxed{54} \\) 、 \\( \\boxed{55} \\) 、 \\( \\boxed{56} \\) 、 \\( \\boxed{57} \\) 、 \\( \\boxed{58} \\) 、 \\( \\boxed{59} \\) 、 \\( \\boxed{60} \\) 、 \\( \\boxed{61} \\) 、 \\( \\boxed{62} \\) 、 \\( \\boxed{63} \\) 、 \\( \\boxed{64} \\) 、 \\( \\boxed{65} \\) 、 \\( \\boxed{66} \\) 、 \\( \\boxed{67} \\) 、 \\( \\boxed{68} \\) 、 \\( \\boxed{69} \\) 、 \\( \\boxed{70} \\) 、 \\( \\boxed{71} \\) 、 \\( \\boxed{72} \\) 、 \\( \\boxed{73} \\) 、 \\( \\boxed{74} \\) 、 \\( \\boxed{75} \\) 、 \\( \\boxed{76} \\) 、 \\( \\boxed{77} \\) 、 \\( \\boxed{78} \\) 、 \\( \\boxed{79} \\) 、 \\( \\boxed{80} \\) 、 \\( \\boxed{81} \\) 、 \\( \\boxed{82} \\) 、 \\( \\boxed{83} \\) 、 \\( \\boxed{84} \\) 、 \\( \\boxed{85} \\) 、 \\( \\boxed{86} \\) 、 \\( \\boxed{87} \\) 、 \\( \\boxed{88} \\) 、 \\( \\boxed{89} \\) 、 \\( \\boxed{90} \\) 、 \\( \\boxed{91} \\) 、 \\( \\boxed{92} \\) 、 \\( \\boxed{93} \\) 、 \\( \\boxed{94} \\) 、 \\( \\boxed{95} \\) 、 \\( \\boxed{96} \\) 、 \\( \\boxed{97} \\) 、 \\( \\boxed{98} \\) 、 \\( \\boxed{99} \\) 、 \\( 100\\%\\text{ (1)} = 100\\%\\text{ (2)} = 100\\%\\text{ (3)} = 100\\%\\text{ (4)} = 100\\%\\text{ (5)} = 100\\%\\text{ (6)} = 100\\%\\text{ (7)} = 100\\%\\text{ (8)} = 100\\%\\text{ (9)} = 100\\%\\text{ (10)} = 100\\%\\text{ (11)} = 100\\%\\text{ (12)} = 100\\%\\text{ (13)} = 100\\%\\text{ (14)} = 100\\%\\text{ (15)} = 100\\%\\text{ (16)} = 100\\%\\text{ (17)} = 100\\%\\text{ (18)} = 100\\%\\text{ (19)} = 100\\%\\text{ (20)} = 100\\%\\text{ (21)} = 100\\%\\text{ (22)} = 100\\%\\text{ (23)} = 100\\%\\text{ (24)} = 100\\%\\text{ (25)} = 100\\%\\text{ (26)} = 100\\%\\text{ (27)} = 100\\%\\text{ (28)} = 100\\%\\text{ (29)} = 100\\%\\text{ (30)} = 100\\%\\text{ (31)} = 100\\%\\text{ (32)} = 100\\%\\text{ (33)} = 100\\%\\text{ (34)} = 100\\%\\text{ (35)} = 100\\%\\text{ (36)} = 100\\%\\text{ (37)} = 100\\%\\text{ (38)} = 100\\%\\text{ (39)} = 100\\%\\text{ (40)} = 100\\%\\text{ (41)} = 100\\%\\text{ (42)} = 100\\%\\text{ (43)} = 100\\%\\text{ (44)} = 100\\%\\text{ (45)} = 100\\%\\text{ (46)} = 100\\%\\text{ (47)} = 100\\%\\text{ (48)} = 100\\%\\text{ (49)} = 100\\%\\text{ (50)} = 100\\%\\text{ (51)} = 100\\%\\text{ (52)} = 100\\%\\text{ (53)} = 100\\%\\text{ (54)} = 100\\%\\text{ (55)} = 100\\%\\text{ (56)} = 100\\%\\text{ (57)} = 100\\%\\text{ (58)} = 100\\%\\text{ (59)} = 100\\%\\text{ (60)} = 100\\%\\text{ (61)} = 100\\%\\text{ (62)} = 100\\%\\text{ (63)} = 100\\%\\text{ (64)} = 100\\%\\text{ (65)} = 100\\%\\text{ (66)} = 100\\%\\text{ (67)} = 100\\%\\text{ (68)} = 100\\%\\text{ (69)} = 100\\%\\text{ (70)} = 100\\%\\text{ (71)} = 100\\%\\text{ (72)} = 100\\%\\text{ (73)} = 100\\%\\text{ (74)} = 100\\%\\text{ (75)} = 100\\%\\text{ (76)} = 100\\%\\text{ (77)} = 100\\%\\text{ (78)} = 100\\%\\text{ (79)} = 100\\%\\text{ (80)} = 100\\%\\text{ (81)} = 100\\%\\text{ (82)} = 100\\%\\text{ (83)} = 100\\%\\text{ (84)} = 100\\%\\text{ (85)} = 100\\%\\text{ (86)} = 100\\%\\text{ (87)} = 100\\%\\text{ (88)} = 100\\%\\text{ (89)} = 100\\%\\text{ (90)} = 100\\%\\text{ (91)} = 100\\%\\text{ (92)} = 100\\%\\text{ (93)} = 100\\%\\text{ (94)} = 100\\%\\text{ (95)} = 100\\%\\text{ (96)} = 100\\%\\text{ (97)} = 100\\%\\text{ (98)} = 100\\%\\text{ (99)} = 100\\%\\text{ (100)} = 100\\%\\text{ (101)} = 100\\%\\text{ (102)} = 100\\%\\text{ (103)} = 100\\%\\text{ (104)} = 100\\%\\text{ (105)} = 100\\%\\text{ (106)} = 100\\%\\text{ (107)} = 100\\%\\text{ (108)} = 100\\%\\text{ (109)} = 100\\%\\text{ (110)} = 100\\%\\text{ (111)} = 100\\%\\text{ (112)} = 100\\%\\text{ (113)} = 100\\%\\text{ (114)} = 100\\%\\text{ (115)} = 100\\%\\text{ (116)} = 100\\%\\text{ (117)} = 100\\%\\text{ (118)} = 100\\%\\text{ (119)} = 100\\%\\text{ (120)} = 100\\%\\text{ (121)} = 100\\%\\text{ (122)} = 100\\%\\text{ (123)} = 100\\%\\text{ (124)} = 100\\%\\text{ (125)} = 100\\%\\text{ (126)} = 100\\%\\text{ (127)} = 100\\%\\text{ (128)} = 100\\%\\text{ (129)} = 100\\%\\text{ (130)} = 100\\%\\text{ (131)} = 100\\%\\text{ (132)} = 100\\%\\text{ (133)} = 100\\%\\text{ (134)} = 100\\%\\text{ (135)} = 100\\%\\text{ (136)} = 100\\%\\text{ (137)} = 100\\%\\text{ (138)} = 100\\%\\text{ (139)} = 100\\%\\text{ (140)} = 100\\%\\text{ (141)} = 100\\%\\text{ (142)} = 100\\%\\text{ (143)} = 100\\%\\text{ (144)} = 100\\%\\text{ (145)} = 100\\%\\text{ (146)} = 100\\%\\text{ (147)} = 100\\%\\text{ (148)} = 100\\%\\text{ (149)} = 100\\%\\text{ (150)} = 100\\%\\text{ (151)} = 100\\%\\text{ (152)} = 100\\%\\text{ (153)} = 100\\%\\text{ (154)} = 100\\%\\text{ (155)} = 100\\%\\text{ (156)} = 100\\%\\text{ (157)} = 100\\%\\text{ (158)} = 100\\%\\text{ (159)} = 100\\%\\text{ (160)} = 100\\%\\text{ (161)} = 100\\%\\text{ (162)} = 100\\%\\text{ (163)} = 100\\%\\text{ (164)} = 100\\%\\text{ (165)} = 100\\%\\text{ (166)} = 100\\%\\text{ (167)} = 100\\%\\text{ (168)} = 100\\%\\text{ (169)} = 100\\%\\text{ (170)} = 100\\%\\text{ (171)} = 100\\%\\text{ (172)} = 100\\%\\text{ (173)} = 100\\%\\text{ (174)} = 100\\%\\text{ (175)} = 100\\%\\text{ (176)} = 100\\%\\text{ (177)} = 100\\%\\text{ (178)} = 100\\%\\text{ (179)} = 100\\%\\text{ (180)} = 100\\%\\text{ (181)} = 100\\%\\text{ (182)} = 100\\%\\text{ (183)} = 100\\%\\text{ (184)} = 100\\%\\text{ (185)} = 100\\%\\text{ (186)} = 100\\%\\text{ (187)} = 100\\%\\text{ (188)} = 100\\%\\text{ (189)} = 100\\%\\text{ (190)} = 100\\%\\text{ (191)} = 100\\%\\text{ (192)} = 100\\%\\text{ (193)} = 100\\%\\text{ (194)} = 100\\%\\text{ (195)} = 100\\%\\text{ (196)} = 100\\%\\text{ (197)} = 100\\%\\text{ (198)} = 100\\%\\text{ (199)} = 100\\%\\text{ (200)} = 100\\%\\text{ (201)} = 100\\%\\text{ (202)} = 100\\%\\text{ (203)} = 100\\%\\text{ (204)} = 100\\%\\text{ (205)} = 100\\%\\text{ (206)} = 100\\%\\text{ (207)} = 100\\%\\text{ (208)} = 100\\%\\text{ (209)} = 100\\%\\text{ (210)} = 100\\%\\text{ (211)} = 100\\%\\text{ (212)} = 100\\%\\text{ (213)} = 100\\%\\text{ (214)} = 100\\%\\text{ (215)} = 100\\%\\text{ (216)} = 100\\%\\text{ (217)} = 100\\%\\text{ (218)} = 100\\%\\text{ (219)} = 100\\%\\text{ (220)} = 100\\%\\text{ (221)} = 100\\%\\text{ (222)} = 100\\%\\text{ (223)} = 100\\%\\text{ (224)} = 100\\%\\text{ (225)} = 100\\%\\text{ (226)} = 100\\%\\text{ (227)} = 100\\%\\text{ (228)} = 100\\%\\text{ (229)} = 100\\%\\text{ (230)} = 100\\%\\text{ (231)} = 100\\%\\text{ (232)} = 100\\%\\text{ (233)} = 100\\%\\text{ (234)} = 100\\%\\text{ (235)} = 100\\%\\text{ (236)} = 100\\%\\text{ (237)} = 100\\%\\text{ (238)} = 100\\%\\text{ (239)} = 100\\%\\text{ (240)} = 100\\%\\text{ (241)} = 100\\%\\text{ (242)} = 100\\%\\text{ (243)} = 100\\%\\text{ (244)} = 100\\%\\text{ (245)} = 100\\%\\text{ (246)} = 100\\%\\text{ (247)} = 100\\%\\text{ (248)} = 100\\%\\text{ (249)} = 100\\%\\text{ (250)} = 100\\%\\text{ (251)} = 100\\%\\text{ (252)} = 100\\%\\text{ (253)} = 100\\%\\text{ (254)} = 100\\%\\text{ (255)} = 100\\%\\text{ (256)} = 100\\%\\text{ (257)} = 100\\%\\text{ (258)} = 100\\%\\text{ (259)} = 100\\%\\text{ (260)} = 100\\%\\text{ (261)} = 100\\%\\text{ (262)} = 100\\%\\text{ (263)} = 100\\%\\text{ (264)} = 100\\%\\text{ (265)} = 100\\%\\text{ (266)} = 100\\%\\text{ (267)} = 100\\%\\text{ (268)} = 100\\%\\text{ (269)} = 100\\%\\text{ (270)} = 100\\%\\text{ (271)} = 100\\%\\text{ (272)} = 100\\%\\text{ (273)} = 100\\%\\text{ (274)} = 100\\%\\text{ (275)} = 100\\%\\text{ (276)} = 100\\%\\text{ (277)} = 100\\%\\text{ (278)} = 100\\%\\text{ (279)} = 100\\%\\text{ (280)} = 100\\%\\text{ (281)} = 100\\%\\text{ (282)} = 100\\%\\text{ (283)} = 100\\%\\text{ (284)} = 100\\%\\text{ (285)} = 100\\%\\text{ (286)} = 100\\%\\text{ (287)} = 100\\%\\text{ (288)} = 100\\%\\text{ (289)} = 100\\%\\text{ (290)} = 100\\%\\text{ (291)} = 100\\%\\text{ (292)} = 100\\%\\text{ (293)} = 100\\%\\text{ (294)} = 100\\%\\text{ (295)} = 100\\%\\text{ (296)} = 100\\%\\text{ (297)} = 100\\%\\text{ (298)} = 100\\%\\text{ (299)} = 100\\%\\text{ (300)} = 100\\%\\text{ (301)} = 100\\%\\text{ (302)} = 100\\%\\text{ (303)} = 100\\%\\text{ (304)} = 100\\%\\text{ (305)} = 100\\%\\text{ (306)} = 100\\%\\text{ (307)} = 100\\%\\text{ (308)} = 100\\%\\text{ (309)} = 100\\%\\text{ (310)} = 100\\%\\text{ (311)} = 100\\%\\text{ (312)} = 100\\%\\text{ (313)} = 100\\%\\text{ (314)} = 100\\%\\text{ (315)} = 100\\%\\text{ (316)} = 100\\%\\text{ (317)} = 100\\%\\text{ (318)} = 100\\%\\text{ (319)} = 100\\%\\text{ (320)} = 100\\%\\text{ (321)} = 100\\%\\text{ (322)} = 100\\%\\text{ (323)} = 100\\%\\text{ (324)} = 100\\%\\text{ (325)} = 100\\%\\text{ (326)} = 100\\%\\text{ (327)} = 100\\%\\text{ (328)} = 100\\%\\text{ (329)} = 100\\%\\text{ (330)} = 100\\%\\text{ (331)} = 100\\%\\text{ (332)} = 100\\%\\text{ (333)} = 100\\%\\text{ (334)} = 100\\%\\text{ (335)} = 100\\%\\text{ (336)} = 100\\%\\text{ (337)} = 100\\%\\text{ (338)} = 100\\%\\text{ (339)} = 100\\%\\text{ (340)} = 100\\%\\text{ (341)} = 100\\%\\text{ (342)} = 100\\%\\text{ (343)} = 100\\%\\text{ (344)} = 100\\%\\text{ (345)} = 100\\%\\text{ (346)} = 100\\%\\text{ (347)} = 100\\%\\text{ (348)} = 100\\%\\text{ (349)} = 100\\%\\text{ (350)} = 100\\%\\text{ (351)} = 100\\%\\text{ (352)} = 100\\%\\text{ (353)} = 100\\%\\text{ (354)} = 100\\%\\text{ (355)} = 100\\%\\text{ (356)} = 100\\%\\text{ (357)} = 100\\%\\text{ (358)} = 100\\%\\text{ (359)} = 100\\%\\text{ (360)} = 100\\%\\text{ (361)} = 100\\%\\text{ (362)} = 100\\%\\text{ (363)} = 100\\%\\text{ (364)} = 100\\%\\text{ (365)} = 100\\%\\text{ (366)} = 100\\%\\text{ (367)} = 100\\%\\text{ (368)} = 100\\%\\text{ (369)} = 100\\%\\text{ (370)} = 100\\%\\text{ (371)} = 100\\%\\text{ (372)} = 100\\%\\text{ (373)} = 100\\%\\text{ (374)} = 100\\%\\text{ (375)} = 100\\%\\text{ (376)} = 100\\%\\text{ (377)} = 100\\%\\text{ (378)} = 100\\%\\text{ (379)} = 100\\%\\text{ (380)} = 100\\%\\text{ (381)} = 100\\%\\text{ (382)} = 100\\%\\text{ (383)} = 100\\%\\text{ (384)} = 100\\%\\text{ (385)} = 100\\%\\text{ (386)} = 100\\%\\text{ (387)} = 100\\%\\text{ (388)} = 100\\%\\text{ (389)} = 100\\%\\text{ (390)} = 100\\%\\text{ (391)} = 100\\%\\text{ (392)} = 100\\%\\text{ (393)} = 100\\%\\text{ (394)} = 100\\%\\text{ (395)} = 100\\%\\text{ (396)} = 100\\%\\text{ (397)} = 100\\%\\text{ (398)} = 100\\%\\text{ (399)} = 100\\%\\text{ (400)} = 100\\%\\text{ (401)} = 100\\%\\text{ (402)} = 100\\%\\text{ (403)} = 100\\%\\text{ (404)} = 100\\%\\text{ (405)} = 100\\%\\text{ (406)} = 100\\%\\text{ (407)} = 100\\%\\text{ (408)} = 100\\%\\text{ (409)} = 100\\%\\text{ (410)} = 100\\%\\text{ (411)} = 100\\%\\text{ (412)} = 100\\%\\text{ (413)} = 100\\%\\text{ (414)} = 100\\%\\text{ (415)} = 100\\%\\text{ (416)} = 100\\%\\text{ (417)} = 100\\%\\text{ (418)} = 100\\%\\text{ (419)} = 100\\%\\text{ (420)} = 100\\%\\text{ (421)} = 100\\%\\text{ (422)} = 100\\%\\text{ (423)} = 100\\%\\text{ (424)} = 100\\%\\text{ (425)} = 100\\%\\text{ (426)} = 100\\%\\text{ (427)} = 100\\%\\text{ (428)} = 100\\%\\text{ (429)} = 100\\%\\text{ (430)} = 100\\%\\text{ (431)} = 100\\%\\text{ (432)} = 100\\%\\text{ (433)} = 100\\%\\text{ (434)} = 100\\%\\text{ (435)} = 100\\%\\text{ (436)} = 100\\%\\text{ (437)} = 100\\%\\text{ (438)} = 100\\%\\text{ (439)} = 100\\%\\text{ (440)} = 100\\%\\text{ (441)} = 100\\%\\text{ (442)} = 100\\%\\text{ (443)} = 100\\%\\text{ (444)} = 100\\%\\text{ (445)} = 100\\%\\text{ (446)} = 100\\%\\text{ (447)} = 100\\%\\text{ (448)} = 100\\%\\text{ (449)} = 100\\%\\text{ (450)} = 100\\%\\text{ (451)} = 100\\%\\text{ (452)} = 100\\%\\text{ (453)} = 100\\%\\text{ (454)} = 100\\%\\text{ (455)} = 100\\%\\text{ (456)} = 100\\%\\text{ (457)} = 100\\%\\text{ (458)} = 100\\%\\text{ (459)} = 100\\%\\text{ (460)} = 100\\%\\text{ (461)} = 100\\%\\text{ (462)} = 100\\%\\text{ (463)} = 100\\%\\text{ (464)} = 100\\%\\text{ (465)} = 100\\%\\text{ (466)} = 100\\%\\text{ (467)} = 100\\%\\text{ (468)} = 100\\%\\text{ (469)} = 100\\%\\text{ (470)} = 100\\%\\text{ (471)} = 100\\%\\text{ (472)} = 100\\%\\text{ (473)} = 100\\%\\text{ (474)} = 100\\%\\text{ (475)} = 100\\%\\text{ (476)} = 100\\%\\text{ (477)} = 100\\%\\text{ (478)} = 100\\%\\text{ (479)} = 100\\%\\text{ (480)} = 100\\%\\text{ (481)} = 100\\%\\text{ (482)} = 100\\%\\text{ (483)} = 100\\%\\text{ (484)} = 100\\%\\text{ (485)} = 100\\%\\text{ (486)} = 100\\%\\text{ (487)} = 100\\%\\text{ (488)} = 100\\%\\text{ (489)} = 100\\%\\text{ (490)} = 100\\%\\text{ (491)} = 100\\%\\text{ (492)} = 100\\%\\text{ (493)} = 100\\%\\text{ (494)} = 100\\%\\text{ (495)} = 100\\%\\text{ (496)} = 100\\%\\text{ (497)} = 100\\%\\text{ (498)} = 100\\%\\text{ (499)} = 100\\%\\text{ (500)} = 100\\%\\text{ (501)} = 100\\%\\text{ (502)} = 100\\%\\text{ (503)} = 100\\%\\text{ (504)} = 100\\%\\text{ (505)} = 100\\%\\text{ (506)} = 100\\%\\text{ (507)} = 100\\%\\text{ (508)} = 100\\%\\text{ (509)} = 100\\%\\text{ (510)} = 100\\%\\text{ (511)} = 100\\%\\text{ (512)} = 100\\%\\text{ (513)} = 100\\%\\text{ (514)} = 100\\%\\text{ (515)} = 100\\%\\text{ (516)} = 100\\%\\text{ (517)} = 100\\%\\text{ (518)} = 100\\%\\text{ (519)} = 100\\%\\text{ (520)} = 100\\%\\text{ (521)} = 100\\%\\text{ (522)} = 100\\%\\text{ (523)} = 100\\%\\text{ (524)} = 100\\%\\text{ (525)} = 100\\%\\text{ (526)} = 100\\%\\text{ (527)} = 100\\%\\text{ (528)} = 100\\%\\text{ (529)} = 100\\%\\text{ (530)} = 100\\%\\text{ (531)} = 100\\%\\text{ (532)} = 100\\%\\text{ (533)} = 100\\%\\text{ (534)} = 100\\%\\text{ (535)} = 100\\%\\text{ (536)} = 100\\%\\text{ (537)} = 100\\%\\text{ (538)} = 100\\%\\text{ (539)} = 100\\%\\text{ (540)} = 100\\%\\text{ (541)} = 100\\%\\text{ (542)} = 100\\%\\text{ (543)} = 100\\%\\text{ (544)} = 100\\%\\text{ (545)} = 100\\%\\text{ (546)} = 100\\%\\text{ (547)} = 100\\%\\text{ (548)} = 100\\%\\text{ (549)} = 100\\%\\text{ (550)} = 100\\%\\text{ (551)} = 100\\%\\text{ (552)} = 100\\%\\text{ (553)} = 100\\%\\text{ (554)} = 100\\%\\text{ (555)} = 100\\%\\text{ (556)} = 100\\%\\text{ (557)} = 100\\%\\text{ (558)} = 100\\%\\text{ (559)} = 100\\%\\text{ (560)} = 100\\%\\text{ (561)} = 100\\%\\text{ (562)} = 100\\%\\text{ (563)} = 100\\%\\text{ (564)} = 100\\%\\text{ (565)} = 100\\%\\text{ (566)} = 100\\%\\text{ (567)} = 100\\%\\text{ (568)} = 100\\%\\text{ (569)} = 100\\%\\text{ (570)} = 100\\%\\text{ (571)} = 100\\%\\text{ (572)} = 100\\%\\text{ (573)} = 100\\%\\text{ (574)} = 100\\%\\text{ (575)} = 100\\%\\text{ (576)} = 100\\%\\text{ (577)} = 100\\%\\text{ (578)} = 100\\%\\text{ (579)} = 100\\%\\text{ (580)} = 100\\%\\text{ (581)} = 100\\%\\text{ (582)} = 100\\%\\text{ (583)} = 100\\%\\text{ (584)} = 100\\%\\text{ (585)} = 100\\%\\text{ (586)} = 100\\%\\text{ (587)} = 100\\%\\text{ (588)} = 100\\%\\text{ (589)} = 100\\%\\text{ (590)} = 100\\%\\text{ (591)} = 100\\%\\text{ (592)} = 100\\%\\text{ (593)} = 100\\%\\text{ (594)} = 100\\%\\text{ (595)} = 100\\%\\text{ (596)} = 100\\%\\text{ (597)} = 100\\%\\text{ (598)} = 100\\%\\text{ (599)} = 100\\%\\text{ (600)} = 100\\%\\text{ (601)} = 100\\%\\text{ (602)} = 100\\%\\text{ (603)} = 100\\%\\text{ (604)} = 100\\%\\text{ (605)} = 100\\%\\text{ (606)} = 100\\%\\text{ (607)} = 100\\%\\text{ (608)} = 100\\%\\text{ (609)} = 100\\%\\text{ (610)} = 100\\%\\text{ (611)} = 100\\%\\text{ (612)} = 100\\%\\text{ (613)} = 100\\%\\text{ (614)} = 100\\%\\text{ (615)} = 100\\%\\text{ (616)} = 100\\%\\text{ (617)} = 100\\%\\text{ (618)} = 100\\%\\text{ (619)} = 100\\%\\text{ (620)} = 100\\%\\text{ (621)} = 100\\%\\text{ (622)} = 100\\%\\text{ (623)} = 100\\%\\text{ (624)} = 100\\%\\text{ (625)} = 100\\%\\text{ (626)} = 100\\%\\text{ (627)} = 100\\%\\text{ (628)} = 100\\%\\text{ (629)} = 100\\%\\text{ (630)} = 100\\%\\text{ (631)} = 100\\%\\text{ (632)} = 100\\%\\text{ (633)} = 100\\%\\text{ (634)} = 100\\%\\text{ (635)} = 100\\%\\text{ (636)} = 100\\%\\text{ (637)} = 100\\%\\text{ (638)} = 100\\%\\text{ (639)} = 100\\%\\text{ (640)} = 100\\%\\text{ (641)} = 100\\%\\text{ (642)} = 100\\%\\text{ (643)} = 100\\%\\text{ (644)} = 100\\%\\text{ (645)} = 100\\%\\text{ (646)} = 100\\%\\text{ (647)} = 100\\%\\text{ (648)} = 100\\%\\text{ (649)} = 100\\%\\text{ (650)} = 100\\%\\text{ (651)} = 100\\%\\text{ (652)} = 100\\%\\text{ (653)} = 100\\%\\text{ (654)} = 100\\%\\text{ (655)} = 100\\%\\text{ (656)} = 100\\%\\text{ (657)} = 100\\%\\text{ (658)} = 100\\%\\text{ (659)} = 100\\%\\text{ (660)} = 100\\%\\text{ (661)} = 100\\%\\text{ (662)} = 100\\%\\text{ (663)} = 100\\%\\text{ (664)} = 100\\%\\text{ (665)} = 100\\%\\text{ (666)} = 100\\%\\text{ (667)} = 100\\%\\text{ (668)} = 100\\%\\text{ (669)} = 100\\%\\text{ (670)} = 100\\%\\text{ (671)} = 100\\%\\text{ (672)} = 100\\%\\text{ (673)} = 100\\%\\text{ (674)} = 100\\%\\text{ (675)} = 100\\%\\text{ (676)} = 100\\%\\text{ (677)} = 100\\%\\text{ (678)} = 100\\%\\text{ (679)} = 100\\%\\text{ (680)} = 100\\%\\text{ (681)} = 100\\%\\text{ (682)} = 100\\%\\text{ (683)} = 100\\%\\text{ (684)} = 100\\%\\text{ (685)} = 100\\%\\text{ (686)} = 100\\%\\text{ (687)} = 100\\%\\text{ (688)} = 100\\%\\text{ (689)} = 100\\%\\text{ (690)} = 100\\%\\text{ (691)} = 100\\%\\text{ (692)} = 100\\%\\text{ (693)} = 100\\%\\text{ (694)} = 100\\%\\text{ (695)} = 100\\%\\text{ (696)} = 100\\%\\text{ (697)} = 100\\%\\text{ (698)} = 100\\%\\text{ (699)} = 100\\%\\text{ (700)} = 100\\%\\text{ (701)} = 100\\%\\text{ (702)} = 100\\%\\text{ (703)} = 100\\%\\text{ (704)} = 100\\%\\text{ (705)} = 100\\%\\text{ (706)} = 100\\%\\text{ (707)} = 100\\%\\text{ (708)} = 100\\%\\text{ (709)} = 100\\%\\text{ (710)} = 100\\%\\text{ (711)} = 100\\%\\text{ (712)} = 100\\%\\text{ (713)} = 100\\%\\text{ (714)} = 100\\%\\text{ (715)} = 100\\%\\text{ (716)} = 100\\%\\text{ (717)} = 100\\%\\text{ (718)} = 100\\%\\text{ (719)} = 100\\%\\text{ (720)} = 100\\%\\text{ (721)} = 100\\%\\text{ (722)} = 100\\%\\text{ (723)} = 100\\%\\text{ (724)} = 100\\%\\text{ (725)} = 100\\%\\text{ (726)} = 100\\%\\text{ (727)} = 100\\%\\text{ (728)} = 100\\%\\text{ (729)} = 100\\%\\text{ (730)} = 100\\%\\text{ (731)} = 100\\%\\text{ (732)} = 100\\%\\text{ (733)} = 100\\%\\text{ (734)} = 100\\%\\text{ (735)} = 100\\%\\text{ (736)} = 100\\%\\text{ (737)} = 100\\%\\text{ (738)} = 100\\%\\text{ (739)} = 100\\%\\text{ (740)} = 100\\%\\text{ (741)} = 100\\%\\text{ (742)} = 100\\%\\text{ (743)} = 100\\%\\text{ (744)} = 100\\%\\text{ (745)} = 100\\%\\text{ (746)} = 100\\%\\text{ (747)} = 100\\%\\text{ (748)} = 100\\%\\text{ (749)} = 100\\%\\text{ (750)} = 100\\%\\text{ (751)} = 100\\%\\text{ (752)} = 100\\%\\text{ (753)} = 100\\%\\text{ (754)} = 100\\%\\text{ (755)} = 100\\%\\text{ (756)} = 100\\%\\text{ (757)} = 100\\%\\text{ (758)} = 100\\%\\text{ (759)} = 100\\%\\text{ (760)} = 100\\%\\text{ (761)} = 100\\%\\text{ (762)} = 100\\%\\text{ (763)} = 100\\%\\text{ (764)} = 100\\%\\text{ (765)} = 100\\%\\text{ (766)} = 100\\%\\text{ (767)} = 100\\%\\text{ (768)} = 100\\%\\text{ (769)} = 100\\%\\text{ (770)} = 100\\%\\text{ (771)} = 100\\%\\text{ (772)} = 100\\%\\text{ (773)} = 100\\%\\text{ (774)} = 100\\%\\text{ (775)} = 100\\%\\text{ (776)} = 100\\%\\text{ (777)} = 100\\%\\text{ (778)} = 100\\%\\text{ (779)} = 100\\%\\text{ (780)} = 100\\%\\text{ (781)} = 100\\%\\text{ (782)} = 100\\%\\text{ (783)} = 100\\%\\text{ (784)} = 100\\%\\text{ (785)} = 100\\%\\text{ (786)} = 100\\%\\text{ (787)} = 100\\%\\text{ (788)} = 100\\%\\text{ (789)} = 100\\%\\text{ (790)} = 100\\%\\text{ (791)} = 100\\%\\text{ (792)} = 100\\%\\text{ (793)} = 100\\%\\text{ (794)} = 100\\%\\text{ (795)} = 100\\%\\text{ (796)} = 100\\%\\text{ (797)} = 100\\%\\text{ (798)} = 100\\%\\text{ (799)} = 100\\%\\text{ (800)} = 100\\%\\text{ (801)} = 100\\%\\text{ (802)} = 100\\%\\text{ (803)} = 100\\%\\text{ (804)} = 100\\%\\text{ (805)} = 100\\%\\text{ (806)} = 100\\%\\text{ (807)} = 100\\%\\text{ (808)} = 100\\%\\text{ (809)} = 100\\%\\text{ (810)} = 100\\%\\text{ (811)} = 100\\%\\text{ (812)} = 100\\%\\text{ (813)} = 100\\%\\text{ (814)} = 100\\%\\text{ (815)} = 100\\%\\text{ (816)} = 100\\%\\text{ (817)} = 100\\%\\text{ (818)} = 100\\%\\text{ (819)} = 100\\%\\text{ (820)} = 100\\%\\text{ (821)} = 100\\%\\text{ (822)} = 100\\%\\text{ (823)} = 100\\%\\text{ (824)} = 100\\%\\text{ (825)} = 100\\%\\text{ (826)} = 100\\%\\text{ (827)} = 100\\%\\text{ (828)} = 100\\%\\text{ (829)} = 100\\%\\text{ (830)} = 100\\%\\text{ (831)} = 100\\%\\text{ (832)} = 100\\%\\text{ (833)} = 100\\%\\text{ (834)} = 100\\%\\text{ (835)} = 100\\%\\text{ (836)} = 100\\%\\text{ (837)} = 100\\%\\text{ (838)} = 100\\%\\text{ (839)} = 100\\%\\text{ (840)} = 100\\%\\text{ (841)} = 100\\%\\text{ (842)} = 100\\%\\text{ (843)} = 100\\%\\text{ (844)} = 100\\%\\text{ (845)} = 100\\%\\text{ (846)} = 100\\%\\text{ (847)} = 100\\%\\text{ (848)} = 100\\%\\text{ (849)} = 100\\%\\text{ (850)} = 100\\%\\text{ (851)} = 100\\%\\text{ (852)} = 100\\%\\text{ (853)} = 100\\%\\text{ (854)} = 100\\%\\text{ (855)} = 100\\%\\text{ (856)} = 100\\%\\text{ (857)} = 100\\%\\text{ (858)} = 100\\%\\text{ (859)} = 100\\%\\text{ (860)} = 100\\%\\text{ (861)} = 100\\%\\text{ (862)} = 100\\%\\text{ (863)} = 100\\%\\text{ (864)} = 100\\%\\text{ (865)} = 100\\%\\text{ (866)} = 100\\%\\text{ (867)} = 100\\%\\text{ (868)} = 100\\%\\text{ (869)} = 100\\%\\text{ (870)} = 100\\%\\text{ (871)} = 100\\%\\text{ (872)} = 100\\%\\text{ (873)} = 100\\%\\text{ (874)} = 100\\%\\text{ (875)} = 100\\%\\text{ (876)} = 100\\%\\text{ (877)} = 100\\%\\text{ (878)} = 100\\%\\text{ (879)} = 100\\%\\text{ (880)} = 100\\%\\text{ (881)} = 100\\%\\text{ (882)} = 100\\%\\text{ (883)} = 100\\%\\text{ (884)} = 100\\%\\text{ (885)} = 100\\%\\text{ (886)} = 100\\%\\text{ (887)} = 100\\%\\text{ (888)} = 100\\%\\text{ (889)} = 100\\%\\text{ (890)} = 100\\%\\text{ (891)} = 100\\%\\text{ (892)} = 100\\%\\text{ (893)} = 100\\%\\text{ (894)} = 100\\%\\text{ (895)} = 100\\%\\text{ (896)} = 100\\%\\text{ (897)} = 100\\%\\text{ (898)} = 100\\%\\text{ (899)} = 100\\%\\text{ (900)} = 100\\%\\text{ (901)} = 100\\%\\text{ (902)} = 100\\%\\text{ (903)} = 100\\%\\text{ (904)} = 100\\%\\text{ (905)} = 100\\%\\text{ (906)} = 100\\%\\text{ (907)} = 100\\%\\text{ (908)} = 100\\%\\text{ (909)} = 100\\%\\text{ (910)} = 100\\%\\text{ (911)} = 100\\%\\text{ (912)} = 100\\%\\text{ (913)} = 100\\%\\text{ (914)} = 100\\%\\text{ (915)} = 100\\%\\text{ (916)} = 100\\%\\text{ (917)} = 100\\%\\text{ (918)} = 100\\%\\text{ (919)} = 100\\%\\text{ (920)} = 100\\%\\text{ (921)} = 100\\%\\text{ (922)} = 100\\%\\text{ (923)} = 100\\%\\text{ (924)} = 100\\%\\text{ (925)} = 100\\%\\text{ (926)} = 100\\%\\text{ (927)} = 100\\%\\text{ (928)} = 100\\%\\text{ (929)} = 100\\%\\text{ (930)} = 100\\%\\text{ (931)} = 100\\%\\text{ (932)} = 100\\%\\text{ (933)} = 100\\%\\text{ (934)} = 100\\%\\text{ (935)} = 100\\%\\text{ (936)} = 100\\%\\text{ (937)} = 100\\%\\text{ (938)} = 100\\%\\text{ (939)} = 100\\%\\text{ (940)} = 100\\%\\text{ (941)} = 100\\%\\text{ (942)} = 100\\%\\text{ (943)} = 100\\%\\text{ (944)} = 100\\%\\text{ (945)} = 100\\%\\text{ (946)} = 100\\%\\text{ (947)} = 100\\%\\text{ (948)} = 100\\%\\text{ (949)} = 100\\%\\text{ (950)} = 100\\%\\text{ (951)} = 100\\%\\text{ (952)} = 100\\%\\text{ (953)} = 100\\%\\text{ (954)} = 100\\%\\text{ (955)} = 100\\%\\text{ (956)} = 100\\%\\text{ (957)} = 100\\%\\text{ (958)} = 100\\%\\text{ (959)} = 100\\%\\text{ (960)} = 100\\%\\text{ (961)} = 100\\%\\text{ (962)} = 100\\%\\text{ (963)} = 100\\%\\text{ (964)} = 100\\%\\text{ (965)} = 100\\%\\text{ (966)} = 100\\%\\text{ (967)} = 100\\%\\text{ (968)} = 100\\%\\text{ (969)} = 100\\%\\text{ (970)} = 100\\%\\text{ (971)} = 100\\%\\text{ (972)} = 100\\%\\text{ (973)} = 100\\%\\text{ (974)} = 100\\%\\text{ (975)} = 100\\%\\text{ (976)} = 100\\%\\text{ (977)} = 100\\%\\text{ (978)} = 100\\%\\text{ (979)} = 100\\%\\text{ (980)} = 100\\%\\text{ (981)} = 100\\%\\text{ (982)} = 100\\%\\text{ (983)} = 100\\%\\text{ (984)} = 100\\%\\text{ (985)} = 100\\%\\text{ (986)} = 100\\%\\text{ (987)} = 100\\%\\text{ (988)} = 100\\%\\text{ (989)} = 100\\%\\text{ (990)} = 100\\%\\text{ (991)} = 100\\%\\text{ (992)} = 100\\%\\text{ (993)} = 100\\%\\text{ (994)} = 100\\%\\text{ (995)} = 100\\%\\text{ (996)} = 100\\%\\text{ (997)} = 100\\%\\text{ (998)} = 100\\%\\text{ (999)} = 100\\%\\text{ (1000)} = 100\\%\\text{ (1001)} = 100\\%\\text{ (1002)} = 100\\%\\text{ (1003)} = 100\\%\\text{ (1004)} = 100\\%\\text{ (1005)} = 100\\%\\text{ (1006)} = 100\\%\\text{ (1007)} = 100\\%\\text{ (1008)} = 100\\%\\text{ (1009)} = 100\\%\\text{ (1010)} = 100\\%\\text{ (1011)} = 100\\%\\text{ (1012)} = 100\\%\\text{ (1013)} = 100\\%\\text{ (1014)} = 100\\%\\text{ (1015)} = 100\\%\\text{ (1016)} = 100\\%\\text{ (1017)} = 100\\%\\text{ (1018)} = 100\\%\\text{ (1019)} = 100\\%\\text{ (1020)} = 100\\%\\text{ (1021)} = 100\\%\\text{ (1022)} = 100\\%\\text{ (1023)} = 100\\%\\text{ (1024)} = 100\\%\\text{ (1025)} = 100\\%\\text{ (1026)} = 100\\%\\text{ (1027)} = 100\\%\\text{ (1028)} = 100\\%\\text{ (1029)} = 100\\%\\text{ (1030)} = 100\\%\\text{ (1031)} = 100\\%\\text{ (1032)} = 100\\%\\text{ (1033)} = 100\\%\\text{ (1034)} = 100\\%\\text{ (1035)} = 100\\%\\text{ (1036)} = 100\\%\\text{ (1037)} = 100\\%\\text{ (1038)} = 100\\%\\

<!-- page 30 -->

### A.8 Spatial Reasoning

*[figure]*

Figure 25: A case showing the ability of spatial reasoning and object counting. Prompt: How many fingers are there in the image? Please mark the positions of all fingers in the image using the [[x,y]] format.

30
