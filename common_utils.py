

def get_log_level(level):
    levels = {'CRITICAL': 50,
              'ERROR': 40,
              'WARNING': 30,
              'INFO': 20,
              'DEBUG': 10,
              'NOTSET': 0,
              }
    level = level.upper()
    return levels[level] if level in levels else 0
