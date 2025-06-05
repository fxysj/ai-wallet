import base64


def image_to_base64(path: str, with_prefix: bool = False) -> str:
    """
    将本地图片转换为 base64 编码字符串。

    参数:
        path (str): 图片文件路径，例如 '1.png'。
        with_prefix (bool): 是否加上 'data:image/...;base64,' 前缀（适合网页或API传输）。

    返回:
        str: base64 编码的字符串。
    """
    try:
        with open(path, "rb") as image_file:
            encoded_bytes = base64.b64encode(image_file.read())
            base64_str = encoded_bytes.decode("utf-8")

            if with_prefix:
                # 自动判断 MIME 类型前缀（这里只举例处理 png）
                if path.lower().endswith(".png"):
                    mime = "image/png"
                elif path.lower().endswith((".jpg", ".jpeg")):
                    mime = "image/jpeg"
                elif path.lower().endswith(".gif"):
                    mime = "image/gif"
                else:
                    mime = "application/octet-stream"

                return f"data:{mime};base64,{base64_str}"
            else:
                return base64_str

    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return f"Error: {str(e)}"
