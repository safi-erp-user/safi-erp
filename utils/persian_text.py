import arabic_reshaper
from bidi.algorithm import get_display
import re


def reshape_text(text):
    """تبدیل متن فارسی برای نمایش صحیح در Kivy"""
    if not text:
        return ''

    if isinstance(text, str):
        try:
            parts = re.split(r'(\d+|[a-zA-Z]+)', text)
            result = []
            for part in parts:
                if part:
                    if re.match(r'^[\u0600-\u06FF\s]+$', part):
                        reshaped = arabic_reshaper.reshape(part)
                        bidi = get_display(reshaped)
                        result.append(bidi)
                    else:
                        result.append(part)
            return ''.join(result)
        except:
            return text
    return str(text)