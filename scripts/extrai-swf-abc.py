import sys, os, zlib, struct, json, re

def read_swf_body(path):
    d = open(path,'rb').read()
    sig = d[:3]
    if sig == b'CWS':
        return d[:8] + zlib.decompress(d[8:])
    if sig == b'FWS':
        return d
    if sig == b'ZWS':
        import lzma
        return d  # not expected
    raise ValueError('sig '+str(sig))

def skip_rect(d, i):
    nbits = d[i] >> 3
    total = 5 + nbits*4
    return i + (total + 7)//8

def iter_tags(body):
    i = 8
    i = skip_rect(body, i)
    i += 4  # framerate + framecount
    while i < len(body):
        if i+2 > len(body): break
        rt, = struct.unpack_from('<H', body, i); i += 2
        code = rt >> 6
        ln = rt & 0x3F
        if ln == 0x3F:
            ln, = struct.unpack_from('<I', body, i); i += 4
        yield code, body[i:i+ln]
        i += ln
        if code == 0: break

def u30(b, i):
    r = 0; s = 0
    for _ in range(5):
        c = b[i]; i += 1
        r |= (c & 0x7F) << s
        if not (c & 0x80): break
        s += 7
    return r, i

def abc_strings(b):
    # DoABC: u32 flags, string name (nul-term), then abcFile
    i = 4
    while b[i] != 0: i += 1
    i += 1
    i += 4  # minor/major version
    # cpool
    n, i = u30(b, i)
    for _ in range(max(0,n-1)):
        _, i = u30(b, i)  # ints
    n, i = u30(b, i)
    for _ in range(max(0,n-1)):
        _, i = u30(b, i)  # uints
    n, i = u30(b, i)
    i += 8*max(0,n-1)     # doubles
    n, i = u30(b, i)
    out = []
    for _ in range(max(0,n-1)):
        l, i = u30(b, i)
        out.append(b[i:i+l].decode('utf-8','replace'))
        i += l
    return out

def analyze(path):
    body = read_swf_body(path)
    strs = []
    nabc = 0
    for code, data in iter_tags(body):
        if code == 82:
            nabc += 1
            try:
                strs += abc_strings(data)
            except Exception as e:
                pass
    return strs

if __name__ == '__main__':
    path = sys.argv[1]
    strs = analyze(path)
    out = sys.argv[2]
    with open(out,'w',encoding='utf-8') as f:
        for s in strs:
            f.write(s+'\n')
    print(path, len(strs))
