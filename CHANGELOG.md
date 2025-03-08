# ComfyUI-Montagen Changelog

Objective: Build a ComfyUI-based video editing framework.

## [0.1.2] - 2025-03-07

**Feature Update: Better Project Manipulation With New Directory Hierarchy.**

### Changed

- [UI] Enhanced Project Panel: Display the project hierarchy, including the workflows and clips within each project, with full manipulation.(#14)
- [UI] ComfyUI Tab Sync: Synchronize the state of items between Project Panel and ComfyUI Tabs.(#16)
- [UI] Workflow As Directory: `Add` or `Edit` clips in the specified original workflow instead of opening a new workflow.(#18)

### Fixed

- [UI] Keyboard Letter Conflict: When input 'a', 's' key, it's not working.(#5)


## [0.1.1] - 2025-03-01

**Feature Update: Alpha Channel Support, Properties Panel, And Other Enhancements.**

### Added

- [UI] Easier Navigation: Click top-left `ComfyUI` or `Montagen`, to switch between the two pages.(#6)
- [UI] Add `Properties` Panel: Support basic transform controls (`rotate`, `x`, `y`, `width`, `height`) for image and video clips.(#4)
- [Editor] Add Text Clip Type: With addtional property `text` on `Properties` panel.(#7)
- [Editor] Add `STICKER` Track Type: Support `gif` image clip as a sticker.(#13)

### Changed

- [Node] Alpha Channel Support: Add alpha input and output to `Clip Adapter` nodes.(#8)
  - `Image Clip Adapter`: Add `preview_fps` parameter, working with alpha input to generate a `gif` image clip, as a special type on `STICKER` track.
  - `Video Clip Adapter`: Working with alpha input to generate a `webm` video clip, as a common video type.
- [UI] Move `Projects` To Header In `Montagen`:(#10)


## [0.1.0] - 2025-02-22

### Added

**Initial Release: Core Video Editing Features for ComfyUI.**

- [Core] The Structural Mapping Between ComfyUI and Montagen:
  - ComfyUI Workflows & Montagen Project: Combine multiple ComfyUI workflows into a structured timeline project for seamless video editing. Each workflow can be linked to only one Montagen project and cannot be shared across projects.
  - ComfyUI Node & Montagen Clip: Within a ComfyUI workflow, a node's media output is linked to a `Clip Adapter` node, making it a media clip in a Montagen timeline project. A workflow can generate multiple independent clips, each editable separately.
- [Node] Clip Adapter:    
  Input: `[images | images | audio]`.   
  Output: `<optional>` original input.   
  Parameters: `name` (Clip identifier), `projectId` (No need to change).   
  After ComfyUI workflow execution is complete, press `Preview` to open the Montagen UI. Types of `Clip Adapter` nodes:
  - `Image Clip Adapter`: Montagen image clip.
  - `Video Clip Adapter`: Set `preview_fps` to use image sequence as a Montagen video clip.
  - `Audio Clip Adapter`: Montagen audio clip.
- [UI] Montagen UI: Unified Montagen UI (`Navigation System`, `Project Tabs`, `Editor`, `Player`) based on the ComfyUI layout.
  - Project Tabs: Each project opens in a dedicated tab, with each tab containing both an `Editor` and a `Player`.
- [UI] Navigation System: The system includes all functional components, with new features being added to the navigation bar.
  - `Projects`: Manage multiple projects, including `Create`, `Open`, `Delete`.
  - `Clips`: Clips list of the project.
  - `Export`: Export the project as a video file.
- [Editor] Core Video Editing Components:
  - Timeline Container: Basic component (`Time Ruler`, `Playhead`, `Hover Indicator`, `Zoom in/Out`). Supports multiple tracks to organize different clip types.
  - Track Management: Track type (`Text`, `Audio`, `Video & Image`) for specific clips. With control of `Mute`, `Hide/Show` for specific type of tracks.
  - Clip Creation: Start by using dedicated `Create` actions (`Create Image`, `Create Video`, `Create Audio`) to generate an empty clip. 
  - Clip Editing: Seamlessly integrate clip with corresponding ComfyUI workflow for further editing through `Edit Workflow`.
  - Basic Clip Manipulation: Supports `Select`, `Hide/Show`, `Delete` for single clip edit. And `Drag & Drop`, `Snap` clip within and across tracks.
- [Player] Core Video Editing Components:
  - Transform Controls: `Position`, `Scale`, `Rotation`. Directly manipulate video clips in the Player viewport with real-time preview. 

### Changed

- [Editor] Frame Locate & Preview: Requires clicking the clip (instead of hovering) to preview and locate a frame.
  
### Removed

- [Node] `Preview Images`: Deprecated, replaced by `Video Clip Adapter`.
- [UI] Media Panel & Metadata Panel: Placeholder panels removed for cleaner UI. Replaced by Navigation System.


## [0.0.1] - 2025-01-25

### Added

**Technical Validation: A ComfyUI Custom Node for Image Sequence Preview with a Timeline Component.**

- [Node] `Preview Images`: Input images, output (optional) the input images. Set 'FPS', and click 'Preview' button to open the Montagen UI with image sequence.
- [UI] Montagen UI Draft: A classic video editor layout (`Media Panel`, `Metadata Panel`, `Editor`, `Player`).
- [UI] Media Panel & Metadata Panel: Useless placeholders for future development.
- [Editor] Basic Timeline Controls: Hover over the clip to preview and precisely locate a frame. Or press the space key to start playback in `Player`.
- [Player] Basic Video Player: Simple media playback functionality.
