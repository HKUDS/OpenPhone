<div align="center">
  <picture>
      <img src="./figures/phoneagent_logo.png" width="20%" style="border: none; box-shadow: none;">
  </picture>
</div >

<div align="center">

# ✨OpenPhone✨: Mobile Agentic Foundation Models for AI Phone

</div>

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Orbitron&size=24&duration=3000&pause=1000&color=00D9FF&center=true&vCenter=true&width=600&lines=Welcome+to+OpenPhone;Mobile+Agentic+Foundation+Models;AI+Phone" alt="Typing Animation" />
</div>

<div align="center">
  <img src="./demo/lightagent_demo.gif" width="800" height="400" alt="演示动画">
</div>

<div align="center">
  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 25px; text-align: center;">
    <p>
      <a href='https://github.com/HKUDS/OpenPhone'><img src='https://img.shields.io/badge/🔥Project-Page-00d9ff?style=for-the-badge&logo=github&logoColor=white&labelColor=1a1a2e'></a>
      <a href="https://huggingface.co/datasets/hkuds/OpenPhone_dataset"><img alt="Hugging Face" src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-ffc107?style=for-the-badge&color=ffc107&logoColor=white&labelColor=1a1a2e"/></a>
      <a href="https://huggingface.co/hkuds/OpenPhone_model"><img alt="Hugging Face" src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Model-ffc107?style=for-the-badge&color=ffc107&logoColor=white&labelColor=1a1a2e"/></a>
      <a href='https://github.com/THUDM/Android-Lab'><img src='https://img.shields.io/badge/⚡Based%20on-AndroidLab-4ecdc4?style=for-the-badge&logo=lightning&logoColor=white&labelColor=1a1a2e'></a>
    </p>
    <p>
      <a href="https://github.com/HKUDS/OpenPhone/stargazers"><img src='https://img.shields.io/github/stars/HKUDS/OpenPhone?color=00d9ff&style=for-the-badge&logo=star&logoColor=white&labelColor=1a1a2e' /></a>
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

## 🎯 What is OpenPhone?

**The Problem**: Most AI agents rely on expensive cloud APIs and large models that are impractical for real-world on-device deployment. Users face **Privacy Concerns**, **Latency Issues**, and **High Costs** when their phone needs to call external services for every interaction.

**Our Solution**: OpenPhone introduces the first **Open-Source, 3B-parameter Agentic Foundation Model** designed specifically for on-device smartphone interaction. This compact vision-language model runs entirely locally — meaning **No Privacy Concerns**, **No Cloud Dependence**, and **Zero API Costs**.

## 🤔 Why 3B Parameters?
We believe the future of mobile AI lies not only in making models larger, but in making them smarter and more efficient for real-world constraints. Our 3B model is:
- ⚡ **Edge-Optimized**: Efficient enough for commodity GPUs and next-generation mobile NPUs.
- 🔒 **Privacy-First**: All computation stays on your device.
- 💰 **Cost-Free**: No cloud inference and no ongoing API fees.
- 🎯 **High-Performance**: Achieves performance comparable to 7B–9B models through advanced training.

---

## 💡 Research Highlights

### 🔍 OpenPhone‑3B: Lightweight Agentic Model
Considering the compute limitations of today’s edge devices, models with **≤3B parameters** strike a practical balance between capability and deployability. Based on this insight, we introduce **OpenPhone‑3B**, a lightweight yet powerful on‑device agent model.

- **Model Size & Architecture**: Vision-language model engineered for efficient on-device reasoning under tight mobile compute constraints.
- **Edge-Native Design**: Primary local agent compatible with consumer GPUs and mobile NPUs, eliminating continuous cloud dependency.
- **GUI‑Aware Action Capabilities**: Trained for visual interpretation, instruction following, and structured action generation across real mobile tasks.
- **Open‑Source Release**: Full model weights, configurations, and inference stack enabling community deployment and development.
- **Practical Sweet Spot**: 3B scale delivers optimal balance—significantly stronger than tiny models while remaining deployable where larger models fail.

### Why 3B is the Sweet Spot for Phone Agents
- **Hardware Fit**: 3B parameters align perfectly with consumer GPU memory (8-12GB) and emerging mobile NPU computational budgets.
- **Speed Advantage**: 3B models deliver 3-5x faster inference than 7B alternatives while maintaining competitive accuracy for sub-second GUI responses.
- **Power Efficiency**: Smaller footprint extends battery life - essential for mobile deployment where power consumption affects user experience.
- **Privacy-First**: Enables phone tasks to run entirely on-device, preserving user privacy while eliminating network dependencies.
- **Cost Savings**: Local processing eliminates expensive cloud APIs and per-request charges for sustainable operation.

---

## 🚀 Model Release & Resources

### 📦 Ready-to-Deploy Model

- **Model Weights**: OpenPhone-3B is available on Hugging Face with full licensing for research and commercial use.
- **Production-Ready Serving**: Pre-configured vLLM inference scripts enable efficient deployment with optimized throughput and memory usage.

### 🛠️ Complete Training Pipeline
- **Reproducible Recipe**: Full training implementation including our novel two-stage approach (SFT + GRPO-style RL with synthetic GUI data).
- **Customization Support**: Detailed documentation in model_training/allows researchers to adapt the model for domain-specific phone tasks or extend to new mobile platforms.
- **Data Generation Paradigm**: Scripts and methodologies for creating high-quality training data at scale.

---

## 📖 Table of Contents
- [✨OpenPhone✨: Mobile Agentic Foundation Models for AI Phone](#openphone-mobile-agentic-foundation-models-for-ai-phone)
  - [🎯 What is OpenPhone?](#-what-is-openphone)
  - [💡 Research Highlights](#-research-highlights)
    - [🔍 OpenPhone‑3B: Lightweight Agentic Model](#-openphone3b-lightweight-agentic-model)
    - [Why 3B is the Sweet Spot for Phone Agents](#why-3b-is-the-sweet-spot-for-phone-agents)
  - [🚀 Model Release \& Resources](#-model-release--resources)
    - [📦 Ready-to-Deploy Model](#-ready-to-deploy-model)
    - [🛠️ Complete Training Pipeline](#️-complete-training-pipeline)
  - [📖 Table of Contents](#-table-of-contents)
  - [🌟 Key Features of OpenPhone](#-key-features-of-openphone)
    - [🤖 Lightweight Agentic Foundation Models](#-lightweight-agentic-foundation-models)
    - [☁️ Device-Cloud Collaboration Framework](#️-device-cloud-collaboration-framework)
    - [🎯 Comprehensive Mobile Agent Evaluation Playground](#-comprehensive-mobile-agent-evaluation-playground)
  - [🌟 Technical Innovation \& Implementation](#-technical-innovation--implementation)
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

## 🌟 Key Features of OpenPhone

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

## 🌟 Technical Innovation & Implementation

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
- OpenPhone Weights: 3B parameter model hosted on HuggingFace<br>
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

- OpenPhone, when deployed in a device-cloud collaborative setting, incurs only a relatively small performance drop while effectively reducing the number of cloud model invocations.
- Notably, prompting large models for extended reasoning does not always yield better results—this benefit depends on the capability of the cloud model, and only sufficiently strong models can take advantage of such strategies.
- We also report a comparison between OpenPhone-3B and both similar-sized and larger models (such as 9B models), showing that OpenPhone-3B achieves performance close to that of 9B models, making it a true "small powerhouse."
- Furthermore, when compared with closed-source models, OpenPhone-3B's performance is comparable to previous or lightweight versions of these proprietary models.

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

OpenPhone, thanks to its lightweight architecture, demonstrates a clear advantage in inference speed, making it more suitable for real-world on-device scenarios. This advantage becomes even more pronounced as computational resources become constrained. In contrast, although GLM-4.1V-9B-Thinking achieves higher performance, its inference time on two 3090s is 3.5 times that of OpenPhone on a single 3090, and 4 times that of OpenPhone on two 3090s. Its inability to run on a single 3090 further limits its feasibility for on-device deployment.

<div align="center">

| Model                  | GPUs        | Size | SR   | Time Cost / Step |
| ---------------------- | ----------- | ---- | ---- | ---------------- |
| Qwen2.5-VL-7B-Instruct | Single 3090 | 7B   | 10.1 | 6289.15 ms       |
| OpenPhone              | Single 3090 | 3B   | 15.2 | 4170.63 ms       |
| GLM-4.1V-9B-Thinking   | Two 3090s   | 9B   | 24.6 | 14584.89 ms      |
| Qwen2.5-VL-7B-Instruct | Two 3090s   | 7B   | 10.1 | 4587.79 ms       |
| OpenPhone              | Two 3090s   | 3B   | 15.2 | 3524.25 ms       |

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

OpenPhone builds upon excellent open-source projects. We sincerely thank their authors and contributors:

- [AndroidLab](https://github.com/THUDM/Android-Lab) - The benchmark framework.
- [R1-V](https://github.com/StarsfieldAI/R1-V) - Implementation details for the GRPO training methodology.
- [LLaMA Factory](https://github.com/hiyouga/LLaMA-Factory) - The unified training framework enabling efficient model fine-tuning.

## 📜 License

This project is released under the [MIT License](./LICENSE).

<div align="center">

**If this project helps you, please give us a Star🌟**

**🤖 Empower AI Phone with Agents!**

<br>

<p align="center">
  <em> ❤️ Thanks for visiting ✨ OpenPhone!</em><br><br>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.OpenPhone&style=for-the-badge&color=00d4ff" alt="Views">
</p>


