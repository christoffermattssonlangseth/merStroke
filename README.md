# Stroke brain — MERSCOPE (Fan / CG) spatial pipeline

Cell segmentation, quantification and clustering for the **Stroke MERSCOPE (Fan / CG)** run:
a targeted **500-gene** panel across 51 tissue regions (49 brain / stroke sections + 2 spinal cord).
Segmentation is done with [Baysor](https://github.com/kharchenkolab/Baysor) (optionally seeded by
Cellpose-SAM nuclei), quantified into AnnData `.h5ad`, and clustered with scanpy.

## Data layout

Large data lives **outside** the repo (nothing here is committed to git):

```
/Volumes/T7/Stroke_merscop_Fan_CG/
├── transcript files/            # raw MERSCOPE detected_transcripts CSVs (one per region)
├── baysor_segmentation/<sample>/m50_s4/   # Baysor outputs (segmentation.csv, *_cell_stats.csv, ...)
└── h5ad/                        # per-region <sample>.h5ad + concatenated stroke_all / sc_all
/Users/christoffer/Downloads/dapi/         # full-res MERSCOPE DAPI mosaics (.tif per region)
```

Baysor parameter tag: **`m50_s4`** (`min_molecules_per_cell=50`, `scale=4`).

## Pipeline

Run in this order. Paths are hard-coded to the locations above; each stage is **re-run safe**
(skips finished regions; clustering only ever writes new `*_clustered.h5ad`).

| # | Notebook | Kernel | What it does |
|---|----------|--------|--------------|
| 1 | `notebooks/cellpose_sam_dapi.ipynb` | `Python (sopa)` | Cellpose-SAM nuclear segmentation of DAPI mosaics → nuclei to use as a Baysor prior (GPU/MPS). Optional. |
| 2 | `notebooks/baysor_stroke_batch.ipynb` | `Baysor-16-Threads` (Julia) | Batch Baysor cell segmentation on the transcript CSVs. |
| 3 | `notebooks/baysor_stroke_to_h5ad.ipynb` | `sc` | Per-region `segmentation.csv` → cell × gene `<sample>.h5ad`; concat → `stroke_all.h5ad` (excludes the 2 SC samples). |
| 4 | `notebooks/attach_dapi_to_adata.ipynb` | `Python (sopa)` | Attach a downsampled DAPI thumbnail per region into each `.h5ad` for spatial viewing (visualization-grade registration). |
| 5 | `notebooks/baysor_stroke_clustering.ipynb` | `sc` | QC → normalize/log1p → PCA → neighbors → Leiden → UMAP → markers → `stroke_all_clustered.h5ad`. |
| 6 | `notebooks/spinalcord_to_h5ad_and_cluster.ipynb` | `sc` | Same build + cluster pipeline for the 2 spinal cord regions → `sc_all.h5ad` / `sc_all_clustered.h5ad`. |

The two spinal cord regions (`SC_uninjured_1`, `SC_uninjured_2`) are handled separately from the brain /
stroke sections throughout (steps 3, 5 exclude them; step 6 covers them).

## Environments

- **`sc`** — conda env with scanpy / anndata / pandas / numpy (quantification + clustering).
- **`Python (sopa)`** — has tifffile + zarr + anndata (DAPI streaming / registration).
- **`Baysor-16-Threads`** — Julia kernel with Baysor installed at `/Users/christoffer/Baysor`.

## Repo structure

```
notebooks/   analysis notebooks (outputs stripped on commit — see .gitattributes)
scripts/     helper scripts, e.g. _concat_nonsc.py (fast re-concat of per-region h5ads)
```

> Notebook outputs are stripped via `nbstripout` (configured in `.gitattributes`). To enable the
> filter in a fresh clone: `nbstripout --install --attributes .gitattributes`.
