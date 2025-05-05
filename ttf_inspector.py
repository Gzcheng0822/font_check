import json
import logging
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from fontTools.ttLib import TTFont

# Logger setup
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.handlers = [handler]

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


class TTFInspector:
    def __init__(self, font_path, language='en', lang_file='lang_pack.json', unicode_file='unicode_ranges.json'):
        self.font_path = font_path
        self.language = language
        self.lang_pack = self._load_lang_pack(resource_path(lang_file))
        self.unicode_ranges = self._load_unicode_ranges(resource_path(unicode_file))

        self._font = self._load_font()

    def _load_lang_pack(self, lang_file):
        try:
            data = load_json_file(lang_file)
            return data.get(self.language, data['en'])
        except Exception as e:
            logger.error(f"Failed to load language pack: {e}")
            return {}

    def _load_unicode_ranges(self, unicode_file):
        try:
            data = load_json_file(unicode_file)
            return {k: (int(v[0]), int(v[1])) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Failed to load unicode ranges: {e}")
            return {}

    def _load_font(self):
        try:
            return TTFont(self.font_path)
        except Exception as e:
            logger.error(f"Failed to load font: {e}")
            raise

    def count_characters(self):
        cmap = self._font['cmap']
        chars = {cp for table in cmap.tables for cp in table.cmap.keys()}
        return len(chars)

    def get_variable_axes(self):
        fvar = self._font.get('fvar')
        return [axis.axisTag for axis in fvar.axes] if fvar and hasattr(fvar, 'axes') else []

    def count_unicode_ranges(self):
        cmap = self._font['cmap']
        chars = {cp for table in cmap.tables for cp in table.cmap.keys()}
        counts = {}
        for key, (start, end) in self.unicode_ranges.items():
            counts[key] = sum(start <= cp <= end for cp in chars)
        return counts

    def get_font_metadata(self):
        name_table = self._font['name']
        keys = {
            'copyright': 0,
            'family': 1,
            'subfamily': 2,
            'unique_id': 3,
            'full_name': 4,
            'version': 5,
            'postscript_name': 6,
            'trademark': 7
        }
        result = {}
        for key, name_id in keys.items():
            record = name_table.getName(name_id, 3, 1, 0x409)
            result[key] = str(record) if record else ''
        return result

    def visualize(self, range_counts, total_ranges):
        import matplotlib.pyplot as plt
        from matplotlib.font_manager import FontProperties

        font_prop = FontProperties(fname=self.font_path)

        cjk_keys = [
            'basic_cjk', 'cjk_extension_a', 'cjk_extension_b', 'cjk_extension_c',
            'cjk_extension_d', 'cjk_extension_e', 'cjk_extension_f', 'cjk_extension_g',
            'kangxi_radicals', 'radical_supplement', 'cjk_compatibility', 'cjk_compatibility_supplement',
            'component_extension', 'cjk_strokes', 'cjk_structure', 'bopomofo', 'bopomofo_extended',
            'pua_gbk', 'pua_wall'
        ]
        global_keys = [
            'en', 'digit', 'punct', 'emoji', 'greek', 'cyrillic',
            'japanese_hiragana', 'japanese_katakana', 'arabic', 'hebrew', 'hindi', 'bengali'
        ]

        def get_color(percent):
            if percent >= 90:
                return '#9dc3e6'  # Monet Sky Blue
            elif percent >= 60:
                return '#b6d7a8'  # Monet Willow Green
            elif percent >= 30:
                return '#f9cb9c'  # Monet Apricot
            else:
                return '#f4cccc'  # Monet Pink

        fig, axs = plt.subplots(1, 2, figsize=(20, 8))

        labels_cjk = [self.lang_pack['section_names'].get(k, k) for k in cjk_keys]
        percents_cjk = [(range_counts.get(k, 0) / total_ranges.get(k, 1)) * 100 for k in cjk_keys]
        colors_cjk = [get_color(p) for p in percents_cjk]
        axs[0].bar(labels_cjk, percents_cjk, color=colors_cjk, edgecolor='gray')
        axs[0].set_title('CJK 区块支持率', fontproperties=font_prop)
        axs[0].set_ylabel('支持率 (%)', fontproperties=font_prop)
        axs[0].set_xticks(range(len(labels_cjk)))
        axs[0].set_xticklabels(labels_cjk, rotation=45, ha='right', fontproperties=font_prop)
        axs[0].set_ylim(0, 100)
        axs[0].tick_params(axis='y', labelsize=10)
        for label in axs[0].get_yticklabels():
            label.set_fontproperties(font_prop)

        labels_global = [self.lang_pack['section_names'].get(k, k) for k in global_keys]
        percents_global = [(range_counts.get(k, 0) / total_ranges.get(k, 1)) * 100 for k in global_keys]
        colors_global = [get_color(p) for p in percents_global]
        axs[1].bar(labels_global, percents_global, color=colors_global, edgecolor='gray')
        axs[1].set_title('全球语言区块支持率', fontproperties=font_prop)
        axs[1].set_xticks(range(len(labels_global)))
        axs[1].set_xticklabels(labels_global, rotation=45, ha='right', fontproperties=font_prop)
        axs[1].set_ylim(0, 100)
        axs[1].tick_params(axis='y', labelsize=10)
        for label in axs[1].get_yticklabels():
            label.set_fontproperties(font_prop)

        plt.tight_layout()
        plt.show()


    def inspect(self):
        char_count = self.count_characters()
        axes = self.get_variable_axes()
        range_counts = self.count_unicode_ranges()
        metadata = self.get_font_metadata()
        total_ranges = {key: end - start + 1 for key, (start, end) in self.unicode_ranges.items()}
        print(f"\n{self.lang_pack['report_title']}")
        print(self.lang_pack['char_count'].format(font=self.font_path, count=char_count))
        if axes:
            print(self.lang_pack['axes'].format(axes=', '.join(axes)))
        else:
            print(self.lang_pack['no_axes'])
        print(self.lang_pack['section'])
        for key, count in range_counts.items():
            name = self.lang_pack['section_names'].get(key, key)
            total = total_ranges[key]
            percent = count / total * 100 if total > 0 else 0
            print(self.lang_pack['section_item'].format(name=name, count=count, total=total, percent=percent))
        print(f"\n{self.lang_pack['metadata']['title']}")
        for meta_key, value in metadata.items():
            label = self.lang_pack['metadata'].get(meta_key, meta_key)
            print(f"    - {label}: {value}")
        self.visualize(range_counts, total_ranges)
