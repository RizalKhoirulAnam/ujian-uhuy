import json
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional

class HSKHTMLToJSONConverter:
    """Class untuk mengonversi HTML kosakata HSK ke JSON secara efisien"""
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
    
    def convert_large_file(self, html_file_path: str, output_json_path: str, batch_size: int = 1000):
        """
        Mengonversi file HTML besar secara batch untuk menghemat memory
        
        Args:
            html_file_path: Path ke file HTML
            output_json_path: Path output JSON
            batch_size: Jumlah item per batch
        """
        print(f"Memproses file besar: {html_file_path}")
        
        # Baca file dalam chunks untuk menghemat memory
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        li_elements = soup.find_all('li', attrs={'data-chapter': True})
        
        total_elements = len(li_elements)
        print(f"Ditemukan {total_elements} elemen kosakata")
        
        # Proses dalam batch
        all_vocabulary = []
        
        for i in range(0, total_elements, batch_size):
            batch = li_elements[i:i + batch_size]
            batch_vocabulary = self._process_batch(batch)
            all_vocabulary.extend(batch_vocabulary)
            
            print(f"Diproses: {min(i + batch_size, total_elements)}/{total_elements}")
        
        # Simpan ke JSON
        self._save_to_json(all_vocabulary, output_json_path)
        
        print(f"Selesai! Berhasil: {self.processed_count}, Gagal: {self.error_count}")
    
    def _process_batch(self, batch: List) -> List[Dict]:
        """Proses batch elemen"""
        batch_vocabulary = []
        
        for li in batch:
            try:
                vocab_data = self._extract_vocabulary_data(li)
                if vocab_data:
                    batch_vocabulary.append(vocab_data)
                    self.processed_count += 1
            except Exception as e:
                self.error_count += 1
                continue
        
        return batch_vocabulary
    
    def _extract_vocabulary_data(self, li_element) -> Optional[Dict]:
        """Ekstrak data dari elemen <li>"""
        # Ekstrak chapter
        chapter = li_element.get('data-chapter', '').strip()
        
        # Cari elemen yang diperlukan
        hsk_card = li_element.find('h4', class_='hsk-card')
        if not hsk_card:
            return None
        
        # Ekstrak karakter Chinese
        simplified = self._extract_text(hsk_card, 'span[data-simplified]')
        traditional = self._extract_text(hsk_card, 'span[data-traditional]')
        
        # Ekstrak dari dialog
        hsk_dialog = li_element.find('div', class_='hsk-dialog')
        if not hsk_dialog:
            return None
        
        pinyin = self._extract_text(hsk_dialog, 'strong.pinyin')
        english = self._extract_text(hsk_dialog, 'p.en')
        indonesian = self._extract_text(hsk_dialog, 'p.id')
        chapter_number = self._extract_text(hsk_dialog, 'small') or chapter
        
        return {
            'chapter': self._clean_text(chapter),
            'chapter_number': self._clean_text(chapter_number),
            'simplified': self._clean_text(simplified),
            'traditional': self._clean_text(traditional),
            'pinyin': self._clean_text(pinyin),
            'english': self._clean_text(english),
            'indonesian': self._clean_text(indonesian)
        }
    
    def _extract_text(self, element, selector: str) -> str:
        """Ekstrak teks dari selector"""
        found = element.select_one(selector)
        return found.text.strip() if found else ''
    
    def _clean_text(self, text: str) -> str:
        """Bersihkan teks dari whitespace berlebih"""
        return re.sub(r'\s+', ' ', text).strip()
    
    def _save_to_json(self, data: List[Dict], output_path: str):
        """Simpan data ke file JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# Contoh penggunaan untuk file besar
if __name__ == "__main__":
    converter = HSKHTMLToJSONConverter()
    
    # Untuk file dengan 20k+ rows
    converter.convert_large_file(
        html_file_path="hsk_vocabulary.html",
        output_json_path="hsk6_vocabulary.json",
        batch_size=2000  # Sesuaikan dengan memory yang tersedia
    )