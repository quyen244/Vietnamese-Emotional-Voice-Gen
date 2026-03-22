from pathlib import Path
import logging 
from datetime import datetime


def _setup_logging(outputPath : str , purpose : str):
        """Thiết lập logging ghi ra cả console và file. \n
            outputPath : str : đường dẫn đầu ra \n
            purpose : str : log cho ai , đối tượng nào 
        """
        log_dir = Path("{outputPath}")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"{purpose}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logger = logging.getLogger(f"{purpose}")
        logger.setLevel(logging.INFO)

        # Định dạng log: Thời gian - Mức độ - Thông điệp
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # File Handler: Ghi vào tệp
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # Stream Handler: Ghi ra màn hình Terminal
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        return logger