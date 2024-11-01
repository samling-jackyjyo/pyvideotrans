from pathlib import Path
from typing import Union, List, Dict

from videotrans import translator
from videotrans.configure import config
# 判断各个语音识别模式是否支持所选语言
# 支持返回True，不支持返回错误文字字符串



# 数字代表界面中的现实顺序
FASTER_WHISPER = 0
OPENAI_WHISPER = 1
FUNASR_CN = 2
STT_API = 3
DOUBAO_API = 4
Deepgram = 5
OPENAI_API = 6
CUSTOM_API = 7
GOOGLE_SPEECH = 8

RECOGN_NAME_LIST = [
    'faster-whisper(本)' if config.defaulelang == 'zh' else 'faster-whisper',
    'openai-whisper(本)' if config.defaulelang == 'zh' else 'openai-whisper',
    "FunASR中文(本)" if config.defaulelang == 'zh' else "FunASR-CN",
    "STT语音识别(本)" if config.defaulelang == 'zh' else "Stt Speech API",
    "字节火山字幕生成API" if config.defaulelang == 'zh' else "VolcEngine Subtitle API",
    "DeepgramAPI" if config.defaulelang == 'zh' else "DeepgramAPI",
    "OpenAI识别API" if config.defaulelang == 'zh' else "OpenAI Speech API",
    "自定义识别API" if config.defaulelang == 'zh' else "Custom Recognition API",
    "Google识别api" if config.defaulelang == 'zh' else "Google Speech API",
]


def is_allow_lang(langcode: str = None, recogn_type: int = None,model_name=None):
    if langcode=='auto' and recogn_type not in [FASTER_WHISPER,OPENAI_WHISPER]:
        return '仅在 faster-whisper和 openai-whisper模式下允许检测语言' if config.defaulelang=='zh' else 'Recognition language is only supported in faster-whisper and openai-whisper modes.'
    if recogn_type == FUNASR_CN and langcode[:2] !='zh':
            return 'FunASR 下 paraformer-zh 和 SenseVoiceSmall 模型仅支持中文语音识别' if config.defaulelang == 'zh' else 'paraformer-zh and SenseVoiceSmall models only support Chinese speech recognition'

    if recogn_type == DOUBAO_API and langcode[:2] not in ["zh", "en", "ja", "ko", "es", "fr", "ru"]:
        return '豆包语音识别仅支持中英日韩法俄西班牙语言，其他不支持'


    return True

# 判断 openai whisper和 faster whisper 模型是否存在
def check_model_name(recogn_type=FASTER_WHISPER, name='',source_language_isLast=False,source_language_currentText=''):
    if recogn_type not in [OPENAI_WHISPER, FASTER_WHISPER]:
        return True
    # 含 / 的需要下载
    if name.find('/') > 0:
        return True
    if name.endswith('.en') and source_language_isLast:
        return '.en结尾的模型不可用于自动检测' if config.defaulelang == 'zh' else 'Models ending in .en may not be used for automated detection'

    if name.endswith('.en') and translator.get_code(show_text=source_language_currentText) != 'en':
        return config.transobj['enmodelerror']

    if recogn_type == OPENAI_WHISPER:
        if name.startswith('distil'):
            return 'distil 开头的模型只可用于 faster-whisper本地模式' if config.defaulelang=='zh' else 'distil-* only use when faster-whisper'
        # 不存在，需下载
        if not Path(config.ROOT_DIR + f"/models/{name}.pt").exists():
            return 'download'
        return True

    file = f'{config.ROOT_DIR}/models/models--Systran--faster-whisper-{name}/snapshots'
    if name.startswith('distil'):
        file = f'{config.ROOT_DIR}/models/models--Systran--faster-{name}/snapshots'
    if not Path(file).exists():
        return 'download'
    return True


# 自定义识别、openai-api识别、zh_recogn识别是否填写了相关信息和sk等
# 正确返回True，失败返回False，并弹窗
def is_input_api(recogn_type: int = None,return_str=False):
    from videotrans.winform import zh_recogn as zh_recogn_win, recognapi as recognapi_win,  openairecognapi as openairecognapi_win, doubao as doubao_win,sttapi as sttapi_win,senseapi as sense_win,deepgram as deepgram_win
    if recogn_type == STT_API and not config.params['stt_url']:
        if return_str:
            return "Please configure the api and key information of the stt channel first."
        sttapi_win.openwin()
        return False
        
    if recogn_type == CUSTOM_API and not config.params['recognapi_url']:
        if return_str:
            return "Please configure the api and key information of the CUSTOM_API channel first."
        recognapi_win.openwin()
        return False

    if recogn_type == OPENAI_API and not config.params['openairecognapi_key']:
        if return_str:
            return "Please configure the api and key information of the OPENAI_API channel first."
        openairecognapi_win.openwin()
        return False
    if recogn_type == DOUBAO_API and not config.params['doubao_appid']:
        if return_str:
            return "Please configure the api and key information of the DOUBAO_API channel first."
        doubao_win.openwin()
        return False
    if recogn_type == Deepgram and not config.params['deepgram_apikey']:
        if return_str:
            return "Please configure the API Key information of the Deepgram channel first."
        deepgram_win.openwin()
        return False
    return True


# 统一入口
def run(*,
        split_type="all",
        detect_language=None,
        audio_file=None,
        cache_folder=None,
        model_name=None,
        inst=None,
        uuid=None,
        recogn_type: int = 0,
        is_cuda=None,
        subtitle_type=0
        ) -> Union[List[Dict], None]:
    if config.exit_soft or (config.current_status != 'ing' and config.box_recogn != 'ing'):
        return
    if model_name and model_name.startswith('distil-'):
        model_name = model_name.replace('-whisper', '')
    kwargs = {
        "detect_language": detect_language,
        "audio_file": audio_file,
        "cache_folder": cache_folder,
        "model_name": model_name,
        "uuid": uuid,
        "inst": inst,
        "is_cuda": is_cuda,
        "subtitle_type":subtitle_type
    }
    if recogn_type == OPENAI_WHISPER:
        from ._openai import OpenaiWhisperRecogn
        return OpenaiWhisperRecogn(**kwargs).run()
    if recogn_type == GOOGLE_SPEECH:
        from ._google import GoogleRecogn
        return GoogleRecogn(**kwargs).run()

    if recogn_type == DOUBAO_API:
        from ._doubao import DoubaoRecogn
        return DoubaoRecogn(**kwargs).run()
    if recogn_type == CUSTOM_API:
        from ._recognapi import APIRecogn
        return APIRecogn(**kwargs).run()
    if recogn_type == STT_API:
        from ._stt import SttAPIRecogn
        return SttAPIRecogn(**kwargs).run()
        
    if recogn_type == OPENAI_API:
        from ._openairecognapi import OpenaiAPIRecogn
        return OpenaiAPIRecogn(**kwargs).run()
    if recogn_type==FUNASR_CN:
        from ._funasr import FunasrRecogn
        return FunasrRecogn(**kwargs).run()
    if recogn_type==Deepgram:
        from ._deepgram import DeepgramRecogn
        return DeepgramRecogn(**kwargs).run()
    if split_type == 'avg':
        from ._average import FasterAvg
        return FasterAvg(**kwargs).run()

    from ._overall import FasterAll
    return FasterAll(**kwargs).run()
