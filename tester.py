import traceback

try:
    k = 1 / 0
except Exception as e:
    print(traceback.format_exc())
    print(e.args)
    print(e.with_traceback(e.__traceback__))
