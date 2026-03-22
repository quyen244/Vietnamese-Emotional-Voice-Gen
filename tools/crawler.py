import yt_dlp
from pathlib import Path
from utils.logger import _setup_logging
from utils.read_txtfile import get_data_fromtxt
import argparse
import os 

class YoutubeCrawler:
    def __init__(self, root_dir: str):
        """
        Khởi tạo Crawler với thư mục gốc và cấu hình Logging.
        :param root_dir: Thư mục lưu trữ chính (ví dụ: 'data/raw')
        """
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)
        
        # Thiết lập logger
        self.logger = _setup_logging(outputPath="logs/crawler" , purpose='YoutubeCrawler')
        self.logger.info("--- Khởi tạo YoutubeCrawler thành công ---")

    def _progress_hook(self, d):
        """Hook để theo dõi tiến độ download của yt-dlp."""

        if d['status'] == 'downloading':
            self.logger.info(f"Đang tải: {d.get('_percent_str', '0%')} - Tốc độ: {d.get('_speed_str', 'N/A')}")
        elif d['status'] == 'finished':
            self.logger.info(f"Hoàn tất tải xuống: {d['filename']}")

    def get_data(self, url: str, topic: str , name : str):
        """
        Tải Audio từ YouTube dựa trên URL và phân loại theo Topic.
        :param url: Đường dẫn video hoặc playlist YouTube.
        :param topic: Tên chủ đề (để tạo thư mục con).
        """
        save_path = os.path.join(self.root , topic , name)
        os.makedirs(name=save_path , exist_ok= True)
   
        self.logger.info(f"Bắt đầu tiến trình cho Topic: [{topic}] | URL: {url} Name : {name}")

        # Cấu hình yt-dlp cho Audio Extraction
        ydl_opts = {
            'format': 'bestaudio/best',      # Lấy chất lượng âm thanh tốt nhất
            'outtmpl': f'{save_path}/%(title)s.%(ext)s', # Quy tắc đặt tên file
            'postprocessors': [{             # Chuyển đổi sang định dạng wav
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'logger': self.logger,           # Gắn logger của mình vào yt-dlp
            'progress_hooks': [self._progress_hook],
            'ignoreerrors': True,            # Bỏ qua nếu có 1 video trong playlist lỗi
            'restrictfilenames': True,       # Đặt tên file không chứa ký tự đặc biệt
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.logger.info(f"Đang trích xuất thông tin từ: {url}")
                ydl.download([url])
        except Exception as e:
            self.logger.error(f"Lỗi nghiêm trọng khi crawl topic {topic}: {str(e)}")
        finally:
            self.logger.info(f"Kết thúc tiến trình cho Topic: {topic}")

def get_parse():
    parser = argparse.ArgumentParser(description= "Crawling data with topic")
    parser.add_argument('--topic' , help= 'Enterting the topic' , default= 'knowledge')

    return parser.parse_args()

# --- Ví dụ sử dụng (Demo) ---
if __name__ == "__main__":
    crawler = YoutubeCrawler(root_dir="data/raw")

    parser = get_parse()

    data = get_data_fromtxt(path=r'D:\Projects\Assignment\LLM & AI Assistant Projects\Voice-Gen\tools\playlist.txt')
    
    for item in data['topics'][f"{parser.topic}"]['authors']:
        for url in item['urls']:
            crawler.get_data(url=url, topic=parser.topic, name=item['name'])
    
# py -m tools.crawler / --topic philosophy 