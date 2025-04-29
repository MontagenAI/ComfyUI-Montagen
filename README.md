# ComfyUI-Montagen


*ComfyUI Video Studio with Node-Controlled Timelines for Multi-Task Production.*

## Updates

### [[0.2.2]](/CHANGELOG.md) - 2025-04-29

*Feature Update: Audio Generator and List Adapter Support.*

![Montagen ScreenShot](assets/montagen0.2.1.png)


## Key Features

### 🎞️  Node-Controlled Timeline Architecture

- Parameterized Timeline Setup
  - Set resolution/FPS via `Create Timeline` nodes
  - Initiate batch rendering with `Execute Timeline` nodes 
  - Deep integration between node workflows and video timelines
- Bi-Directional Metadata Sync
  - Real-time synchronization between node parameters and timeline properties
  - Reverse-tweak generated content via editor-side adjustments

### 🖥️ Integrated Production Workspace

- Unified Preview
  - Timeline visualization embedded in ComfyUI interface 
  - Asset preview through `Editor` and `Player` component
- Structured Project System
  - Standard directory templates (`assets/`/`workflows/`/`timelines/`)
  - Hybrid protocol support (Local/HTTP/SMB/FTP) for unified resource management

### 🚀 Batch Production Pipeline

- Multi-Timeline Rendering
  - Each timeline produces one video
  - Centralized output management via `builds/` directory
- Prebuilt Scenarios (In Development)
  - Digital human video synthesis
  - Batch processing templates
  - Novel-to-video automation


## Get Started with a Template

![Montagen ScreenShot](assets/montagen0.2.1_1.png)

![Montagen ScreenShot](assets/montagen0.2.1_2.png)


## Custom Workflow

### Step 1, Open Project

1. Select `Montagen` icon from ComfyUI Activity Bar, to display Montagen Explorer.
2. Start from `default` project, or click `Browse project` to enter custom project folder path.
3. Click `Open project` to open recent project.

### Step 2, Create Timeline

1. Add `Create Timeline` node and set up timeline paramters.
2. Add `Adapter` nodes, set up paramters, and connect to the `Create Timeline` node.
3. Run workflow to create timeline.

### Step 3, Timeline Editing

1. Select timeline from project Explorer panel, to display timeline `Editor` and `Player`.
2. Select specify clip and open `Clips` and `Properties` Explorer panel, to display the clip's metadata.
3. Edit with timeline or `Properties` panel, to update the timeline.

### Step 4, Timeline Rendering

1. Add `Execute Timeline` node and set up file name, and connect to the `Create Timeline` node.
2. Run workflow to rendering timeline.
3. Select `builds/` from project Explorer panel, and preview output files.


## Installation

### Install via ComfyUI-Manager

* Search ComfyUI-Montagen in ComfyUI-Manager and click Install button.

### Manual Install

To install ComfyUI-Montagen in addition to an existing installation of ComfyUI, you can follow the following steps:

1. Goto `ComfyUI/custom_nodes` dir in terminal (cmd)
2. `git clone https://github.com/MontagenAI/ComfyUI-Montagen.git`
3. Restart ComfyUI.


## Acknowledgments

- Base on the project of [FFCreator](https://github.com/tnfe/FFCreator). And inspired by the examples of [miravideo](https://github.com/miravideo).
- Reference portions of media loading/preview code from [ComfyUI-VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite) into our custom node implementation.
- Reference EdgeTTS code from [ComfyUI-EdgeTTS](https://github.com/1038lab/ComfyUI-EdgeTTS) into our custom node implementation.