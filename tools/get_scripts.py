import os
import logging
from pathlib import Path
from faster_whisper import WhisperModel
from tqdm import tqdm
import torch

# Sử dụng logger đã setup của bạn
from utils.logger import _setup_logging
logger = _setup_logging(outputPath='transcription.log', purpose='Speech-to-Text')

class TranscriptionPipeline:
    def __init__(self, model_size="large-v3", device="cuda"):
        """
        Khởi tạo Whisper Model. 
        Sử dụng float16 trên GPU để tối ưu tốc độ và bộ nhớ.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing Faster-Whisper {model_size} on {self.device}")
        
        # compute_type="float16" giúp chạy cực nhanh trên GPU NVIDIA
        self.model = WhisperModel(
            model_size, 
            device=self.device, 
            compute_type="float16" if self.device == "cuda" else "int8"
        )

    def run(self, chunks_root, output_file, speaker_name="VoTong"):
        """
        Quét toàn bộ thư mục chunks và tạo file list.txt
        Format: path|speaker|language|text
        """
        chunks_root = Path(chunks_root)
        all_wavs = list(chunks_root.rglob("*.wav")) # Quét tất cả folder con
        
        if not all_wavs:
            logger.warning(f"No wav files found in {chunks_root}")
            return

        logger.info(f"Found {len(all_wavs)} chunks. Starting transcription...")
        
        with open(output_file, "w", encoding="utf-8") as f:
            for wav_path in tqdm(all_wavs, desc="Transcribing"):
                try:
                    # Chạy Transcription
                    # beam_size=5: Tăng độ chính xác
                    # vad_filter=True: Loại bỏ các đoạn nhiễu không phải tiếng người
                    segments, info = self.model.transcribe(
                        str(wav_path), 
                        beam_size=5, 
                        language="vi", 
                        vad_filter=True
                    )
                    
                    text = "".join([segment.text for segment in segments]).strip()
                    
                    if not text:
                        continue # Bỏ qua nếu không nhận diện được chữ nào

                    # Format chuẩn GPT-SoVITS: path|speaker|language|text
                    # Lưu ý: Nên dùng đường dẫn tương đối hoặc tuyệt đối chuẩn xác
                    line = f"{wav_path.resolve()}|{speaker_name}|vi|{text}\n"
                    f.write(line)
                    
                except Exception as e:
                    logger.error(f"Failed to transcribe {wav_path.name}: {e}")

        logger.info(f"Transcription finished! Dataset list saved to: {output_file}")

# --- Cách tích hợp vào main của bạn ---
if __name__ == "__main__":
    # Đường dẫn thư mục chunks bạn vừa tạo ở bước trước
    CHUNKS_DIR = "data/processed/chunks"
    OUTPUT_LIST = "data/processed/list.txt"
    
    transcriber = TranscriptionPipeline(model_size="large-v3")
    transcriber.run(CHUNKS_DIR, OUTPUT_LIST, speaker_name="Nikola_Tesla")