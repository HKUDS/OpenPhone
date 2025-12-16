<div align="center">
  <picture>
      <img src="./figures/logo_new.png" width="20%" style="border: none; box-shadow: none;">
  </picture>
</div >

<div align="center">

# ✨Open-PhoneAgent✨: Mobile Agentic Foundation Models for AI Phone

</div>

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Orbitron&size=24&duration=3000&pause=1000&color=00D9FF&center=true&vCenter=true&width=600&lines=Welcome+to+Open-PhoneAgent;Mobile+Agentic+Foundation+Models;AI+Phone" alt="Typing Animation" />
</div>

<div align="center">
  <img src="./demo/lightagent_demo.gif" width="800" height="400" alt="演示动画">
</div>

<div align="center">
  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 25px; text-align: center;">
    <p>
      <a href='https://github.com/HKUDS/LightAgent'><img src='https://img.shields.io/badge/🔥Project-Page-00d9ff?style=for-the-badge&logo=github&logoColor=white&labelColor=1a1a2e'></a>
      <a href="https://huggingface.co/datasets/hkuds/LightAgent_dataset"><img alt="Hugging Face" src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-ffc107?style=for-the-badge&color=ffc107&logoColor=white&labelColor=1a1a2e"/></a>
      <a href="https://huggingface.co/hkuds/LightAgent_model"><img alt="Hugging Face" src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Model-ffc107?style=for-the-badge&color=ffc107&logoColor=white&labelColor=1a1a2e"/></a>
      <a href='https://github.com/THUDM/Android-Lab'><img src='https://img.shields.io/badge/⚡Based%20on-AndroidLab-4ecdc4?style=for-the-badge&logo=lightning&logoColor=white&labelColor=1a1a2e'></a>
    </p>
    <p>
      <a href="https://github.com/HKUDS/LightAgent/stargazers"><img src='https://img.shields.io/github/stars/HKUDS/LightAgent?color=00d9ff&style=for-the-badge&logo=star&logoColor=white&labelColor=1a1a2e' /></a>
      <a href="./Communication.md"><img src="https://img.shields.io/badge/💬Feishu-Group-07c160?style=for-the-badge&logoColor=white&labelColor=1a1a2e"></a>
      <a href="./Communication.md"><img src="https://img.shields.io/badge/WeChat-Group-07c160?style=for-the-badge&logo=wechat&logoColor=white&labelColor=1a1a2e"></a>
      <a href=""><img src="https://img.shields.io/badge/Platform-Android-d3d3d3?style=for-the-badge&logo=android&logoColor=white&labelColor=1a1a2e"/></a>
      <a href='https://arxiv.org/abs/2510.22009'><img src='https://img.shields.io/badge/📄arXiv-2510.22009-ff6b6b?style=for-the-badge&logo=arxiv&logoColor=white&labelColor=1a1a2e'></a>
    </p>
  </div>
</div>

</div>

<div align="center">
  <div style="width: 100%; height: 2px; margin: 20px 0; background: linear-gradient(90deg, transparent, #00d9ff, transparent);"></div>
</div>

## 🎯 What is Open-PhoneAgent?

**The Problem**: Current mobile AI agents rely on expensive cloud APIs and large language models that are impractical for real-world deployment. Users face **Privacy Concerns**, **Latency Issues**, and **High Costs** when their phone needs to call external services for every interaction.

**Our Solution**: Open-PhoneAgent introduces the first **Open-Source 3B-Parameter Agentic Foundation Model** specifically proposed for smartphone interaction. This compact Vision-Language Model runs entirely on your device - **No Privacy Concerns** and **No API Costs**.

**Why 3B Parameters?** We believe the future of mobile AI isn't about cramming larger models into phones, but about smart optimization for real-world constraints:
- **⚡ Edge-Ready**: Runs on commodity GPUs and emerging mobile NPUs
- **🔒 Privacy-First**: All processing happens locally on your device
- **💰 Cost-Effective**: No ongoing API fees or cloud dependencies
- **🎯 Performance-Optimized**: Matches 7B-9B model performance through advanced training

---

## 💡 Research Highlights

## 🔍 LightAgent-3B: Open-Source On-Device GUI Agent Model

- **Model size & architecture**: ~3B-parameter vision-language model tailored for mobile GUI understanding and action generation, optimized for efficiency rather than maximal scale.
- **On-device first**: Designed to run as the **primary agent on the device**, with latency and memory usage compatible with single 3090-class GPUs and future mobile chips, instead of assuming always-on cloud access.
- **GUI-specialized skills**: Trained to perceive mobile screens, reason over GUI layouts, and produce structured action sequences (click, scroll, input, navigation) for real-world apps.
- **Open-source release**: We release the full 3B model weights, configuration, and inference stack so that researchers and practitioners can deploy, fine-tune, and extend the model for their own mobile agents.
- **Practical sweet spot**: In current hardware conditions, 3B sits at a **practical sweet spot**—significantly stronger than tiny models, but still deployable on edge devices where 7B–9B models are often too heavy.

### Why 3B is the sweet spot for on-device GUI agents

- **Deployment feasibility**: 3B fits comfortably on a single high-end consumer GPU and is a realistic target for upcoming mobile NPUs, while 7B–9B models typically exceed memory or latency budgets for real edge devices.
- **Latency vs. capability trade-off**: For GUI control, responsiveness matters as much as accuracy. Our experiments show that a well-trained 3B model offers a much better latency/quality trade-off than larger models that are hard to deploy.
- **Cloud offloading as a backup, not default**: In Open-PhoneAgent, the 3B model handles steps locally, with the hardest cases escalated to strong cloud models—reducing cost and preserving user privacy.

### Model release & resources

- **Model weights**: `LightAgent-3B` is released on [Hugging Face](https://huggingface.co/hkuds/LightAgent_model).
- **Serving stack**: We provide vLLM-based scripts to run the 3B model efficiently as an inference service.
- **Training recipe**: The training code and instructions (SFT + RL with synthetic GUI data) are documented under `model_training/` so you can reproduce or adapt the 3B model for your own use cases.

---

## 📖 Table of Contents
- [✨Open-PhoneAgent✨: Mobile Agentic Foundation Models for AI Phone](#open-phoneagent-mobile-agentic-foundation-models-for-ai-phone)
  - [🎯 What is Open-PhoneAgent?](#-what-is-open-phoneagent)
  - [💡 Research Highlights](#-research-highlights)
  - [🔍 LightAgent-3B: Open-Source On-Device GUI Agent Model](#-lightagent-3b-open-source-on-device-gui-agent-model)
    - [Why 3B is the sweet spot for on-device GUI agents](#why-3b-is-the-sweet-spot-for-on-device-gui-agents)
    - [Model release \& resources](#model-release--resources)
  - [📖 Table of Contents](#-table-of-contents)
  - [🌟 Key Features of Open-PhoneAgent](#-key-features-of-open-phoneagent)
    - [🤖 Lightweight Agentic Foundation Models](#-lightweight-agentic-foundation-models)
    - [☁️ Device-Cloud Collaboration Framework](#️-device-cloud-collaboration-framework)
    - [🎯 Comprehensive Mobile Agent Evaluation Playground](#-comprehensive-mobile-agent-evaluation-playground)
  - [🌟 Core Solutions of Open-PhoneAgent](#-core-solutions-of-open-phoneagent)
    - [🧠 Model Training: SFT+RL](#-model-training-sftrl)
    - [☁️ Device-Cloud Collaboration Framework](#️-device-cloud-collaboration-framework-1)
    - [💾 Efficient Memory Mechanism for Mobile Agents](#-efficient-memory-mechanism-for-mobile-agents)
  - [🚀 Quick Start](#-quick-start)
    - [📱 AndroidLab Benchmark Setup](#-androidlab-benchmark-setup)
    - [🚀 Model Deployment \& Inference](#-model-deployment--inference)
    - [⚙️ Pre-Testing Configuration](#️-pre-testing-configuration)
  - [🧪 Testing \& Evaluation](#-testing--evaluation)
    - [Single Task Testing](#single-task-testing)
    - [Batch Evaluation Scripts](#batch-evaluation-scripts)
    - [Additional App Documentation](#additional-app-documentation)
  - [📊 Result Generation](#-result-generation)
    - [LLM Evaluator Setup](#llm-evaluator-setup)
    - [Generate Evaluation Results](#generate-evaluation-results)
    - [Batch Testing File Management](#batch-testing-file-management)
  - [🎯 Evaluation Results](#-evaluation-results)
  - [🌟 Citation](#-citation)
  - [🔗 Related Projects](#-related-projects)
  - [📜 License](#-license)

---

## 🌟 Key Features of Open-PhoneAgent

### 🤖 Lightweight Agentic Foundation Models
• **Compact Architecture**: Specialized **3B-scale** Vision-Language Models optimized for mobile GUI tasks with minimal computational footprint.<br>
• **On-Device Deployment**: True smartphone-compatible models that maintain competitive performance while running locally without cloud dependency.

### ☁️ Device-Cloud Collaboration Framework
• **Dynamic Orchestration**: Real-time task complexity assessment that intelligently switches between device and cloud models based on execution requirements. <br>
• **Cost-Performance Optimization**: Strategic resource allocation that leverages cost-efficient on-device models while compensating limitations through selective cloud model usage.

### 🎯 Comprehensive Mobile Agent Evaluation Playground
• **Extended Benchmark Suite**: Beyond AndroidLab, incorporating 25+ additional tasks across popular mobile applications for real-world validation. <br>
• **Multi-Dimensional Assessment**: Comprehensive evaluation covering performance metrics, computational efficiency, and practical deployment scenarios.

---

## 🌟 Core Solutions of Open-PhoneAgent

### 🧠 Model Training: SFT+RL
• **Synthetic Data Generation**: Leverages advanced MLLMs to create high-quality reasoning chain training data, addressing the scarcity of manual annotations. <br>
• **Two-Stage Training**: SFT injects GUI foundational knowledge, while GRPO reinforcement learning optimizes task completion accuracy. <br>
• **Small Model Enhancement**: Enables 3B models to achieve performance comparable to 7B-9B models on GUI tasks through structured training. 

### ☁️ Device-Cloud Collaboration Framework
• **Dynamic Task Assessment**: Real-time complexity evaluation determines when and how frequently to monitor device model performance. <br>
• **Intelligent Orchestration**: Seamlessly switches between device and cloud models based on execution progress and failure patterns. <br>
• **Cost-Performance Optimization**: Reduces cloud invocations by ~10% while maintaining high task success rates through strategic resource allocation.

### 💾 Efficient Memory Mechanism for Mobile Agents
• **Long-Horizon Reasoning**: Multi-step chain-of-thought reasoning with reflective error correction to enhance decision-making capabilities. <br>
• **Text-Based Summarization**: Compresses high-resolution screenshots into compact textual representations for efficient memory management. <br>
• **Structured Context Retention**: Maintains 10-20 steps of historical context in resource-constrained environments through optimized token usage.

---

<img src="./figures/model_large.png" style="zoom:100%;" />

---

## 🚀 Quick Start
This project comprises three core components designed for comprehensive mobile agent development and evaluation:

- ⚡ For **model training**, please refer to the training guide [README](./model_training/README.md) for comprehensive setup and execution instructions.
- 🔧 For the **data generation pipeline**, please refer to the data preparation guide [README](./prepare_data/README.md) for detailed implementation steps.

Below, we focus on evaluation using the AndroidLab benchmark framework.

### 📱 AndroidLab Benchmark Setup
Installation: Follow the official AndroidLab documentation [AndroidLab](https://github.com/THUDM/Android-Lab) for complete setup instructions.<br>

**Environment Configuration**:
- Recommended Mode: AVD on Mac (arm64) - validated in our experiments.<br>
- App Setup: Manual installation and task-specific configuration required.<br>
- Compatibility Note: Original Docker images are not compatible with AVD environments.<br>

### 🚀 Model Deployment & Inference
**vLLM Integration**:
- Inference scripts available in ./vllm_script/ directory<br>
- Optimized for efficient small model serving<br>

**Model Access**:
- LightAgent Weights: 3B parameter model hosted on HuggingFace<br>
- Deployment Process: Download weights → Deploy via vLLM → Configure inference service<br>
- Service Ready: Seamless integration with evaluation pipeline<br>

### ⚙️ Pre-Testing Configuration
- API Setup Required: Configure cloud model credentials in ./evaluation/evaluation.py: Line 63, Line 75, Line 81<br>
- Coming Soon: Streamlined configuration interface in development<br>

---

## 🧪 Testing & Evaluation

### Single Task Testing
Test individual tasks using the following command structure:

```bash
python eval.py -n test_name -c your path to config.yaml --task_id task_id
```

Example Usage:

```bash
python eval.py -n all_cloud_v1_hyper -c ./configs/example_xml_cloud_hyper.yaml --task_id zoom_1
```

### Batch Evaluation Scripts
Convenient batch testing scripts are available in `./test_script`:

• `all_test_cloud_v1_hyper.sh`: Evaluates all 138 AndroidLab benchmark tasks<br>
• `all_test_cloud_v1_hyper_add.sh`: Evaluates tasks for four additional mobile apps<br>

### Additional App Documentation
For comprehensive details about the four additional app tasks, refer to the documentation: [Additional Apps Documentation](./docs/new_apps.md)

---

## 📊 Result Generation

### LLM Evaluator Setup
Required Configuration: Set up LLM service credentials in ./evaluation/tasks/llm_evaluator.py:

• Line 10: API configuration<br>
• Line 12: Service URL<br>

💡 Enhancement: Our implementation replaces AndroidLab's rule-based evaluation with LLM-powered assessment, providing more nuanced and accurate task completion evaluation.

### Generate Evaluation Results
Execute result generation with the following command:

```bash
python generate_result.py --input_folder ./logs/evaluation/ --output_folder ./logs/evaluation/ --output_excel ./logs/evaluation/test_name.xlsx
```
### Batch Testing File Management
⚠️ Important: When using batch scripts from ./test_script/:<br>
• Manual Transfer Required: Move generated evaluation files from script directory to ./logs/<br>
• Then Execute: Run the result generation command above<br>
• Error Prevention: This step prevents file path conflicts and ensures proper result compilation<br>

## 🎯 Evaluation Results

The key findings from our online evaluation on AndroidLab are summarized as follows:

- Open-PhoneAgent, when deployed in a device-cloud collaborative setting, incurs only a relatively small performance drop while effectively reducing the number of cloud model invocations.
- Notably, prompting large models for extended reasoning does not always yield better results—this benefit depends on the capability of the cloud model, and only sufficiently strong models can take advantage of such strategies.
- We also report a comparison between LightAgent-3B and both similar-sized and larger models (such as 9B models), showing that LightAgent-3B achieves performance close to that of 9B models, making it a true "small powerhouse."
- Furthermore, when compared with closed-source models, LightAgent-3B's performance is comparable to previous or lightweight versions of these proprietary models.

<p align="center">
  <img src="./figures/three_subplots_corrected.png" width="90%"/>
</p>

For each MLLM, we measure the average total steps required to complete tasks, the proportion of steps handled by the on-device model versus the cloud model, and the average steps when using only the cloud model to quantify the reduction in cloud calls. The main results are as follows:

- The cloud model is still responsible for about 65% of the steps, mainly due to the limited capacity of the smaller on-device model.
- Introducing the on-device model leads to approximately a 10% reduction in cloud calls.
- Stronger cloud models (such as GLM-4.5V) experience a smaller reduction in cloud calls, as they are capable of solving more tasks independently without relying on the on-device model.

<p align="center">
  <img src="./figures/device_cloud_per.png" width="49%"/>
  <img src="./figures/device_cloud_reduce.png" width="47%"/>
</p>

We evaluate the average inference time per step using vLLM under different GPU setups. GLM-4.1V-9B-Thinking could not run on a single 3090 GPU due to context length limits, so only two-GPU results are shown.

LightAgent, thanks to its lightweight architecture, demonstrates a clear advantage in inference speed, making it more suitable for real-world on-device scenarios. This advantage becomes even more pronounced as computational resources become constrained. In contrast, although GLM-4.1V-9B-Thinking achieves higher performance, its inference time on two 3090s is 3.5 times that of LightAgent on a single 3090, and 4 times that of LightAgent on two 3090s. Its inability to run on a single 3090 further limits its feasibility for on-device deployment.

<div align="center">

| Model                  | GPUs        | Size | SR   | Time Cost / Step |
| ---------------------- | ----------- | ---- | ---- | ---------------- |
| Qwen2.5-VL-7B-Instruct | Single 3090 | 7B   | 10.1 | 6289.15 ms       |
| LightAgent             | Single 3090 | 3B   | 15.2 | 4170.63 ms       |
| GLM-4.1V-9B-Thinking   | Two 3090s   | 9B   | 24.6 | 14584.89 ms      |
| Qwen2.5-VL-7B-Instruct | Two 3090s   | 7B   | 10.1 | 4587.79 ms       |
| LightAgent             | Two 3090s   | 3B   | 15.2 | 3524.25 ms       |

</div>
</p>

## 🌟 Citation

If you find this work helpful to your research, please kindly consider citing our paper.

```
@article{jiang2025lightagent,
  title={LightAgent: Mobile Agentic Foundation Models},
  author={Jiang, Yangqin and Huang, Chao},
  journal={arXiv preprint arXiv:2510.22009},
  year={2025}
}
```

## 🔗 Related Projects

Open-PhoneAgent builds upon excellent open-source projects. We sincerely thank their authors and contributors:

- [AndroidLab](https://github.com/THUDM/Android-Lab) - The benchmark framework.
- [R1-V](https://github.com/StarsfieldAI/R1-V) - Implementation details for the GRPO training methodology.
- [LLaMA Factory](https://github.com/hiyouga/LLaMA-Factory) - The unified training framework enabling efficient model fine-tuning.

## 📜 License

This project is released under the [MIT License](./LICENSE).


<br>

<p align="center">
  <em> ❤️ Thanks for visiting ✨ Open-PhoneAgent!</em><br><br>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.Open-PhoneAgent&style=for-the-badge&color=00d4ff" alt="Views">
</p>


