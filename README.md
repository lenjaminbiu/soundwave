# Sound Waveform Generator (Blender Addon)

Generates a 3D mesh object in Blender based on the waveform of an imported audio file (WAV, MP3, etc.).

![Example Screenshot (Optional - Add one later!)](/assets/screenshot.png)

## Features

*   Import common audio formats (WAV, MP3 - requires `ffmpeg` for MP3).
*   Generate 3D mesh from audio amplitude data.
*   Customizable Resolution: Control the detail level of the mesh.
*   Scaling: Adjust X (Time), Y (Amplitude), and Z (Depth/Stereo) scale.
*   Visualization Styles:
    *   Linear: Classic waveform shape.
    *   Radial: Waveform wrapped in a circle.
    *   Spiral: Waveform extruded along a spiral path.
*   Stereo Handling: Choose how to represent stereo audio (Mono average, use for Z-depth).
*   Optional Amplitude Normalization.
*   Adjustable Mesh Thickness for Linear/Radial styles.

## Installation

**⚠️ IMPORTANT PRE-REQUISITE: Installing the `librosa` Library ⚠️**

This addon **requires** the external Python library `librosa` to function. You MUST install it into Blender's Python environment *before* enabling the addon.

**Why?** `librosa` is a powerful library used for loading, analyzing, and manipulating audio files, which this addon relies on. Blender doesn't include it by default.

**How to Install `librosa` (Recommended Method: using `pip`)**

1.  **Find Blender's Python Executable:**
    *   **Windows:** Typically `C:\Program Files\Blender Foundation\Blender <Version>\<Version>\python\bin\python.exe` (Replace `<Version>` with your Blender version, e.g., `3.4`).
    *   **macOS:** Typically `/Applications/Blender.app/Contents/Resources/<Version>/python/bin/python3.10` (Right-click Blender.app -> Show Package Contents. The exact Python version number might vary).
    *   **Linux:** Often found in the extracted Blender folder: `./<blender_folder>/<version>/python/bin/python3.10` (The exact Python version number might vary).
    *   **Finding the Exact Path:** If you can't locate the Python executable, run this Python script in Blender's Text Editor (Editor Type > Text Editor):
        ```python
        import sys
        import os
        print(os.path.join(sys.prefix, "bin", "python.exe"))  # For Windows
        print(os.path.join(sys.prefix, "bin", "python3"))     # For macOS/Linux
        ```
        Use the output path for the following steps.

2.  **Open a Terminal or Command Prompt:**
    *   **Windows:** Search for `cmd` or `Command Prompt`.
    *   **macOS:** Search for `Terminal`.
    *   **Linux:** Use your distribution's default terminal.

3.  **Ensure `pip` is Available:** (Navigate to the directory containing `python.exe`/`python3.x` OR use the full path directly)
    *   Run: `<Full Path to Blender's Python> -m ensurepip`
    *   *Example (Windows):* `"C:\Program Files\Blender Foundation\Blender 3.4\3.4\python\bin\python.exe" -m ensurepip`
    *   *Example (macOS):* `/Applications/Blender.app/Contents/Resources/3.4/python/bin/python3.10 -m ensurepip`

4.  **Install `librosa`:**
    *   Run: `<Full Path to Blender's Python> -m pip install librosa`
    *   *Example (Windows):* `"C:\Program Files\Blender Foundation\Blender 3.4\3.4\python\bin\python.exe" -m pip install librosa`
    *   *Example (macOS):* `/Applications/Blender.app/Contents/Resources/3.4/python/bin/python3.10 -m pip install librosa`
    *   This will download and install `librosa` and its own dependencies (like `numpy`, `scipy`, `soundfile`, etc.) into Blender's Python site-packages.

5.  **(Potentially Required for MP3): Install `ffmpeg`**
    *   `librosa` often relies on the system tool `ffmpeg` to decode MP3 and other compressed formats.
    *   This must be installed separately on your operating system (it's *not* a Python package installed via pip).
    *   Download `ffmpeg` from [ffmpeg.org](https://ffmpeg.org/download.html) and follow their installation instructions for your OS (usually involves adding it to your system's PATH).

6.  **Restart Blender:** After installing `librosa` (and potentially `ffmpeg`), restart Blender completely.

**Installing the Addon Itself:**

1.  Download the latest release `sound_waveform_generator_vX.X.X.zip` file.
2.  Open Blender.
3.  Go to `Edit > Preferences... > Add-ons`.
4.  Click `Install...`.
5.  Navigate to where you downloaded the `.zip` file and select it. Click `Install Add-on`.
6.  Search for "Sound Waveform Generator" in the Add-ons list.
7.  **Enable the checkbox next to the addon name.** (Only do this *after* you have successfully installed `librosa`!).

## Usage

1.  Make sure the addon is enabled (see Installation steps).
2.  In the 3D Viewport, press `N` to open the Sidebar (if it's not already open).
3.  Look for a tab named **"Sound Waveform"**.
4.  Click the folder icon next to "Audio File" to browse and select your desired sound file (`.wav`, `.mp3`, etc.).
5.  Adjust the `Resolution`, `Visualization Style`, `Stereo Handling`, `Scale`, and other parameters as needed.
6.  Click the **"Generate Waveform Mesh"** button.
7.  A new mesh object representing the waveform will be created at the 3D cursor location and selected.

## Troubleshooting

*   **Addon doesn't appear or gives an error on activation:** You most likely haven't installed the `librosa` library correctly into Blender's Python environment. Please carefully follow the "Installing the `librosa` Library" steps above. Check Blender's System Console (`Window > Toggle System Console`) for specific error messages (e.g., `ModuleNotFoundError: No module named 'librosa'`).
*   **MP3 files don't load or cause errors:** Ensure you have installed `ffmpeg` correctly on your system and that it's accessible in your PATH environment variable. Again, check the System Console for errors.
*   **Generated mesh looks wrong/unexpected:** Double-check your `Scale` and `Resolution` settings. Very high resolutions can create very dense meshes. Experiment with different visualization styles and stereo handling options.

## License

This addon is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html) or later, compatible with Blender.

## Author

*   Benjamin Liu