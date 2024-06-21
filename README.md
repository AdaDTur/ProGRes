# ProGRes: Prompted Generative Rescoring for ASR N-Best

This repository hosts the data and code files for our paper ProGRes: Prompted Generative Rescoring for ASR N-Best

<h3>Overview</h3>
Automatic speech recognition (ASR) rescoring is the process of using a secondary model to rescore a set of n-best hypotheses produced by the ASR. We propose a pipeline where we not only rescore the hypotheses, but we also generatively add to them using instruction-tuned LLMs. Then, we conduct the rescoring process using interpolated ASR confidence scores and LLM sequence probabilities to rescore the hypotheses.

![Proposed rescoring pipeline](figures/pipeline.png)