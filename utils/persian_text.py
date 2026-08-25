import arabic_reshaper
from bidi.algorithm import get_display


def reshape_text(text):
    """تبدیل متن فارسی به فرمت صحیح برای نمایش"""
    if not text:
        return ''

    if isinstance(text, str):
        try:
            reshaped = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped)
            return bidi_text
        except:
            return text
    return str(text)


def rtl_text(text):
    """تبدیل متن فارسی برای نمایش RTL"""
    return reshape_text(text)