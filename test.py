'''
import requests
from PySide6.QtCore import QSettings

from videotrans.configure import config

url=QSettings("Jameson", "VideoTranslate").value("clone_api", "")
print(f'{url=}')
if not url:
    print(config.transobj['bixutianxiecloneapi'])
else:
    try:
        url = url.strip().rstrip('/') + "/init"
        res = requests.get('http://' + url.replace('http://', ''))
        if res.status_code == 200:
            print(res.json)
            print("\nOK\n")
        else:
            raise Exception(f"code={res.status_code},{config.transobj['You must deploy and start the clone-voice service']}")
    except Exception as e:
        print(f'[error]:clone-voice:{str(e)}')


input("Press Enter for quit")
'''

# from videotrans.separate import st
# try:
#     gr = st.uvr(model_name="HP2", save_root="./", inp_path=r'C:/Users/c1/Videos/240.wav')
#     print(next(gr))
#     print(next(gr))
# except Exception as e:
#     msg=f"separate vocal and background music:{str(e)}"
#     #set_process(msg)
#     print(msg)


## 获取识别文字
# import os
# from faster_whisper import WhisperModel
# model = WhisperModel("base", device="cpu",
#                              download_root="./models",
#                              local_files_only=True)
# data=[]
#
# for i in range(0,24):
#     name=f'output0{str(i).zfill(2)}.wav'
#     if not os.path.exists(f'c:/users/c1/videos/_video_out/{name}'):
#         continue
#     segments, info = model.transcribe(f'c:/users/c1/videos/_video_out/{name}',
#                                           beam_size=1,
#                                           best_of=1,
#                                           condition_on_previous_text=False,language="zh")
#     res=[]
#     for segment in segments:
#         res.append(segment.text.strip())
#     data.append(f"wavs/{name}|{'.'.join(res)}|coqui")
#
# with open("./metadata_train.csv","w",encoding='utf-8') as f:
#     f.write("\n".join(data))

# import requests
# lang=["zh-hans","zh-hant","en","fr","de","ja","ko","ru","es","th","it","pt","vi","ar","tr","hi","hu"]
#
# auth=requests.get('https://edge.microsoft.com/translate/auth')
#
# for it in lang:
#     url=f'https://api-edge.cognitive.microsofttranslator.com/translate?from=&to={it}&api-version=3.0&includeSentenceLength=true'
#     res=requests.post(url,json=[{"Text":"hello,my friend\nI am from China"}],headers={"Authorization":f"Bearer {auth.text}"})
#     print(res.json())


# from videotrans.util import tools
#
# cmd=["-y",'-ss', '0', '-to', '00:00:01.300', '-i', 'C:/Users/c1/Videos/pyvideotrans/renamemp4/_video_out/31-副本/novoice.mp4', '-vf', 'setpts=1.96*PTS', '-c:v', 'libx264', '-crf', '13', 'F:/python/pyvideo/tmp/31-副本/novoice_tmp.mp4']
#
# tools.runffmpeg(cmd)
# import time

# a="有新的版本哦，快去升级吧"
# length=len(a)
# while 1:
#     for i in range(length):
#         if i==0:
#             print(a)
#         elif i==length-1:
#             print(a[i]+a[:i])
#         else:
#             print(a[i:]+a[:i])
#         time.sleep(0.1)
#     time.sleep(5)


# from videotrans.util import tools


# tools.get_subtitle_from_srt(r'C:\Users\c1\Videos\dev\0001.srt',is_file=True)


# import re
#
# def format_time(s_time="",separate=','):
#     if not s_time.strip():
#         return f'00:00:00.000'
#     hou,min,sec="00","00","00.000"
#     tmp=s_time.split(':')
#     if len(tmp)>=3:
#         hou=tmp[-3]
#         min=tmp[-2]
#         sec=tmp[-1]
#     elif len(tmp)==2:
#         min=tmp[0]
#         sec=tmp[1]
#     elif len(tmp)==1:
#         sec=tmp[0]
#
#     if re.search(r',|\.',str(sec)):
#         sec,ms=re.split(r',|\.',str(sec))
#     else:
#         ms='000'
#     hou=hou if hou!="" else "00"
#     if len(hou)<2:
#         hou=f'0{hou}'
#     hou=hou[-2:]
#
#     min=min if min!="" else "00"
#     if len(min)<2:
#         min=f'0{min}'
#     min=min[-2:]
#
#     sec=sec if sec!="" else "00"
#     if len(sec)<2:
#         sec=f'0{sec}'
#     sec=sec[-2:]
#
#     ms_len=len(ms)
#     if ms_len<3:
#         for i in range(3-ms_len):
#             ms=f'0{ms}'
#     ms=ms[-3:]
#     return f"{hou}:{min}:{sec}{separate}{ms}"
#
# print(format_time('',','))


#
# import httpx, json,requests
#
# deeplx_api = "https://service-2rlyleme-1259515617.gz.tencentapigw.com.cn/translate"
#
# data = {
#     "text": "你好我的朋友",
#     "source_lang": "auto",
#     "target_lang": "en"
# }
# res=requests.post(url=deeplx_api, json=data)
# print(res.json())


# import requests
#
# data={
#     "refer_wav_path": "wavs/mayun.wav",
#     "prompt_text": "我记得我大学一年级的时候，我自，我从小自学的英文，我的英文是在西湖边上抓老外。",
#     "prompt_language": "zh",
#     "text": """GPT Sovits 是一个非常棒的少样本中文声音克隆项目，之前有一篇文章详细介绍过如何部署和训练自己的模型，并使用该模型在 web 界面中合成声音，可惜它自带的 api 在调用方面支持比较差，比如不能中英混合、无法按标点切分句子等，因此对原版 api 做了修改，详细使用说明如下。
#
# 和官方原版 api 一样都不支持动态模型切换，也不建议这样做，因为动态启动加载模型很慢，而且在失败时也不方便处理。
#
# 解决方法是:一个模型起一个 api 服务器，绑定不同的端口，在启动 api 时，指定当前服务所要使用的模型和绑定的端口。
#
# 比如起2个服务，一个使用默认模型，绑定 9880 端口，一个绑定自己训练的模型，绑定 9881 端口，命令如下。""",
#     "text_language": "zh"
# }
#
# response=requests.post("http://127.0.0.1:9881",json=data)
#
# if response.status_code==400:
#     raise Exception(f"请求GPTSoVITS出现错误:{response.message}")
#
#
# # 如果是WAV音频流，获取原始音频数据
# with open("success.wav", 'wb') as f:
#     f.write(response.content)

import os
import shutil
import subprocess
import sys

if not shutil.which("ffmpeg"):
    print('当前系统未安装ffmpeg，请下载ffmpeg.exe 放在当前目录下\n下载地址\nhttps://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z')
    input("按回车退出")
    sys.exit()

root = os.getcwd()
cfg = os.path.join(root, 'cfg.ini')
sext = ['mp3', 'flac', 'mp4', 'mpeg', 'aac', 'mkv', 'avi']
ext = 'wav'
if os.path.exists(cfg):
    with open(cfg, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            it = line.strip()
            if it:
                it = it.replace('，', ',').split('=')
                if len(it) == 2 and it[0].lower() == 'source_ext':
                    sext = [x.lower().strip() for x in it[1].split(",")]
                elif len(it) == 2 and it[0].lower() == 'target_ext':
                    ext = it[1].lower().strip()

files = []
for it in os.listdir(root):
    if it.split('.')[-1].lower() in sext:
        files.append(it)

print(f'当前将把格式为 {sext} 的文件转为 {ext}\n')
if len(files) < 1:
    print(f'没有需要转换的文件')
else:
    ok = 0
    err = []

    for it in files:
        try:
            subprocess.run(
                ['ffmpeg', "-hide_banner", "-ignore_unknown", '-y', '-i', os.path.normpath(os.path.join(root, it)),
                 f'{it}.{ext}'], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            print(f'[OK] {it} 转换成功')
            ok += 1
        except:
            err.append(it)
            print(f'[Error] {it} 转换失败')

    print(f"\n转换完毕，{ok} 个成功，{len(err)} 个失败,{err if len(err) > 0 else ''}\n")
input("按回车退出")
