import re

def parse_version(v_str):
    try:
        nums = re.findall(r'\d+', str(v_str))
        return tuple(int(n) for n in nums)
    except Exception:
        return ()

def is_outdated(installed_v, min_v):
    v1 = parse_version(installed_v)
    v2 = parse_version(min_v)
    if not v1 or not v2:
        return False
    max_len = max(len(v1), len(v2))
    v1 = v1 + (0,) * (max_len - len(v1))
    v2 = v2 + (0,) * (max_len - len(v2))
    return v1 < v2
