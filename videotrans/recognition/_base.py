import copy
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Union

import torch
import zhconv

from videotrans.configure import config
from videotrans.configure._base import BaseCon

from videotrans.util import tools


class BaseRecogn(BaseCon):

    def __init__(self, detect_language=None, audio_file=None, cache_folder=None,
                 model_name=None, inst=None, uuid=None, is_cuda=None,subtitle_type=0):
        super().__init__()
        # 需要判断当前是主界面任务还是单独任务，用于确定使用哪个字幕编辑区
        self.detect_language = detect_language
        self.audio_file = audio_file
        self.cache_folder = cache_folder
        self.model_name = model_name
        self.inst = inst
        self.uuid = uuid
        self.is_cuda = is_cuda
        self.has_done = False
        self.error = ''
        self.subtitle_type=subtitle_type
        self.device="cuda" if  torch.cuda.is_available() else 'cpu'


        self.api_url = ''
        self.proxies = None

        self.flag = [
            ",",
            
            ".",
            "?",
            "!",
            ";",
           
            "，",
            "。",
            "？",
            "；",      
            "！"
        ]
        
        self.join_word_flag = " "
        
        self.jianfan=False
        if self.detect_language[:2].lower() in ['zh', 'ja', 'ko']:
            self.maxlen = int(float(config.settings.get('cjk_len',20)))
            self.jianfan = True if self.detect_language[:2] == 'zh' and config.settings['zh_hant_s'] else False
        else:
            self.maxlen = int(float(config.settings.get('other_len',60)))
        
        if not tools.vail_file(self.audio_file):
            raise Exception(f'[error]not exists {self.audio_file}')

    # 出错时发送停止信号
    def run(self) -> Union[List[Dict], None]:
        self._signal(text="")
        try:
            if self.detect_language[:2].lower() in ['zh', 'ja', 'ko']:
                self.flag.append(" ")
                self.join_word_flag = ""
            return self._exec()
        except Exception as e:
            config.logger.exception(e, exc_info=True)
            msg = f'{str(e)}'
            if re.search(r'cub[a-zA-Z0-9_.-]+?\.dll', msg, re.I | re.M) is not None:
                msg = f'【缺少cuBLAS.dll】请点击菜单栏-帮助/支持-下载cublasxx.dll,或者切换为openai模型 {msg} ' if config.defaulelang == 'zh' else f'[missing cublasxx.dll] Open menubar Help&Support->Download cuBLASxx.dll or use openai model {msg}'
            elif re.search(r'out\s+?of.*?memory', msg, re.I):
                msg = f'显存不足，请使用较小模型，比如 tiny/base/small {msg}' if config.defaulelang == 'zh' else f'Insufficient video memory, use a smaller model such as tiny/base/small {msg}'
            elif re.search(r'cudnn', msg, re.I):
                msg = f'cuDNN错误，请尝试升级显卡驱动，重新安装CUDA12.x和cuDNN9 {msg}' if config.defaulelang == 'zh' else f'cuDNN error, please try upgrading the graphics card driver and reinstalling CUDA12.x and cuDNN9 {msg}'
            self._signal(text=msg, type="error")
            raise
        finally:
            if self.shound_del:
                self._set_proxy(type='del')

    def _exec(self) -> Union[List[Dict], None]:
        pass

    def re_segment_sentences(self,words):
        from funasr import AutoModel
        import zhconv
        # 删掉标点和不含有文字的word
        new_words = []
        pat = re.compile(r'[，。！？；｛｝“”‘’"\'{}\[\](),.?!;_ \s-]')
        jianfan=config.settings.get('zh_hant_s')
        for i, it in enumerate(words):
            it['word'] = pat.sub('', it['word']).strip()
            if not it['word']:
                continue
            it['word']=zhconv.convert(it['word'], 'zh-hans') if jianfan else it['word']
            new_words.append(it)
        text = "".join([w["word"] for w in new_words])
        model = AutoModel(model="ct-punc-c", model_revision="v2.0.4",
                          disable_update=True,
                          disable_log=True,
                          local_dir=config.ROOT_DIR + "/models",
                          disable_progress_bar=True,
                        device=self.device)
        res = model.generate(input=text)
        # 移除空格防止位置变化
        text = re.sub(r'[ \s]', '', res[0]['text']).strip()
        flag_list = ['，', '。', '？', '！', '；', '、', ',', '?', '.', '!', ';']

        # 记录每个标点符号在原text中应该插入的位置
        flags = {}
        pos_index = -1
        for i in range(len(text)):
            if text[i] not in flag_list:
                pos_index += 1
            else:
                flags[str(pos_index)] = text[i]

        # 复制一份words，将标点插入
        pos_start = -1
        flags_index = list(flags.keys())
        copy_words = copy.deepcopy(new_words)
        for w_index, it in enumerate(new_words):
            if len(flags_index) < 1:
                new_words[w_index] = it
                break
            f0 = int(flags_index[0])
            if pos_start + len(it['word']) < f0:
                pos_start += len(it['word'])
                continue
            # 当前应该插入的标点位置 f0大于 pos_start 并且小于 pos_start+长度，即位置存在于当前word
            # word中可能是1-多个字符
            if f0 > pos_start and f0 <= pos_start + len(it['word']):
                if len(it['word']) == 1:
                    copy_words[w_index]['word'] += flags[str(f0)]
                    pos_start += len(it['word'])
                    flags_index.pop(0)
                elif len(it['word']) > 1:
                    for j in range(f0 - pos_start):
                        if pos_start + j + 1 == f0:
                            copy_words[w_index]['word'] += flags[str(f0)]
                            pos_start += len(it['word'])
                            flags_index.pop(0)
                            break
                new_words[w_index] = it
        # 根据标点符号断句

        raws = []
        last_tmp = None
        length = int(config.settings.get('cjk_len'))
        for i, w in enumerate(copy_words):
            if not last_tmp:
                last_tmp = {
                    "line": 1 + len(raws),
                    "start_time": int(w['start'] * 1000),
                    "end_time": int(w['end'] * 1000),
                    "text": w['word'],
                }
            elif w['word'][-1] in flag_list and (
                    w['start'] * 1000 > last_tmp['end_time']  or len(last_tmp['text']) + len(w['word']) > length/2):
                last_tmp['text'] += w['word']
                last_tmp['end_time'] = int(w['end'] * 1000)
                last_tmp['startraw']=tools.ms_to_time_string(ms=last_tmp["start_time"])
                last_tmp['endraw']=tools.ms_to_time_string(ms=last_tmp["end_time"])
                last_tmp['time'] = f"{last_tmp['startraw']} --> {last_tmp['endraw']}"
                raws.append(last_tmp)
                last_tmp = None
            else:
                last_tmp['text'] += w['word']
                last_tmp['end_time'] = int(w['end'] * 1000)
        if last_tmp:
            last_tmp['startraw'] = tools.ms_to_time_string(ms=last_tmp["start_time"])
            last_tmp['endraw'] = tools.ms_to_time_string(ms=last_tmp["end_time"])
            last_tmp['time'] = f"{last_tmp['startraw']} --> {last_tmp['endraw']}"
            raws.append(last_tmp)
        return raws

    # True 退出
    def _exit(self) -> bool:
        if config.exit_soft or (config.current_status != 'ing' and config.box_recogn != 'ing'):
            return True
        return False
