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
        """
        Bước 2.2: Tách lời và khử vang (2 giai đoạn)
        """
        input_path = Path(input_path)
        final_vocal_dir = self.output_root / "clean_vocals"
        final_vocal_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Giai đoạn 1: Tách nhạc nền (MDX-Net)
            logger.info(f"Stage 1: Separating Vocals/BGM for {input_path.name}")
            self.separator.load_model("UVR-MDX-NET-Voc_FT.onnx")
            output_files = self.separator.separate(str(input_path))
            vocal_file_path = [f for f in output_files if "Vocals" in f][0]
            vocal_full_path = self.output_root / "tmp" / vocal_file_path

            # Giai đoạn 2: Khử vang (DeEcho-DeReverb)
            logger.info(f"Stage 2: De-reverberating {vocal_file_path}")
            self.separator.load_model("UVR-DeEcho-DeReverb.onnx")
            dry_vocal_files = self.separator.separate(str(vocal_full_path))
            dry_vocal_name = [f for f in dry_vocal_files if "No Echo" in f or "Vocals" in f][0]
            
            # Di chuyển file cuối cùng ra thư mục chính thức
            final_path = final_vocal_dir / f"{input_path.stem}_dry.wav"
            os.replace(self.output_root / "tmp" / dry_vocal_name, final_path)
            
            logger.info(f"Vocal separation completed: {final_path}")
            return final_path
        except Exception as e:
            logger.error(f"Error in vocal separation for {input_path}: {e}")
            return None

    def slice_audio(self, vocal_path, min_duration=3000, max_duration=10000):
        """
        Bước 2.3: Cắt nhỏ audio dựa trên khoảng lặng (Silence Detection)
        min_duration: ms (3s), max_duration: ms (10s)
        """
        if not vocal_path: return
        
        vocal_path = Path(vocal_path)
        chunk_dir = self.output_root / "chunks" / vocal_path.stem
        chunk_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Slicing audio: {vocal_path.name}")
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
            # Chỉ giữ các đoạn từ 3s đến 10s
            if min_duration <= duration <= max_duration:
                chunk_name = f"{vocal_path.stem}_chunk_{count:03d}.wav"
                chunk.export(chunk_dir / chunk_name, format="wav")
                count += 1
            
            # Nếu đoạn quá dài, ta có thể cắt cưỡng bức (optional)
            elif duration > max_duration:
                for j in range(0, duration, max_duration):
                    sub_chunk = chunk[j:j+max_duration]
                    if len(sub_chunk) >= min_duration:
                        chunk_name = f"{vocal_path.stem}_chunk_{count:03d}.wav"
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
            
            if clean_vocal:
                pipeline.slice_audio(clean_vocal)


    # py -m tools.bg_remover