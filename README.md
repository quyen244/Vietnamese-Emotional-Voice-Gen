
<p align="center">
  <a href="https://www.uit.edu.vn/" title="University of Information Technology" style="border: none;">
    <img src="https://i.imgur.com/WmMnSRt.png" alt="University of Information Technology (UIT)">
  </a>
</p>

<h1 align="center"><b>Vn-EmoVoice: Emotional Vietnamese TTS System</b></h1>
# **Personal Project: Vn-EmoVoice (VEV)**

> **Vn-EmoVoice** là một hệ thống chuyển đổi văn bản thành giọng nói (Text-to-Speech) chuyên sâu cho tiếng Việt, tập trung vào khả năng tái tạo cảm xúc và sắc thái biểu cảm tự nhiên. Thay vì giọng đọc robot đơn điệu, hệ thống sử dụng công nghệ Fine-tuning trên mô hình **GPT-SoVITS** với tập dữ liệu đặc thù từ Podcast và Truyện ma, giúp tạo ra các nội dung lồng tiếng có hồn, phục vụ cho sáng tạo nội dung số, audiobook và trợ lý ảo thông minh.

\<p align="center"\>
\<img src="[https://raw.githubusercontent.com/RVC-Boss/GPT-SoVITS/main/docs/en/img/inference\_webui.png](https://www.google.com/search?q=https://raw.githubusercontent.com/RVC-Boss/GPT-SoVITS/main/docs/en/img/inference_webui.png)" width="600" alt="VEV System Preview"\>
\</p\>

**Technical Highlights:**

  * **Core Architecture:** Sử dụng **GPT-SoVITS** (Few-shot Voice Conversion & TTS).
  * **Data Processing:** Pipeline tự động tách giọng (**UVR5**) và gán nhãn văn bản (**Faster-Whisper**).
  * **Fine-tuning:** Kỹ thuật **Transfer Learning** trên tập dataset tiếng Việt đa sắc thái (Vui, Buồn, Giận dữ, Kinh dị).
  * **Audio Optimization:** Quy trình xử lý nhiễu và chuẩn hóa âm thanh studio-quality.
  * **Deployment:** Giao diện WebUI tương tác trực quan để tùy chỉnh độ dài, tốc độ và cảm xúc giọng đọc.

-----

## **Team Information**

| No. | Student ID | Full Name | Role | Github | Email |
| --- | --- | --- | --- | --- | --- |
| 1 | 23521329 | Nguyen Van Quyen | AI Research & Dev | [quyen244](https://github.com/quyen244) | 23521329@gm.uit.edu.vn |

-----

## **Table of Contents**

  * [Overview](#overview)
  * [System Architecture](#system-architecture)
  * [Data Pipeline](#data-pipeline)
  * [Repository Structure](#repository-structure)
  * [Tech Stack](#tech-stack)
  * [Features](#features)
  * [Installation & Usage](#installation--usage)
  * [Future Work](#future-work)

-----

## **Overview**

### **Problem Statement**

Hiện nay, các hệ thống TTS tiếng Việt phổ biến thường gặp vấn đề về sự thiếu hụt cảm xúc (flat prosody), khiến người nghe cảm thấy nhàm chán khi nghe các nội dung dài như truyện audio hoặc podcast. Việc tạo ra một giọng đọc có khả năng nhấn nhá, biểu đạt cảm xúc hỉ-nộ-ái-ố vẫn là một thách thức lớn.

### **Solution**

**Vn-EmoVoice** giải quyết vấn đề này thông qua việc xây dựng một bộ Dataset "cảm xúc" từ các nguồn thực tế và ứng dụng mô hình sinh giọng nói thế hệ mới:

1.  **Emotion Cloning:** Sao chép phong cách đọc từ các nghệ sĩ lồng tiếng chuyên nghiệp.
2.  **Zero-shot/Few-shot Learning:** Chỉ cần 5-10 giây giọng mẫu để tạo ra một giọng đọc mới.
3.  **Cross-lingual Support:** Khả năng đọc xen kẽ Anh-Việt tự nhiên.

-----

## **System Architecture**

```text
┌─────────────────────────────────────────────────────────────┐
│                   Input Layer (Text / Prompt)                │
│            (Input Script + Reference Audio Emotion)         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              Preprocessing & Feature Extraction             │
│   - Semantic Tokenization (BERT Vietnamese)                  │
│   - Acoustic Feature Extraction (HuBERT)                    │
└────────────────────┬──────────────────────────────────────┬─┘
                     │                                      │
    ┌────────────────▼──────────────┐      ┌────────────────▼──────────────┐
    │    Autoregressive GPT Stage   │      │    VITS Diffusion Stage       │
    │ - Predict Semantic Tokens     │      │ - Latent Space Transformation │
    │ - Emotion & Tone Control      │      │ - Waveform Synthesis          │
    └────────────────┬──────────────┘      └────────────────┬──────────────┘
                     │                                      │
    ┌────────────────▼──────────────────────────────────────▼──────────────┐
    │                    Output: Natural Emotional Audio                   │
    └──────────────────────────────────────────────────────────────────────┘
```

-----
## **Repository Structure**

```text
.
├── data/                       # Dữ liệu huấn luyện
│   ├── raw/                    # Audio thô từ YouTube/Podcast (wav, mp3)
│   ├── processed/              # Audio đã qua xử lý (Vocal only)
│   └── segments/               # Audio đã cắt nhỏ (3s-10s) + file list.txt
├── tools/                      # Bộ công cụ tiền xử lý
│   ├── uvr5/                   # Ultimate Vocal Remover (tách nhạc nền)
│   ├── whisper/                # Faster-Whisper (tự động tạo transcript)
│   └── audio_slicer.py         # Script cắt audio dựa trên khoảng lặng
├── GPT_SoVITS/                 # Mã nguồn chính của mô hình (Core)
│   ├── AR/                     # Autoregressive Transformer (tầng GPT)
│   ├── VITS/                   # Variational Inference (tầng SoVITS)
│   └── pretrained_models/      # Trọng số pre-trained mặc định
├── logs/                       # Lưu trữ checkpoints trong quá trình train
│   ├── my_emotional_voice_v1/  # Checkpoint của model bạn fine-tune
│   └── train_logs/             # Tensorboard logs
├── src/                        # Mã nguồn ứng dụng
│   ├── inference.py            # Script chạy sinh giọng nói (CLI)
│   └── app_gradio.py           # Giao diện WebUI (Gradio)
├── requirements.txt            # Danh sách thư viện cần thiết
├── .env                        # Biến môi trường (Config đường dẫn)
└── webui.py                    # Entry point để khởi chạy hệ thống
```

---


## **Data Pipeline**

Hệ thống được huấn luyện qua quy trình xử lý dữ liệu nghiêm ngặt:

1.  **Crawl:** Thu thập Audio từ các kênh Podcast/Truyện ma uy tín (1 speaker).
2.  **Vocal Separation:** Sử dụng **UVR5 (MDX-Net)** để loại bỏ nhạc nền và tiếng vang.
3.  **Segmentation:** Cắt audio thành các đoạn ngắn 3s-10s dựa trên khoảng lặng.
4.  **Transcription:** Dùng **Faster-Whisper (Large-v3)** để chuyển audio thành text chính xác 99%.
5.  **Labeling:** Gán nhãn cảm xúc thủ công để tăng cường độ chính xác khi inference.

-----

## **Tech Stack**

| Category | Technology |
| --- | --- |
| **Model Architecture** | GPT-SoVITS |
| **Audio Processing** | UVR5, FFmpeg, Librosa |
| **Speech-to-Text** | OpenAI Faster-Whisper |
| **NLP** | PhoBERT (Vietnamese Semantic Support) |
| **Backend/GUI** | Python, Gradio |
| **Infrastructure** | PyTorch, CUDA 12.x |

-----

## **Features**

  * ✅ **Emotion Control**: Tùy chỉnh giọng đọc theo mood (Dramatice, Calm, Scary, etc).
  * ✅ **Voice Cloning**: Clone bất kỳ giọng nói nào chỉ với sample ngắn.
  * ✅ **High-speed Inference**: Tối ưu hóa pipeline để sinh audio thời gian thực trên GPU tầm trung.
  * ✅ **Noise Robustness**: Khả năng xử lý tốt các tệp âm thanh đầu vào có lẫn tạp âm nhẹ.
  * ✅ **English-Vietnamese Mixing**: Xử lý mượt mà các câu văn chứa thuật ngữ tiếng Anh.

-----

## **Installation & Usage**

### **1. Clone & Environment**

```bash
git clone https://github.com/quyen244/Vietnamese-Emotional-Voice-Gen.git
cd Vietnamese-Emotional-Voice-Gen
conda create -n emovoice python=3.9
conda activate emovoice
pip install -r requirements.txt
```

### **2. Pre-trained Models**

Tải các trọng số (weights) của GPT-SoVITS và bỏ vào thư mục `GPT_SoVITS/pretrained_models`.

### **3. Run WebUI**

```bash
python webui.py
```

-----

## **Contact**

  * **Developer**: Nguyen Van Quyen
  * **Github**: [@quyen244](https://github.com/quyen244)
  * **Project Status**: 🛠️ Development Phase (Fine-tuning in progress)

**Last Updated**: March 2026

