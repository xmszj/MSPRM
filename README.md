# MSPRM — Mid-Sagittal Plane Registration Module for 3D Slicer

A 3D Slicer extension for fast, semi-automatic alignment of medical image volumes (CT/MR) based on the **Mid-Sagittal Plane (MSP)**.

## Overview

MSPRM provides an interactive workflow for registering two volumetric images by leveraging the anatomical mid-sagittal plane as a registration reference. The module uses 3D Slicer's built-in Multi-Planar Reconstruction (MPR) crosshair views to define the MSP for both the moving and fixed images, then computes a rigid transformation to align them.

### Key Features

- **MSP-based rigid registration** — Aligns moving image to fixed image using the mid-sagittal plane as the common reference.
- **Interactive MPR crosshair** — Toggle crosshair lines on/off to precisely position the sagittal plane in both volumes.
- **Fit-to-view layout** — Switch between a custom expanded MPR layout and the standard 3-slice view.
- **Fusion preview with opacity slider** — Overlay the fixed and moving images with adjustable transparency for visual verification.
- **Interactive manual refinement** — After automatic registration, fine-tune the alignment using interactive rotation/translation handles on a fiducial point placed at the volume center.
- **One-click apply** — Harden the transform onto the volume and clean up all intermediate nodes in a single step.

## Requirements

- [3D Slicer](https://download.slicer.org/) (tested on 5.x)
- Python 3 (bundled with 3D Slicer)
- NumPy (bundled with 3D Slicer)
- VTK (bundled with 3D Slicer)

## Installation

### Option 1: Manual install

1. Download or clone this repository.
2. Copy the `MSPRM` folder into your 3D Slicer extensions directory, or place it anywhere on disk.
3. In 3D Slicer, open **Edit → Application Settings → Modules → Additional module paths** and add the path to the `MSPRM` folder.
4. Restart 3D Slicer. The module will appear under the **Modules → Tools** category as **MSPRM**.

### Option 2: Clone directly

```bash
git clone https://github.com/xmszj/MSPRM.git
```

Then follow steps 3–4 above.

## Usage

### Step 1 — Load Images

Load your fixed and moving volumes (CT or MR) into 3D Slicer via the **Add Data** dialog.

### Step 2 — Select Volumes

Open the **MSPRM** module. In the panel:

- **Moving image** — Select the volume you want to transform.
- **Fixed image** — Select the reference volume that stays in place.

### Step 3 — Enable Crosshair

Click the **Crosshair** button to toggle the MPR intersecting slice lines on. Use these lines to visually identify the mid-sagittal plane in each volume.

- Use the **Fit to view** button to switch to an expanded layout for better visibility if needed.

### Step 4 — Confirm MSP for Each Volume

1. Navigate to the slice view where the crosshair represents the mid-sagittal plane for the **moving** image.
2. Click **Confirm MSP** next to the Moving image selector.
3. Repeat for the **fixed** image — navigate to its mid-sagittal plane and click **Confirm MSP** next to the Fixed image selector.

### Step 5 — Start Registration

Click **Start registration**. The module will:

1. Compute the rigid transformation that maps the moving image's MSP onto the fixed image's MSP.
2. Apply a correction matrix to restore anatomical orientation.
3. Harden the initial transform onto both volumes.
4. Set up the slice views (Axial / Coronal / Sagittal) for review.
5. Place an interactive fiducial point at the center of the moving volume for manual fine-tuning — drag the rotation/translation handles to adjust.

### Step 6 — Verify with Fusion

- Use the **Fusion opacity** slider to blend the fixed (foreground) and moving (background) images.
- Toggle the checkboxes next to each selector to switch which volume is displayed as the background.

### Step 7 — Apply Registration

Once satisfied with the alignment, click **Apply registration** to:

- Harden the current transform onto the moving volume.
- Remove all intermediate nodes (transform nodes, fiducial points).

## How It Works

The registration pipeline consists of three stages:

1. **MSP Capture** — The user positions the MPR crosshair at the mid-sagittal plane for each volume. The module records the slice-to-RAS matrix of the Yellow (sagittal) slice view as the MSP reference for each volume.

2. **Initial Alignment** — A correction matrix is applied to convert from the slice coordinate system back to anatomical (RAS) orientation. The inverse of each MSP matrix is used to bring both volumes into a canonical anatomical pose, achieving initial alignment.

3. **Manual Refinement** — A fiducial point with interactive handles is placed at the center of the moving volume. The user can rotate and translate the volume in 3D space by manipulating the handles. Changes are applied in real time via a VTK observer.

## File Structure

```
MSPRM/
├── MSPRM.py                  # Main module logic
├── .gitignore
├── README.md
└── Resources/
    ├── Icons/
    │   └── MSPRM.png         # Module icon
    └── UI/
        └── MSPRM.ui          # Qt UI file (built with Qt Designer)
```

## License

This project is intended for research and educational use. Please cite appropriately if used in published work.

## Author

**xmszj**

GitHub: [https://github.com/xmszj](https://github.com/xmszj)
