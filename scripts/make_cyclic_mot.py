#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将 .mot 周期化：首尾混合 + 重采样，使 state(0)≈state(T)
用法：
  python scripts/make_cyclic_mot.py \
    --in data/opensim/motions_raw/walk.mot \
    --out data/opensim/motions_cyclic/walk_cyclic.mot \
    --period 1.0 --blend 0.08 --fps 120
"""
import argparse, numpy as np, pandas as pd

def blend_loop(df, time_col, blend=0.08):
    w = max(int(len(df)*blend), 2)
    head = df.head(w).copy().reset_index(drop=True)
    tail = df.tail(w).copy().reset_index(drop=True)
    for c in df.columns:
        if c == time_col:
            continue
        a = tail[c].values
        b = head[c].values
        alpha = np.linspace(0,1,w)
        tail[c] = (1-alpha)*a + alpha*b
    return pd.concat([df.iloc[:-w], tail], axis=0)

def resample(df, time_col, fps=120, period=1.0):
    t0 = df[time_col].iloc[0]
    t  = np.linspace(t0, t0+period, int(period*fps)+1)
    out = pd.DataFrame({time_col: t})
    for c in df.columns:
        if c == time_col: continue
        out[c] = np.interp(t, df[time_col].values, df[c].values)
    out.iloc[-1] = out.iloc[0]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='fin', required=True)
    ap.add_argument('--out', dest='fout', required=True)
    ap.add_argument('--period', type=float, default=1.0)
    ap.add_argument('--blend', type=float, default=0.08)
    ap.add_argument('--fps', type=int, default=120)
    args = ap.parse_args()

    df = pd.read_table(args.fin, comment='#', sep=r'\s+')
    time_col = df.columns[0]
    df2 = blend_loop(df, time_col, blend=args.blend)
    df3 = resample(df2, time_col, fps=args.fps, period=args.period)

    with open(args.fout, 'w', encoding='utf-8') as f:
        f.write("# OpenSim compatible MOT (cyclic)\n")
        f.write(f"nRows={len(df3)} nColumns={len(df3.columns)}\n")
        df3.to_csv(f, sep='\t', index=False)

    print(f"✅ Saved cyclic MOT → {args.fout}")

if __name__ == '__main__':
    main()
