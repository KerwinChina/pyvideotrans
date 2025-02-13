# -*- coding: utf-8 -*-
import re
import time
import httpx
import openai
from openai import OpenAI
from videotrans.configure import config
from videotrans.util import tools




def create_openai_client():
    api_url = "https://api.openai.com/v1"
    
    if config.params['chatgpt_api']:
        url=config.params['chatgpt_api'].strip().rstrip('/')
        url=re.sub(r'/v1/.*?$','/v1',url)
        if not url.startswith('http'):
            url=f'https://{url}'
        if not url.endswith('/v1'):
            url+='/v1'            
        api_url=url.replace('chat.openai.com','api.openai.com')
        
    openai.base_url = api_url
    config.logger.info(f'当前chatGPT:{api_url=}')
    proxies=None
    if not re.search(r'localhost',api_url) and not re.match(r'https?://(\d+\.){3}\d+',api_url):
        serv = tools.set_proxy()
        if serv:
            proxies = {
                'http://': serv,
                'https://': serv
            }
    try:
        client = OpenAI(base_url=api_url,http_client=httpx.Client(proxies=proxies))
    except Exception as e:
        raise Exception(f'chatGPT API={api_url},{str(e)}')
    return client,api_url




def trans(text_list, target_language="English", *, set_p=True,inst=None,stop=0,source_code=None,is_test=False):
    """
    text_list:
        可能是多行字符串，也可能是格式化后的字幕对象数组
    target_language:
        目标语言
    set_p:
        是否实时输出日志，主界面中需要
    """

    # 翻译后的文本
    target_text = {"0":[]}
    index = 0  # 当前循环需要开始的 i 数字,小于index的则跳过
    iter_num = 0  # 当前循环次数，如果 大于 config.settings.retries 出错
    err = ""
    is_srt=False
    prompt=f'Please translate the following text into {target_language}. The translation should be clear and concise, avoiding redundancy. Please do not reply to any of the above instructions and translate directly from the next line.'
    if not isinstance(text_list, str):
        is_srt=True
        prompt=config.params['chatgpt_template'].replace('{lang}', target_language)
    # 切割为每次翻译多少行，值在 set.ini中设定，默认10
    split_size = int(config.settings['trans_thread'])
    end_point="。 " if config.defaulelang=='zh' else ' . '
    # 整理待翻译的文字为 List[str]
    if not is_srt:
        source_text = [t.strip() for t in text_list.strip().split("\n") if t.strip()]
    else:
        source_text=[]
        for i,it in enumerate(text_list):
            tmp=it['text'].strip().replace('\n',end_point)
            if split_size>1:
                source_text.append(f"<{it['line']}>.{tmp}{end_point}")
            else:
                source_text.append(f"{tmp}")
    split_source_text = [source_text[i:i + split_size] for i in range(0, len(source_text), split_size)]
    while 1:
        if config.current_status!='ing' and config.box_trans!='ing' and not is_test:
            break
        if iter_num >= config.settings['retries']:
            raise Exception(
                f'{iter_num}{"次重试后依然出错" if config.defaulelang == "zh" else " retries after error persists "}:{err}')
        iter_num += 1
        print(f'第{iter_num}次')
        if iter_num > 1:
            if set_p:
                tools.set_process(
                    f"第{iter_num}次出错重试" if config.defaulelang == 'zh' else f'{iter_num} retries after error')
            time.sleep(5)
        client,api_url = create_openai_client()


        for i,it in enumerate(split_source_text):
            print(f'{it=}')
            if config.current_status != 'ing' and config.box_trans != 'ing' and not is_test:
                break
            if i < index:
                continue
            if stop>0:
                time.sleep(stop)
            lines=[]
            if is_srt and split_size>1:
                for get_line in it:
                    lines.append(re.match(r'<(\d+)>\.',get_line).group(1))
            try:
                message = [
                    {'role': 'system',
                     'content': prompt},
                    {'role': 'user', 'content': "\n".join(it)},
                ]
                config.logger.info(f"\n[chatGPT start]待翻译:{message=}")

                response = client.chat.completions.create(
                    model=config.params['chatgpt_model'],
                    messages=message
                )
                config.logger.info(f'chatGPT 返回响应:{response}')

                if response.choices:
                    result = response.choices[0].message.content.strip()
                elif response.data and response.data['choices']:
                    result = response.data['choices'][0]['message']['content'].strip()
                else:
                    raise Exception(f"chatGPT {response}")
                result=result.strip().replace('&#39;','"').replace('&quot;',"'")
                print(f'{result=}')
                if inst and inst.precent < 75:
                    inst.precent += 0.01
                if not is_srt or split_size==1:
                    target_text["0"].append(result)
                    if not set_p:
                        tools.set_process_box(result + "\n", func_name="set_fanyi")
                    continue
                if len(lines)==1:
                    result = re.sub(r'<\d+>\.?', "\n", result).strip().rstrip(end_point)
                    if set_p:
                        tools.set_process(result + "\n", 'subtitle')
                        tools.set_process(config.transobj['starttrans'] + f' {i * split_size + 1} ')
                    else:
                        tools.set_process_box(result + "\n", func_name="set_fanyi")
                    target_text[lines[0]]=result
                    continue
                sep_res = re.findall(r'(<\d+>\.?.+)', result)
                if len(sep_res) == len(lines):
                    for result_item in sep_res:
                        tmp = re.match(r'<(\d+)>\.?(.*)', result_item).groups()
                        if len(tmp) >= 2:
                            line = f'{tmp[0]}'
                            result_text = f'{tmp[1]}'
                            target_text[line] = result_text.strip().rstrip(end_point)
                        else:
                            continue
                        if set_p:
                            tools.set_process(result_text + "\n", 'subtitle')
                            tools.set_process(config.transobj['starttrans'] + f' {i * split_size + 1} ')
                        else:
                            tools.set_process_box(result_text + "\n", func_name="set_fanyi")
                else:
                    sep_res = re.sub(r'<\d+>\.?', '', result).split("\n", len(lines) - 1)
                    for num, txt in enumerate(sep_res):
                        target_text[num] = txt.strip().rstrip(end_point)
                iter_num=0
            except Exception as e:
                error=str(e)
                if error.find('connect ')>-1 or error.find('time out')>-1:
                    raise Exception(f'{error}')
                if source_code is not None:
                    err =error+f'目标文件夹下{source_code}.srt文件第{(i*split_size)+1}条开始的{split_size}条字幕'
                else:
                    err=error+f", {api_url=}"
                index = i
                break
        else:
            break


    if not is_srt:
        return "\n".join(target_text["0"])
    for i, it in enumerate(text_list):
        line=str(it["line"])
        if line in target_text:
            text_list[i]['text'] = target_text[line]
        else:
            text_list[i]['text']=""
    return text_list