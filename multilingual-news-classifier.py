import pandas as pd
import numpy as np
from pathlib import Path
import  random
from typing import List, Dict, Tuple
import json


from sympy.integrals.meijerint_doc import category


def create_prject_structure():
    directories = [
        'data/raw',
        'data/processed',
        'models',
        'logs',
        'config'
    ]

    print("Proje yapısı oluşturuluyor.")
    for directory in directories:
        Path(directory).mkdir(parents=True,exist_ok=True)
        print(f"{directory}")

        with open('requirementes.txt', 'w') as f:
            f.write("""torch>=2.0.0
transformers>=4.30.0
pandas>=2.0.0
scikit-learn>=1.2.0
fastapi>=0.100.0
uvicorn>=0.23.0
langdetect>=1.0.9
nltk>=3.8.0
""")

        with open('.gitignore', 'w')as f:
            f.write("""__pycache__/
*.pyc
venv/
.env
data/processed/
models/
*.pth
*.bin
""")
        print("Proje yapısı oluşturuldu.")

def generate_sample_data(num_samples_per_lang: int = 50):

    categories = {
        'tr': ['spor', 'politika', 'teknoloji', 'ekonomi', 'sağlık'],
        'en': ['sports', 'politics', 'technology', 'economy', 'health'],
        'es': ['deportes', 'política', 'tecnología', 'economía', 'salud']
    }

    templates = {
            'tr': {
                'spor': ['{} takım maçı {} kazandı', '{} karşılaşmasında heyecanlı anlar'],
                'politika': ['{} konusunda yeni yasa teklifi', '{} görüşmeleri devam ediyor'],
                'teknoloji': ['{} alanında yeni buluş', '{} teknolojisi geliştirildi'],
                'ekonomi': ['{} piyasasında hareketlilik', '{} verileri açıklandı'],
                'sağlık': ['{} hastalığı için yeni tedavi', '{} sağlık merkezi açıldı']
            },
            'en': {
                'sports': ['{}  team won the match {}', 'Exciting moments in {} game'],
                'politics': ['New law proposal about {}', '{} negotiations continue'],
                'technology': ['New invention in {} field', '{} technology developed'],
                'economy': ['Movement in {} market', '{} data announced'],
                'health': ['New treatment for {} disease', '{} health center opened']
            },
            'es': {
                'deportes': ['El equipo {} ganó el partido {}', 'Momentos emocionantes en el juego {}'],
                'política': ['Nueva propuesta de ley sobre {}', 'Continuán las negociaciones de {}'],
                'tecnología': ['Nuevo invento en el campo {}', 'Tecnología {} desarrollada'],
                'economía': ['Movimiento en el mercado {}', 'Datos de {} anunciados'],
                'salud': ['Nuevo tratamiento para la enfermedad {}', 'Centro de salud {} abierto']
            }
        }

    news_words = {
            'tr': {
                'spor' : ['Fenerbahçe', 'Rizespor', 'Gençlerbirliği', 'Kasımpaşa'],
                'politika' : ['seçim', 'meclis', 'bakanlık', 'cumhurbaşkanı'],
                'teknoloji': ['yapay zeka', 'blockchain', 'nesnelerin interneti', 'büyük veri'],
                'ekonomi': ['dolar', 'euro', 'borsa', 'enflasyon'],
                'sağlık': [ 'covid','grip', 'diyabet', 'kanser']
            },
        'en': {
            'sports': ['Arsenal', 'Manchester United', 'Tottehnam', 'Brighton'],
            'politics': ['election', 'parliament', 'ministry', 'president'],
            'technology': ['artificial intelligence', 'blackchain', 'IoT', 'big data'],
            'economy': ['dollar', 'euro', 'stock market', 'inflation'],
            'health': ['covid','flu', 'disabetes', 'cancer']
        },
        'es': {
            'deportes': ['Real Madrid', 'Barcelona', 'Atlético Madrid', 'Sevilla'],
            'política': ['elección', 'congreso', 'ministerio', 'presidente'],
            'tecnología': ['inteligencia artificial', 'blockchain', 'IoT', 'big data'],
            'economía': ['dólar', 'euro', 'bolsa', 'inflación'],
            'salud': ['covid', 'gripe', 'diabetes', 'cáncer']
        }
    }

    all_data = []

    print("Örnek veri oluşturuluyor.")

    for lang in ['tr', 'en' , 'es']:
        for _ in range(num_samples_per_lang):
            category_key = random.choice(list(categories[lang]))
            category = categories[lang][categories[lang].index(category_key)]

            selected_template = random.choice(templates[lang][category_key])

            word_pool = news_words[lang][category_key]
            fill_word = random.choice(word_pool)

            extra_info = str(random.randint(1, 5)) if selected_template.count('{}') > 1 else ""

            if extra_info:
                text = selected_template.format(fill_word, extra_info)
            else:
                text = selected_template.format(fill_word)
            all_data.append({
                'text': text,
                'category': category,
                'language': lang,
                'category_id': categories[lang].index(category_key)
            })

        df = pd.DataFrame(all_data)

    df.to_csv('data/raw/sample_newa_data.csv', index=False, encoding='utf-8')

    print(f"{len(df)} örnek veri oluşturuldu.")
    print(f"     -Diller: {df['language'].unique()}")
    print(f"     -Kategoriler: {len(df['category'].unique())}")

    return df

def analyze_data(df: pd.DataFrame):
        print("\n Veri Analizi")
        print("=" * 50)

        print(f"\nToplam örenk sayısı: {len(df)}")
        print(f"\nDil dağılımı:")
        lang_dist = df['language'].value_counts()
        for lang, count in lang_dist.items():
            percentage = (count / len(df)) * 100
            print(f" {lang.upper()}: {count} örnek ({percentage: .1f}%)")

        print(f"\nKategori dağılımı (dil bazlı):")
        for lang in df['language'].unique():
            lang_df = df[df['language'] == lang]
            print(f"\n {lang.upper()}:")
            cat_dist = lang_df['category'].value_counts()
            for cat, count in cat_dist.items():
                print(f"    {cat}: {count} örnek")

        print(f"\n Örnek Veriler:")
        print("-" * 30)

        for lang in ['tr', 'en', 'es']:
            sample = df[df['language'] == lang].iloc[0]
            print(f"\n{lang.upper()}:")
            print(f"    Metin: {sample['text']}")
            print(f"    Kategori: {sample['category']}")
            print(f"    ID: {sample['category_id']}")

def create_config_files():

    print("\n Konfigürasyon dosyaları oluşturuyor...")

    config_data = {
        'model': {
            'name': 'bert-base-multilingual-cased',
            'max_lenght': 128,
            'batch_size': 16,
            'learning_rate': 2e-5,
            'epochs': 3,
            'num_labels': 5
        },
        'data': {
            'train_size': 0.7,
            'val_size': 0.15,
            'test_size': 0.15,
            'text_column': 'text',
            'label_column': 'category_id',
            'language_column': 'language'
        },
        'paths': {
            'raw_data': 'data/raw',
            'processed_data': 'data/processed',
            'models': 'models',
            'logs': 'logs'
        },
        'categories': {
            'tr': ['spor', 'politika', 'teknoloji', 'ekonomi', 'sağlık'],
            'en': ['sports', 'politics', 'technology', 'economy', 'health'],
            'es': ['deportes', 'política', 'tecnología', 'economía', 'salud'],
            'mapping': {
                'sports': 'spor',
                'politics': 'politika',
                'technology': 'teknoloji',
                'economy': 'ekonomi',
                'health': 'sağlık',
                'deportes': 'spor',
                'política': 'politika',
                'tecnología': 'teknoloji',
                'economía': 'ekonomi',
                'salud': 'sağlık'
            }
        }
    }

    with open('config/config.yaml','w', encoding='utf-8') as f:
        import yaml
        yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

        with open('requirements.txt', 'a') as f:
            f.write("\npyyaml>=6.0\n")

        print("Konfigürasyon dosyaları oluşturuldu.")

def setup_tokenizer():

    print("\n Tokenizer kurulumu...")

    try:
        from transformers import AutoTokenizer

        model_name = "bert-base-multilingual-cased"
        print(f"Tokenizer indiriliyor: {model_name}")

        tokenizer = AutoTokenizer.from_pretrained(model_name)

        sample_text = "Bu bir test cümlesidir."
        tokens = tokenizer(sample_text, truncation=True, padding=True, max_length=128)

        print(f" Tokenizer başarıyla yüklendi.")
        print(f" Örnek token sayısı: {len(tokens['input_ids'])}")
        print(f"Vocab size: {tokenizer.vocab_size}")

        tokenizer.save_pretrained("model/tokenizer")
        print("Tokenizer models/tokenizer dizinine kaydedildi.")

        return tokenizer

    except ImportError:
        print("Transformers kütüphanesi kurulu değil.")
        print("Çalıştır: pip install transformers")
        return None
    except Exception as e:
        print(f"Hata: {e}")

def prepare_datasets(df: pd.DataFrame):

    from sklearn.model_selection import train_test_split
    print("\n Veri setleri hazırlanıyor")

    train_dfs = []
    val_dfs = []
    test_dfs = []

    for lang in df['language'].unique():
        lang_df = df[df['language'] == lang]

        train_val, test = train_test_split(
            lang_df, test_size=0.15, random_state=42, stratify=lang_df['category_id']
        )

        train, val = train_test_split(
            train_val, test_size=0.1765, random_state=42, stratify=train_val['category_id']
        )

        train_dfs.append(train)
        val_dfs.append(val)
        test_dfs.append(test)

    train_df = pd.concat(train_dfs)
    val_df = pd.concat(val_dfs)
    test_df = pd.concat(test_dfs)

    train_df.to_csv('data/processed/train.csv', index=False, encoding='utf-8')
    val_df.to_csv('data/processed/test.csv', index=False, encoding='utf-8')

    print(f"Veri setleri oluşturuldu:")
    print(f"Train: {len(train_df)} örnek")
    print(f"Validation: {len(val_df)} örnek")
    print(f"Test: {len(test_df)} örnek")

    return train_df, val_df, test_df

def main():
    print("=" * 60)
    print("ÇOK DİLLİ HABER SINIFLANDIRICI - KURULUM")
    print("=" * 60)

    create_prject_structure()

    df = generate_sample_data(num_samples_per_lang=50)

    analyze_data(df)
    create_config_files()
    train_df, val_df, test_ = prepare_datasets(df)

    print("\n" + "=" * 60)
    print("İnternet bağlantısı gereken adım:")
    print("=" * 60)

    install_transformers = input("\nTransformers kütüphanesini kurmak istiyor musun? (e/h): ")

    if install_transformers.lower() == 'e':
        import subprocess
        import sys

        print("Transformers kütüphanesi kuruluyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "transformers"])

        tokenizer = setup_tokenizer()
        if tokenizer:
            print("\n Tokenizer başarıyla kuruldu.")
        else:
            print(" Transformers kurulumu atlandı. Daha sonra manuel kur:")
            print("  pip install transformers")

            print("\n" + "=" * 60)
            print("KURULUM TAMAMLANDI")
            print("=" * 60)

            print("\n OLUŞTURULAN DOSYALAR:")
            print(" - data/raw/sample_news_data.csv (Örnek Veri)")
            print(" - data/processed/train.csv (Eğitim Verisi)")
            print(" - data/processed/val.csv (Doğrulama Verisi)")
            print(" - data/processed/test.csv (Test Verisi)")
            print(" - config/config.yaml (Konfigürasyon)")
            print(" - requirements.txt (Gereksinimler)")
            print(" - gitignore (Git Ayarları)")

            print("\n SONRAKİ ADIMLAR:")
            print("1. Gerçek veri setini bul/oluştur")
            print("2. Model eğitim script'ini yaz")
            print("3. Modeli eğit")
            print("4. API geliştir")

            print("\n HIZLI TEST İÇİN:")
            print(
                "   python -c \"import pandas as pd; df=pd.read_csv('data/raw/sample_news_data.csv'); print(df.head())\"")

if __name__ == "__main__":
    main()

