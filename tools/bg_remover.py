import os
from pathlib import Path
from audio_separator.separator import Separator
from pydub import AudioSegment, silence
import librosa
import soundfile as sf
from tqdm import tqdm
from utils.logger import _setup_logging
import argparse

logger = _setup_logging(outputPath= 'audio_processing.log', purpose='Data pre-processing' )

class AudioProductionPipeline:
    def __init__(self, model_dir="models", output_root="data/processed"):
        self.output_root = Path(output_root)
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Khởi tạo Separator
        self.separator = Separator(
            output_dir=str(self.output_root / "tmp"),
            model_file_dir=str(self.model_dir),
            output_format="WAV"
        )

    def separate_vocals(self, input_path):
        input_path = Path(input_path)
        final_vocal_dir = self.output_root / "clean_vocals"
        final_vocal_dir.mkdir(parents=True, exist_ok=True)
        tmp_dir = self.output_root / "tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)

        # Biến tạm để lưu đường dẫn file tốt nhất hiện có
        current_best_vocal = None

        try:
            # --- Giai đoạn 1: Tách nhạc nền (BẮT BUỘC) ---
            logger.info(f"--- Stage 1: Separating Vocals for {input_path.name} ---")
            self.separator.load_model("UVR-MDX-NET-Voc_FT.onnx")
            output_files = self.separator.separate(str(input_path))
            
            vocal_file_name = next((f for f in output_files if "Vocals" in f), None)
            if not vocal_file_name:
                logger.error("Không tách được lời ở Stage 1.")
                return None
            
            current_best_vocal = tmp_dir / vocal_file_name
            logger.info(f"Stage 1 thành công: {vocal_file_name}")

            # --- Giai đoạn 2: Khử vang (TÙY CHỌN - Nếu lỗi vẫn chạy tiếp) ---
            try:
                logger.info(f"--- Stage 2: De-reverberating {vocal_file_name} ---")

                self.separator.load_model("UVR-De-Echo-Normal.onnx") 
                dry_vocal_files = self.separator.separate(str(current_best_vocal))
                
                if dry_vocal_files:
                    current_best_vocal = tmp_dir / dry_vocal_files[0]
                    logger.info("Stage 2 (Khử vang) thành công.")
            except Exception as e_stage2:
                logger.warning(f"Stage 2 lỗi (có thể do thiếu model): {e_stage2}. Sẽ dùng kết quả Stage 1 để Slice.")

            # --- Di chuyển file cuối cùng ra thư mục chính thức ---
            import shutil
            final_path = final_vocal_dir / f"{input_path.stem}_clean.wav"
            
            if current_best_vocal and current_best_vocal.exists():
                shutil.move(str(current_best_vocal), str(final_path))
                logger.info(f"SUCCESS: File sạch đã sẵn sàng tại {final_path}")
                return final_path
            else:
                return None

        except Exception as e:
            logger.error(f"Lỗi nghiêm trọng tại {input_path.name}: {str(e)}")
            return None
    def slice_audio(self, vocal_path, min_duration=3000, max_duration=10000):
        """
        Bước 2.3: Cắt nhỏ audio dựa trên khoảng lặng (Silence Detection)
        min_duration: ms (3s), max_duration: ms (10s)
        """
        if not vocal_path: return
        
        vocal_path = Path(vocal_path)
        
        short_name = f"{vocal_path.stem[:15]}_{vocal_path.stem[-5:]}"
        chunk_dir = self.output_root / "chunks" / short_name
        chunk_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Slicing audio: {vocal_path.name} -> Saving to: {short_name}")
        audio = AudioSegment.from_wav(vocal_path)
        
        # Tự động cắt theo khoảng lặng
        # silence_thresh: dưới -40dB được coi là im lặng
        # min_silence_len: im lặng ít nhất 500ms thì mới cắt
        chunks = silence.split_on_silence(
            audio, 
            min_silence_len=600, 
            silence_thresh=-45, 
            keep_silence=300
        )

        count = 0
        for i, chunk in enumerate(chunks):
            duration = len(chunk)
            if min_duration <= duration <= max_duration:
                chunk_name = f"c_{count:04d}.wav" 
                chunk.export(chunk_dir / chunk_name, format="wav")
                count += 1
            
            elif duration > max_duration:
                for j in range(0, duration, max_duration):
                    sub_chunk = chunk[j:j+max_duration]
                    if len(sub_chunk) >= min_duration:
                        chunk_name = f"c_{count:04d}.wav"
                        sub_chunk.export(chunk_dir / chunk_name, format="wav")
                        count += 1

        logger.info(f"Created {count} valid chunks in {chunk_dir}")

def get_args():
    parser = argparse.ArgumentParser(description='Pre-processing regarding topic')

    parser.add_argument('--mode', default='one')
    parser.add_argument('--topic', default='knowledge')

    return parser.parse_args()

# --- Thực thi Pipeline ---
if __name__ == "__main__":
    pipeline = AudioProductionPipeline()

    args = get_args()
    # get authors
    raw_wav_dir = Path(f"data/raw/{args.topic}")
    authors = list(raw_wav_dir.glob("*"))

    print(f'Current path : {raw_wav_dir.resolve()}')


    for author in tqdm(authors, desc="Getting a author list"):
        files = list(author.glob("*.wav")) 

        for file in tqdm(files, desc="Processing Audio"):
            clean_vocal = pipeline.separate_vocals(file)

            print(f'Path of clean_vocal : {clean_vocal}')
            
            if clean_vocal:
                pipeline.slice_audio(clean_vocal)


    # py -m tools.bg_remover