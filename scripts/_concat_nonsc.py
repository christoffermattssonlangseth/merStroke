"""Fast rebuild of stroke_all.h5ad from the existing per-region h5ads, excluding
the two spinal cord samples. Skips re-reading the giant segmentation CSVs.

Sample set is derived the same way as baysor_stroke_to_h5ad.ipynb (glob the Baysor
segmentation dirs, drop SC_SAMPLES) so it stays in sync with that notebook.
"""
from pathlib import Path
import numpy as np
import anndata as ad

seg_root  = Path("/Volumes/T7/Stroke_merscop_Fan_CG/baysor_segmentation")
param_tag = "m50_s4"
out_dir   = Path("/Volumes/T7/Stroke_merscop_Fan_CG/h5ad")
SC_SAMPLES = {"SC_uninjured_1", "SC_uninjured_2"}

# Discover finished non-SC regions (mirror notebook's find_outputs)
samples = []
for seg in sorted(seg_root.glob(f"*/{param_tag}/segmentation_segmentation.csv")):
    if seg.name.startswith("._"):
        continue
    sample = seg.parent.parent.name
    if sample in SC_SAMPLES:
        continue
    if seg.stat().st_size > 0 and (seg.parent / "segmentation_cell_stats.csv").exists():
        samples.append(sample)

print(f"Concatenating {len(samples)} non-SC regions (SC excluded).")

missing = [s for s in samples if not (out_dir / f"{s}.h5ad").exists()]
if missing:
    raise SystemExit(f"Missing per-region h5ads for: {missing}\n"
                     f"Run baysor_stroke_to_h5ad.ipynb (full) for these first.")

adatas = {}
for s in samples:
    a = ad.read_h5ad(out_dir / f"{s}.h5ad")
    adatas[s] = a
    print(f"  loaded {s:40s} cells={a.n_obs:7d} genes={a.n_vars}")

combined = ad.concat(adatas, join="outer", label="sample", index_unique=None)
combined.X = np.nan_to_num(combined.X)
out_path = out_dir / "stroke_all.h5ad"
combined.write_h5ad(out_path)
print(combined)
print(f"\nWrote {out_path}  ({combined.n_obs} cells, {combined.n_vars} genes)")
assert not combined.obs["sample"].isin(SC_SAMPLES).any(), "SC samples leaked in!"
print("Verified: no SC samples present.")
