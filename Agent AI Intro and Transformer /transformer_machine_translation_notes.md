# Teaching Notes: Transformer Architecture for Machine Translation

**Audience:** Students new to Deep Learning and AI  
**Goal:** Understand the Transformer encoder–decoder and how it is used for machine translation.

---

## Table of Contents

1. [Where We Start: The Problem](#1-where-we-start-the-problem)
2. [From RNNs to Transformers (Motivation)](#2-from-rnns-to-transformers-motivation)
3. [Big Picture: Encoder–Decoder for Translation](#3-big-picture-encoder-decoder-for-translation)
4. [Turning Words into Numbers](#4-turning-words-into-numbers)
5. [The Encoder](#5-the-encoder)
6. [The Decoder](#6-the-decoder)
7. [How Encoder and Decoder Work Together](#7-how-encoder-and-decoder-work-together)
8. [From Scores to Words: Output Layer](#8-from-scores-to-words-output-layer)
9. [Training vs Inference](#9-training-vs-inference)
10. [Summary Diagram and Checklist](#10-summary-diagram-and-checklist)

---

## 1. Where We Start: The Problem

**Machine translation (MT):**  
Input: a sentence in one language (e.g. English).  
Output: the same meaning in another language (e.g. French).

- Input: *"The cat sat on the mat."*
- Output: *"Le chat s'est assis sur le tapis."*

The model must:
1. **Understand** the full input sentence.
2. **Generate** the output sentence **one word at a time**, using that understanding.

So we need:
- Something that **reads and summarizes** the input → **Encoder**.
- Something that **generates** the target sentence step by step → **Decoder**.

---

## 2. From RNNs to Transformers (Motivation)

**Older approach: RNNs (Recurrent Neural Networks)**  
- Process the input **word by word, in order**.
- Each word is processed using the “memory” from the previous words.
- Drawbacks:
  - **Slow:** Cannot process all words in parallel; must wait for previous steps.
  - **Long-range dependency:** Information from the start of the sentence can get “diluted” by the time we reach the end.

**Transformer (2017, “Attention Is All You Need”)**  
- Does **not** process words strictly one-by-one in sequence.
- Uses **attention**: at each position, the model can “look at” **any** other position (all at once, in parallel).
- Benefits:
  - **Parallel:** Many operations can be done in parallel → faster training.
  - **Direct connections:** The word “cat” can directly attend to “chat” when generating the translation, no matter how far apart they are.

You can tell students: *“Think of attention as: when producing each output word, the model is allowed to look at every input word and decide which ones to focus on.”*

---

## 3. Big Picture: Encoder–Decoder for Translation

```
INPUT (Source sentence, e.g. English)
         │
         ▼
   ┌─────────────┐
   │   ENCODER   │  ← Reads the whole input, produces a "summary" (context)
   │  (stack of  │     for each position
   │   layers)   │
   └──────┬──────┘
          │  Encoder output (context)
          ▼
   ┌─────────────┐
   │   DECODER   │  ← Generates the target sentence one word at a time,
   │  (stack of  │     using encoder output + previously generated words
   │   layers)   │
   └──────┬──────┘
          │
          ▼
OUTPUT (Target sentence, e.g. French)
```

**Roles in one sentence:**  
- **Encoder:** “What does the source sentence mean?” → one representation per input position.  
- **Decoder:** “Given that meaning and what I’ve already written, what is the next word?” → repeat until end-of-sentence.

---

## 4. Turning Words into Numbers

Neural networks only work with numbers. So we do two things:

### 4.1 Tokenization

- Split the text into **tokens** (words or subwords).
- Example: *"The cat sat"* → `["The", "cat", "sat"]`.
- Each token has an **ID** from a vocabulary (e.g. "The" = 5, "cat" = 102).

### 4.2 Embedding

- An **embedding layer** converts each token ID into a **vector** of fixed size (e.g. 256 or 512 numbers).
- So the input sentence becomes a **sequence of vectors**: one vector per token.

### 4.3 Positional Encoding

- The Transformer has no built-in notion of “first word,” “second word,” etc.
- We add **positional encodings** to each token’s embedding so the model knows **order**.
- Result: each token is represented by **embedding + position**.

**Takeaway:**  
Input sentence → list of token IDs → embeddings → add position → **matrix of shape (sequence length × model dimension)**. This is what the encoder sees.

---

## 5. The Encoder

The encoder is a **stack of identical layers**. Each layer has two main sub-layers:

1. **Multi-Head Self-Attention**
2. **Feed-Forward Network**

Around each sub-layer we use **residual connection** and **layer normalization** (you can say: “add the input back and normalize so training is stable”).

### 5.1 What Is Self-Attention?

**Idea:** For each word in the input, we want a new representation that incorporates **information from all other words** in the same sentence.

- **Query (Q):** “What am I looking for?”
- **Key (K):** “What do I offer?”
- **Value (V):** “What information do I give?”

For each token we compute Q, K, V (using learned weight matrices). Then:

1. **Scores:** Compare each token’s Q with every token’s K → scores (how relevant is each other token?).
2. **Weights:** Apply **softmax** on those scores → weights sum to 1 (attention weights).
3. **Output:** For each position, take a **weighted sum of all V vectors** using these weights.

So the new representation at position *i* is: “a mix of all tokens, where the mix is decided by how relevant each token is to position *i*.”

**Multi-Head Attention:**  
We do this several times in parallel (e.g. 8 “heads”) with different Q/K/V projections, then concatenate and project. This lets the model focus on different types of relationships (e.g. syntax vs meaning) in different heads.

### 5.2 Feed-Forward Network (FFN)

- Same at every position: two linear layers with a non-linearity (e.g. ReLU) in between.
- Formula (conceptually): `FFN(x) = Linear2(ReLU(Linear1(x)))`.
- This adds per-position processing after mixing information via attention.

### 5.3 Encoder Output

After all encoder layers, we have **one vector per input token**. Together they form the **encoder output** (the “context” the decoder will use). Shape: (input length × model dimension).

**Summary for students:**  
The encoder turns the source sentence into a set of vectors that capture the meaning of the whole sentence (and each position), using self-attention and FFNs.

---

## 6. The Decoder

The decoder is also a **stack of identical layers**. Each layer has **three** sub-layers:

1. **Masked Multi-Head Self-Attention** (only over **decoder** positions)
2. **Cross-Attention** (decoder attends to **encoder output**)
3. **Feed-Forward Network**

Again: residual connections and layer norm around each sub-layer.

### 6.1 Masked Self-Attention

- When generating the **next** word, the model must not “see” future words (we don’t know them yet).
- So we **mask** the attention: at position *i*, the decoder can only attend to positions 1, 2, …, *i* (and often a start token at 0).
- Mechanically: before softmax, we set scores for positions > *i* to a very negative number so their attention weight becomes ~0.

So the decoder’s self-attention is “causal”: each position only looks at past and current tokens.

### 6.2 Cross-Attention (Encoder–Decoder Attention)

- **Query (Q)** comes from the **decoder** (current decoder layer output).
- **Key (K)** and **Value (V)** come from the **encoder output**.
- So: for each decoder position, we ask “which parts of the **source sentence** should I focus on right now?”
- This is how the translation of “chat” can focus on “cat” in the source.

**Difference from encoder self-attention:**  
- Encoder: attention within the **same** sequence (source ↔ source).  
- Decoder cross-attention: decoder positions attend to **encoder output** (target position ↔ source).

### 6.3 Feed-Forward in the Decoder

- Same idea as in the encoder: two linear layers + activation. Applied per decoder position after cross-attention.

**Summary for students:**  
The decoder (1) looks at its own previous words (masked self-attention), (2) looks at the encoder’s summary of the source (cross-attention), (3) processes with an FFN, and repeats for several layers. Then it predicts the next word.

---

## 7. How Encoder and Decoder Work Together

- **Encoder:**  
  Input: source token embeddings + positions.  
  Output: one vector per source token → **encoder output**.

- **Decoder:**  
  Input at each step:
  - Target tokens generated so far (embeddings + positions),
  - **Encoder output** (fed into **cross-attention** as K and V).
  Output: one vector per decoder position. We use the vector at the **last** position to predict the **next** word.

So the only place encoder and decoder “meet” is **cross-attention**: decoder queries, encoder output provides keys and values.

---

## 8. From Scores to Words: Output Layer

After the last decoder layer we have a vector for the “current” position (e.g. after feeding &lt;START&gt; Le chat s'est assis). We then:

1. **Linear layer:** Map the decoder vector to a vector of size = vocabulary size → one **score** per word.
2. **Softmax:** Turn scores into **probabilities** (they sum to 1).
3. **Training:** We use the correct next word and minimize cross-entropy (e.g. “correct word should have high probability”).
4. **Inference:** We pick one word (e.g. argmax or sampling), append it to the sequence, and repeat until we get an end-of-sentence token.

So: **decoder final hidden state → linear → softmax → next-word distribution**.

---

## 9. Training vs Inference

### 9.1 Training (Teacher Forcing)

- We have many pairs (source sentence, target sentence).
- We feed the **entire target sentence** into the decoder (with a start token), but **mask** the self-attention so position *i* only sees positions ≤ *i*.
- At each position *i*, we predict the **next** word (position *i*+1) and compare to the true word; loss is cross-entropy.
- So we can compute loss for all positions in **parallel** (efficient).

### 9.2 Inference (Actual Translation)

- We only have the source sentence.
- We start with &lt;START&gt; and run the decoder → get distribution over words → pick one (e.g. “Le”), append it.
- Input is now &lt;START&gt; Le → run decoder again → next word (e.g. “chat”) → append.
- We **repeat** until the model outputs an end-of-sentence token (e.g. &lt;END&gt;).

So inference is **autoregressive**: one word at a time, each step conditioned on the source (via encoder) and all previously generated words.

---

## 10. Summary Diagram and Checklist

### End-to-End Flow (Machine Translation)

```
Source: "The cat sat on the mat"
    │
    ▼  Tokenize → Embed → Add position
    │
    ▼  ┌─────────────────────────────────────┐
    │  │ ENCODER (e.g. 6 layers)              │
    │  │  • Self-attention (source ↔ source)  │
    │  │  • Feed-forward                      │
    │  └──────────────────┬──────────────────┘
    │                     │ Encoder output
    │                     ▼
    │  ┌─────────────────────────────────────┐
    │  │ DECODER (e.g. 6 layers)             │
    │  │  • Masked self-attention (target)    │
    │  │  • Cross-attention (target → source) │  ← Uses encoder output
    │  │  • Feed-forward                      │
    │  └──────────────────┬──────────────────┘
    │                     │
    │                     ▼  Linear + Softmax
    │                     │
    ▼                     ▼
Target: "Le chat s'est assis sur le tapis."
         (generated one word at a time)
```

### Concept Checklist for Students

- [ ] **Encoder:** Reads source; self-attention + FFN; output = context (one vector per source token).
- [ ] **Decoder:** Generates target step by step; masked self-attention (no future); cross-attention to encoder; FFN.
- [ ] **Self-attention:** Each position looks at all (allowed) positions in the **same** sequence; Q, K, V; weights from softmax.
- [ ] **Cross-attention:** Decoder looks at **encoder output**; Q from decoder, K and V from encoder.
- [ ] **Masking in decoder:** So the model cannot use future target words when predicting the next word.
- [ ] **Embedding + positional encoding:** Words → vectors; add position so order is known.
- [ ] **Output:** Last decoder position → linear → softmax → next-word probabilities.
- [ ] **Training:** Full target fed in with masking; loss at each position. **Inference:** Generate one word at a time until &lt;END&gt;.

---

## Optional: One-Slide Recap for the Board

**Transformer for machine translation:**

1. **Input** → tokens → embeddings + positions.
2. **Encoder** → self-attention + FFN (× N layers) → context vectors.
3. **Decoder** → masked self-attention + **cross-attention to encoder** + FFN (× N layers) → one vector per target position.
4. **Output** → last vector → linear → softmax → next word → repeat until &lt;END&gt;.

**Key phrase:** “Encoder summarizes the source; decoder generates the target one word at a time, looking at the encoder’s summary and at its own past words.”

---

*End of notes. You can add a simple diagram of one attention head (Q, K, V → scores → weights → weighted sum) on the board when explaining self-attention.*
