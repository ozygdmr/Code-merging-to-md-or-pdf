import os
from fpdf import FPDF

# Taranacak kod ve yapılandırma uzantıları
ALLOWED_EXTENSIONS = {
    '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.scss',
    '.c', '.cpp', '.h', '.java', '.json', '.sql', '.sh', '.yaml', 
    '.yml', '.xml', '.toml', '.ini', '.conf', '.md', '.txt'
}

# Uzantısı olmayan ama taranması gereken özel dosyalar
ALLOWED_EXACT_NAMES = {
    'Dockerfile', 'Makefile', '.gitignore', '.dockerignore', '.eslintrc', '.prettierrc'
}

# Yoksayılacak gereksiz/sistem klasörleri
IGNORE_DIRS = {
    'node_modules', '.git', '__pycache__', 'venv', '.venv', 'dist', 'build', '.next'
}

# Kendi ürettiği çıktı dosyalarını tekrar taramaması için hariç tutulanlar
IGNORE_FILES = {
    'proje_kodlari.md', 'proje_kodlari.pdf', 'package-lock.json', 'yarn.lock'
}

def is_target_file(filename):
    if filename in IGNORE_FILES:
        return False
    # .env, .env.local, .env.production gibi tüm env dosyalarını yakalar
    if filename == '.env' or filename.startswith('.env.'):
        return True
    if filename in ALLOWED_EXACT_NAMES:
        return True
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def collect_code(root_dir):
    collected_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Yoksayılan klasörleri yerinde filtrele (gizli klasörler dahil taranır, sadece listedekiler atlanır)
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        
        for filename in sorted(filenames):
            if is_target_file(filename):
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_dir)
                ext = os.path.splitext(filename)[1].lower()
                lang = ext[1:] if ext else "text"
                
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    collected_files.append((rel_path, lang, content))
                    print(f"Bulundu: {rel_path}")
                except Exception as e:
                    print(f"Okunamadı ({rel_path}): {e}")

    if not collected_files:
        print("\nBelirtilen klasör ve alt klasörlerinde uygun dosya bulunamadı.")
        return
    output_name = input("\n Dosya Çıktı Adını Giriniz (Varsayılan: proje_kodlari): ").strip()
    if not output_name:
        output_name = "proje_kodlari"
    output_md = os.path.join(".", f"{output_name}.md")
    output_pdf = os.path.join(".", f"{output_name}.pdf")

    # 1. Markdown Çıktısı
    with open(output_md, 'w', encoding='utf-8') as md_file:
        for rel_path, lang, content in collected_files:
            md_file.write(f"==================================================\n")
            md_file.write(f"DOSYA YOLU: {rel_path}\n")
            md_file.write(f"==================================================\n")
            md_file.write(f"```{lang}\n{content}\n```\n\n")

    # 2. PDF Çıktısı
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Courier", size=9)

    for rel_path, _, content in collected_files:
        pdf.set_font("Courier", style="B", size=11)
        safe_path = rel_path.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 10, f"=== DOSYA: {safe_path} ===", ln=True)
        
        pdf.set_font("Courier", size=8)
        safe_content = content.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 4, safe_content)
        pdf.ln(5)

    pdf.output(output_pdf)
    print(f"\nTamamlandı! Toplam {len(collected_files)} dosya işlendi.")
    print(f"-> {output_md}")
    print(f"-> {output_pdf}")

if __name__ == "__main__":
    girilen_yol = input("Taranacak ana klasörün yolunu girin: ").strip()
    girilen_yol = girilen_yol.strip('"').strip("'")
    
    if os.path.isdir(girilen_yol):
        collect_code(girilen_yol)
    else:
        print("Hata: Geçerli bir klasör yolu girmediniz!")