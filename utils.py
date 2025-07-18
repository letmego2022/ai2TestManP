from openai import OpenAI
import io
import contextlib
client = OpenAI(api_key="sk-UZdaQuqB7BwuwlOhQawLgePMCdbEOPrUrafibnJJ3M3P4DLt", base_url="https://api.moonshot.cn/v1")


def run_python_code(code: str):
    output = io.StringIO()
    local_vars = {}

    with contextlib.redirect_stdout(output):
        try:
            # 尝试先作为表达式执行
            result = eval(code, {}, local_vars)
        except SyntaxError:
            # 如果不是表达式，是代码块，就用 exec 执行
            exec(code, {}, local_vars)
            result = None
        except Exception as e:
            result = f"❌ 错误: {e}"

    printed_output = output.getvalue()
    return printed_output.strip() or result

def chat_mode(messages, stream=False):
    if stream:
        def generator():
            completion = client.chat.completions.create(
                model="moonshot-v1-auto",
                messages=messages,
                temperature=0.3,
                stream=True
            )
            collected_messages = []
            for chunk in completion:
                chunk_message = chunk.choices[0].delta.content
                if not chunk_message:
                    continue
                collected_messages.append(chunk_message)
                yield chunk_message

            result = ''.join(collected_messages)
            if '</think>' in result:
                result = result.split('</think>', 1)[1].strip()
            result_holder["text"] = result  # 将最终结果写入外部变量

        result_holder = {"text": ""}
        return generator(), result_holder
    else:
        completion = client.chat.completions.create(
            model="moonshot-v1-auto",
            messages=messages,
            temperature=0.3
        )
        result = completion.choices[0].message.content
        if '</think>' in result:
            result = result.split('</think>', 1)[1].strip()
        return result
