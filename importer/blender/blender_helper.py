import inspect

def log(text):
    caller = inspect.stack()[1].filename.split("\\")[-1].replace(".py", "")
    print("[owm]", caller+":", text)