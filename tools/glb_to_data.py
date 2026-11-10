# GLB（Tripoなどで作った銃の3Dモデル）から「形のデータだけ」を取り出し、index.html に貼る文字列にする。
#   使い方: python3 -I tools/glb_to_data.py 入力.glb 名前 [--rot 度] [--axis x|z]
#   出力  : window.<名前>_POS（float32）と window.<名前>_IDX（uint16）の2行（base64）
#   処理  : ①z軸まわりに --rot 度 回す ②長さを1.0にそろえ、長さ方向の中心を0・最も低い点を y=0・横の中心を0にする
#           ③同じ位置の頂点をまとめる（色や法線は捨てる。色はゲーム側で部位ごとに付ける）
import sys, json, struct, base64, argparse
import numpy as np
CT = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {'SCALAR': 1, 'VEC3': 3}

def load(path):
    d = open(path, 'rb').read(); assert d[:4] == b'glTF'
    off, js, bn = 12, None, None
    while off < len(d):
        l, t = struct.unpack('<II', d[off:off + 8]); c = d[off + 8:off + 8 + l]; off += 8 + l
        if t == 0x4E4F534A: js = json.loads(c)
        elif t == 0x004E4942: bn = c
    return js, bn

def acc(js, bn, i):
    a = js['accessors'][i]; bv = js['bufferViews'][a['bufferView']]; dt = CT[a['componentType']]; n = NC[a['type']]
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0); sz = np.dtype(dt).itemsize; stride = bv.get('byteStride', 0) or n * sz
    raw = np.frombuffer(bn, dtype=np.uint8, offset=off, count=stride * (a['count'] - 1) + n * sz)
    return np.lib.stride_tricks.as_strided(raw, (a['count'], n * sz), (stride, 1)).copy().view(dt).reshape(a['count'], n)

def convert(path, rot=0.0, axis='x'):
    js, bn = load(path)
    pr = js['meshes'][0]['primitives'][0]
    P = acc(js, bn, pr['attributes']['POSITION']).astype(np.float64); I = acc(js, bn, pr['indices']).astype(np.int64).reshape(-1)
    if rot:
        c, s = np.cos(np.radians(rot)), np.sin(np.radians(rot)); P = np.stack([c * P[:, 0] - s * P[:, 1], s * P[:, 0] + c * P[:, 1], P[:, 2]], 1)
    k = 0 if axis == 'x' else 2
    L = P[:, k].max() - P[:, k].min(); P = P / L
    P[:, k] -= (P[:, k].max() + P[:, k].min()) / 2; P[:, 1] -= P[:, 1].min()
    o = 2 - k; P[:, o] -= (P[:, o].max() + P[:, o].min()) / 2
    q = np.round(P * 1e5).astype(np.int64); _, first, inv = np.unique(q, axis=0, return_index=True, return_inverse=True)
    inv = inv.reshape(-1); P2 = P[first]; T = inv[I].reshape(-1, 3)
    T = T[(T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])]
    used = np.unique(T); remap = -np.ones(len(P2), np.int64); remap[used] = np.arange(len(used))
    return P2[used].astype(np.float32), remap[T].astype(np.uint16).reshape(-1)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('glb'); ap.add_argument('name'); ap.add_argument('--rot', type=float, default=0.0); ap.add_argument('--axis', default='x')
    ap.add_argument('--raw', help='数値確認用: 配列をnpzで保存')
    a = ap.parse_args(); P, T = convert(a.glb, a.rot, a.axis)
    assert len(P) < 65536, 'uint16に入らない'
    if a.raw: np.savez(a.raw, P=P, T=T)
    print(f'window.{a.name}_POS="{base64.b64encode(P.tobytes()).decode()}";')
    print(f'window.{a.name}_IDX="{base64.b64encode(T.tobytes()).decode()}";')
    print(f'// verts {len(P)} tris {len(T)//3}', file=sys.stderr)
