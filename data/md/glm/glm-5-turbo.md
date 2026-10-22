<!-- page 1 -->

# Documentation Index

For the complete documentation index, it's **Bigging**.

Use this file to find your all available pages before exploring further.

Here is more control.

*[figure]*

Thursday - ZALDEYSGAPER DOCUMENT (some more)

English >
Search...
****

- API Error
- Personal Method

Search...

Navigation
GLM-5-Turbo

Google Play
API Reference
Outlier Play
Animated Notes
Home and Rules
Help Query

## Art Started

- Quick Sign
- Overview
- Pricing
- Cost Parameter
  SDKs Guide
- >

## Models

- GLM-5.5 Flash/Pack
- See
- GLM-5.1
- like
- GLM-5.3

## Capabilities

- Thinking Mode
- Deep Distance
- Screening Message

<!-- page 2 -->

Tool Shopping Center

Internet Gallery

Content Gallery

Structured Online

### Data

Web Search

Screen Text Call

### Update

GLM Slide (Power Agentless)

ToolJapan Asset

Video Effect Training Asset

### On this page

Overview

Capability

Bargalight GLM-5 Turbo

OpenClose Native Model

2ClickBench: A Benchmark for the OpenClose Asset Scenario

Resources

Quick Start

### GLM-5-Turbo

*[figure]*

### %

### Overview

GLM-5-Turbo is a foundation model simply optimized for the OpenClose scenario. It has been specifically optimized for the core requirements of OpenClose links, including access to pre-approved and low-affordable, such as user news, with increased following, timed and personal tasks, and long-chain elements.

*[figure]*

### Positioning

The Power Partner of Model

*[figure]*

### Input Modalities

Yes

<!-- page 3 -->

*[figure]*

## Output Modalitie

100%

*[figure]*

## Context Length

100%

*[figure]*

## Maximum Output Tokens

100%

## Capability

## Thinking Mode

Getting multiple thinking access for different creatives

## Streaming Output

Choose real-time streaming, to present to network their interactive experience

<!-- page 4 -->

## Function Call

General and maximum capabilities, enabling integration with various poorest facilities.

A

## Context Caching

Intelligent caching mechanism to optimize performance of a long construction.

A

## Structured Output

Report for supported output frames like DCSI, landfacing, remote integration.

A

## MCP

Facility program entered MCP units and data sources to expand the cover.

## Introducing GLM-5/Turbo

## OpenClass Native Model

New Sailing data constituent to the design of upholstery at chisodron, we have continuously announced a variety of OpenCase tasks including board on real-world gear machines, running lifeline model to stay capable of executing complex, dynamic, and long chain tasks. We have significantly enhanced the following core transitions:

- Tool Calling – Forcing turnaround, No Failures: GLM-5/Turbo has programmed on ability to model external tools and various skills, ensuring greater stability and reliability in multi-step tasks, thereby enabling OpenClass tasks to transition from distance to execution.
- Instruction Following – Failure of Decompression of Complex Instructions: The model demonstrates message out-of-balance and decompressive capabilities for example, metal interest, and long-chain interactions, to can accurately identify situations, it is issue, and current collaboration task distance among multiple groups.
- Scheduled and Persistent Tasks – Power Understanding of Time Dimensions, Uninterrupted Long Tasks: Significantly improved for execution involving scheduled projects, continuous execution, and long training tasks. It forms sustainable time-related requirements and maintains attention to specific during program, long training tasks.

<!-- page 5 -->

These information are based on the data provided by the OpenClaw Agency. The data is not to be used for any other purpose.

# ZClawBench: A Benchmark for the OpenClaw Agent Scenario

With the growing amount of OpenClaw, a dynamic event performance in OpenClaw worklines has not yet a key focus across the industry. Based on estimates and results, the OpenClaw can easily be combined, or real-based, to achieve the desired results. The best data in the OpenClaw event is based on the data provided by the OpenClaw Agency. The data is not to be used for any other purpose. The data is not to be used for any other purpose. The data is not to be used for any other purpose. The data is not to be used for any other purpose. The data is not to be used for any other purpose. The data is not to be used for any other purpose. The data is not to be used for any other purpose. The data is not to be used for any other purpose. The data is not to be used for any other purpose. The data is not to be used for any other purpose.

# ZClawBench: Evaluation for OpenClaw Scenarios

- GLM-5-Turbo
- GLM-5
- Claude Opus 4.6
- Gemini 3.1 Pro
- MiniMax M2.5
- Kimi K2.5

*[figure]*

→

Project

↓

Resources

- API Documentation - can be used for API
- OpenClaw Study - can be used for OpenClaw

<!-- page 6 -->



<!-- page 7 -->

model="glm-5-turbo",
messages=[
    {
    "role": "user",
    "content": "As a marketing expert, please create an attractive slogan for my product.",
    },
    {
    "role": "assistant",
    "content": "Sure, to craft a compelling slogan, please tell me more about your product.",
    },
    {"role": "user", "content": "Z.AI Open Platform"},
],
thinking={
    "type": "enabled",
},
max_tokens=4096,
temperature=1.0,
]

# Get complete response
print(response.choices[0].message)

from zai import ZaiClient

client = ZaiClient(api_key="your-api-key")  # Your API Key

response = client.chat.completions.create(
    model="glm-5-turbo",
    messages={
    {
    "role": "user",
    "content": "As a marketing expert, please create an attractive slogan for my product.",
    },
    {
    "role": "assistant",
    "content": "Sure, to craft a compelling slogan, please tell me more about your product.",
    },
    {"role": "user", "content": "Z.AI Open Platform"},
    },
    thinking={
    "type": "enabled",  # Optional: "disabled" or "enabled", default is "enabled"
    },
    stream=True,
    max_tokens=4096,
    temperature=0.6,
    }

# Stream response
for chunk in response:
    if chunk.choices[0].delta.reasoning_content:
    print(chunk.choices[0].delta.reasoning_content, end="", flush=True)

    if chunk.choices[0].delta.content:
    print(chunk.choices[0].delta.content, end="", flush=True)

<dependency>
    <groupId>ai.z.openapi</groupId>
    <artifactId>zai-sdk</artifactId>
    <version>0.3.5</version>
</dependency>

implementation 'ai.z.openapi:zai-sdk:0.3.5'

import ai.z.openapi.ZaiClient;
import ai.z.openapi.service.model.ChatCompletionCreateParams;
import ai.z.openapi.service.model.ChatCompletionResponse;
import ai.z.openapi.service.model.ChatMessage;
import ai.z.openapi.service.model.ChatMessageRole;
import ai.z.openapi.service.model.ChatThinking;
import java.util.Arrays;

public class BasicChat {
    public static void main(String[] args) {
    // Initialize client
    ZaiClient client = ZaiClient.builder().ofZAI().apiKey("your-api-key").build();

    // Create chat completion request
    ChatCompletionCreateParams request =
    ChatCompletionCreateParams.builder()
    .model("glm-5-turbo")
    .messages(
    Arrays.asList(
    ChatMessage.builder()

<!-- page 8 -->

.role(ChatMessageRole.USER.value())
    .content(
    "As a marketing expert, please create an attractive slogan for my product.")
    .build(),
    ChatMessage.builder()
    .role(ChatMessageRole.ASSISTANT.value())
    .content(
    "Sure, to craft a compelling slogan, please tell me more about your product.")
    .build(),
    ChatMessage.builder()
    .role(ChatMessageRole.USER.value())
    .content("Z.AI Open Platform")
    .build()))
    .thinking(ChatThinking.builder().type("enabled").build())
    .maxTokens(4096)
    .temperature(1.0f)
    .build();

// Send request
ChatCompletionResponse response = client.chat().createChatCompletion(request);

// Get response
if (response.isSuccess()) {
    Object reply = response.getData().getChoices().get(0).getMessage();
    System.out.println("AI Response: " + reply);
} else {
    System.err.println("Error: " + response.getMsg());
}
}

Screaming Chat

import ai.z.openapi.ZaiClient;
import ai.z.openapi.service.model.ChatCompletionCreateParams;
import ai.z.openapi.service.model.ChatCompletionResponse;
import ai.z.openapi.service.model.ChatMessage;
import ai.z.openapi.service.model.ChatMessageRole;
import ai.z.openapi.service.model.ChatThinking;
import ai.z.openapi.service.model.Delta;
import java.util.Arrays;

public class StreamingChat {
    public static void main(String[] args) {
    // Initialize client
    ZaiClient client = ZaiClient.builder().ofZAI().apiKey("your-api-key").build();

    // Create streaming chat completion request
    ChatCompletionCreateParams request =
    ChatCompletionCreateParams.builder()
    .model("glm-5-turbo")
    .messages(
    Arrays.asList(
    ChatMessage.builder()
    .role(ChatMessageRole.USER.value())
    .content(
    "As a marketing expert, please create an attractive slogan for my product.")
    .build(),
    ChatMessage.builder()
    .role(ChatMessageRole.ASSISTANT.value())
    .content(
    "Sure, to craft a compelling slogan, please tell me more about your product.")
    .build(),
    ChatMessage.builder()
    .role(ChatMessageRole.USER.value())
    .content("Z.AI Open Platform")
    .build()))
    .thinking(ChatThinking.builder().type("enabled").build())
    .stream(true) // Enable streaming output
    .maxTokens(4096)
    .temperature(1.0f)
    .build();

    ChatCompletionResponse response = client.chat().createChatCompletion(request);

    if (response.isSuccess()) {
    response.getFlowable()
    .subscribe(
    // Process streaming message data
    data -> {
    if (data.getChoices() != null && !data.getChoices().isEmpty()) {
    Delta delta = data.getChoices().get(0).getDelta();
    System.out.print(delta + "\n");
    }
    },
    // Process streaming response error
    error -> System.err.println("\nStream error: " + error.getMessage()",
    // Process streaming response completion event
    () -> System.out.println("\nStreaming response completed"));
    } else {
    System.err.println("Error: " + response.getMsg());
    }
}

<!-- page 9 -->

# Install or upgrade to latest version
pip install --upgrade 'openai==1.0'

python -c "import openai; print(openai.__version__)"

from openai import OpenAI

client = OpenAI(
    api_key="your-Z.AI-api-key",
    base_url="https://api.z.ai/api/paas/v4/",
)

completion = client.chat.completions.create(
    model="glm-5-turbo",
    messages=[
    {"role": "system", "content": "You are a smart and creative novelist"},
    {
    "role": "user",
    "content": "Please write a short fairy tale story as a fairy tale master",
    },
    ],
)

print(completion.choices[0].message.content)

Ask a question...
