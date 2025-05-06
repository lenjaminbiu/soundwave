# Sound Waveform Generator
# Copyright (C) 2025 Benjamin Liu
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# Metadata for Blender Addon
bl_info = {
    "name": "Sound Waveform Generator",
    "author": "Benjamin Liu",
    "version": (1, 0, 0), # Update version as needed
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Sound Waveform Tab",
    "description": "Generates a 3D mesh from an audio file's waveform.",
    "warning": "REQUIRED: Install 'librosa' library in Blender's Python before enabling! (See instructions)", # Make it prominent!
    "doc_url": "", # Link to your instructions (GitHub page, etc.)
    "category": "Add Mesh",
}

import bpy
import numpy as np # Useful for array operations, often comes with Blender or librosa
import os

# Attempt to import librosa, provide guidance if it fails
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("Sound Waveform Generator: librosa library not found.")
    print("Please install it using Blender's Python.")
    # Add more detailed instructions here or in documentation later

# --- Properties ---
class SoundWaveformProperties(bpy.types.PropertyGroup):
    """Stores the addon's settings"""

    filepath: bpy.props.StringProperty(
        name="Audio File",
        description="Path to the audio file (WAV, MP3, etc.)",
        subtype='FILE_PATH',
        maxlen=1024,
        default="",
    )

    resolution: bpy.props.IntProperty(
        name="Resolution",
        description="Number of samples to take along the waveform (higher = more detail, more vertices)",
        default=1000,
        min=10,
        max=100000, # Set a reasonable upper limit
    )

    scale_x: bpy.props.FloatProperty(
        name="Scale X (Time)",
        description="Scaling factor for the time axis",
        default=1.0,
        min=0.01,
    )

    scale_y: bpy.props.FloatProperty(
        name="Scale Y (Amplitude)",
        description="Scaling factor for the amplitude axis",
        default=1.0,
        min=0.01,
    )

    scale_z: bpy.props.FloatProperty(
        name="Scale Z (Depth/Stereo)",
        description="Scaling factor for depth or stereo separation",
        default=0.2, # Often needs less scale than Y
        min=0.0,
    )

    vis_style: bpy.props.EnumProperty(
        name="Visualization Style",
        description="How the waveform is represented geometrically",
        items=[
            ('LINEAR', "Linear", "Time on X, Amplitude on Y, Depth on Z"),
            ('RADIAL', "Radial", "Time as Angle, Amplitude as Radius offset"),
            ('SPIRAL', "Spiral", "Time as Angle and Radius, Amplitude on Z"),
        ],
        default='LINEAR',
    )

    stereo_handling: bpy.props.EnumProperty(
        name="Stereo Handling",
        description="How to handle stereo audio files",
        items=[
            ('MONO', "Mono (Average)", "Average left and right channels"),
            # ('SEPARATE', "Separate Objects", "Create one object per channel"), # More complex
            ('Z_AXIS', "Use for Z-Depth", "Use second channel for Z displacement/thickness (Linear only)"),
            # ('IGNORE', "Ignore Second Channel", "Only use the first channel"),
        ],
        default='MONO',
    )

    normalize_amp: bpy.props.BoolProperty(
        name="Normalize Amplitude",
        description="Scale amplitude values to fit between -1.0 and 1.0 before applying Scale Y/Z",
        default=True,
    )

    mesh_thickness: bpy.props.FloatProperty(
        name="Mesh Thickness",
        description="Thickness of the generated ribbon/mesh (used in Linear/Radial)",
        default=0.1,
        min=0.0,
    )

# --- Operator ---
class SOUNDWAVEFORM_OT_generate(bpy.types.Operator):
    """Generates the waveform mesh based on current settings"""
    bl_idname = "soundwaveform.generate"
    bl_label = "Generate Waveform Mesh"
    bl_options = {'REGISTER', 'UNDO'} # Enable Undo

    @classmethod
    def poll(cls, context):
        # Only allow running if librosa is available and a file is selected
        props = context.scene.soundwaveform_props
        return LIBROSA_AVAILABLE and props.filepath != "" and os.path.exists(props.filepath)

    def execute(self, context):
        if not LIBROSA_AVAILABLE:
            self.report({'ERROR'}, "Librosa library not found. Please install it in Blender's Python environment.")
            return {'CANCELLED'}

        props = context.scene.soundwaveform_props
        filepath = bpy.path.abspath(props.filepath) # Ensure absolute path

        if not os.path.exists(filepath):
            self.report({'ERROR'}, f"File not found: {filepath}")
            return {'CANCELLED'}

        print(f"Loading audio from: {filepath}")

        try:
            # Load audio file using librosa
            # sr=None loads at original sample rate, then we resample/downsample later
            # mono=False preserves channels
            audio_data, sample_rate = librosa.load(filepath, sr=None, mono=False)
            print(f"Loaded audio: {audio_data.shape}, Sample Rate: {sample_rate}")

            # Handle stereo/mono
            if audio_data.ndim > 1: # Stereo
                if props.stereo_handling == 'MONO':
                    audio_data = librosa.to_mono(audio_data)
                    print("Converted to Mono (Averaged)")
                elif props.stereo_handling == 'Z_AXIS' and props.vis_style == 'LINEAR':
                    # Keep both channels for Linear Z-axis mode
                    pass
                else: # Default to using only the first channel if stereo mode not applicable
                    audio_data = audio_data[0]
                    print("Using only first channel")
            else: # Already mono
                 print("Audio is Mono")


            # --- Data Processing ---
            num_total_samples = audio_data.shape[-1] # Get length from last dimension
            target_resolution = props.resolution

            # Ensure resolution is not higher than available samples
            if target_resolution > num_total_samples:
                target_resolution = num_total_samples
                print(f"Warning: Resolution capped at available samples: {num_total_samples}")

            # Calculate step size for downsampling
            step = num_total_samples // target_resolution
            if step == 0: step = 1 # Avoid division by zero if resolution > samples

            # Downsample (take average over windows or just pick samples)
            # Simple approach: pick every 'step' sample
            indices = np.arange(0, num_total_samples, step)

            if audio_data.ndim > 1 and props.stereo_handling == 'Z_AXIS' and props.vis_style == 'LINEAR':
                 sampled_data_l = audio_data[0, indices]
                 sampled_data_r = audio_data[1, indices]
                 # Optionally normalize each channel independently
                 if props.normalize_amp:
                     sampled_data_l = librosa.util.normalize(sampled_data_l)
                     sampled_data_r = librosa.util.normalize(sampled_data_r)
            else:
                # Handle mono or cases where we only care about one effective channel
                if audio_data.ndim > 1: # If stereo but handled as mono/first channel earlier
                    sampled_data = audio_data[0, indices] if props.stereo_handling != 'MONO' else librosa.to_mono(audio_data)[indices]
                else: # Already mono
                    sampled_data = audio_data[indices]

                if props.normalize_amp:
                    sampled_data = librosa.util.normalize(sampled_data)


            print(f"Downsampled to {len(indices)} points.")

            # --- Mesh Generation ---
            verts = []
            edges = []
            faces = []
            num_verts = len(indices)

            # Get scales
            sx, sy, sz = props.scale_x, props.scale_y, props.scale_z
            thickness = props.mesh_thickness

            if props.vis_style == 'LINEAR':
                has_stereo_z = audio_data.ndim > 1 and props.stereo_handling == 'Z_AXIS'

                for i in range(num_verts):
                    t = (i / (num_verts - 1)) if num_verts > 1 else 0.5 # Normalized time (0 to 1)
                    x = t * sx

                    if has_stereo_z:
                        amp_l = sampled_data_l[i] * sy
                        amp_r = sampled_data_r[i] * sz # Use second channel for z-offset/thickness
                        # Create two vertices per sample for thickness based on right channel
                        verts.append((x, amp_l, -amp_r * 0.5)) # Left channel Y, Right channel Z (bottom)
                        verts.append((x, amp_l,  amp_r * 0.5)) # Left channel Y, Right channel Z (top)
                    else:
                        amp = sampled_data[i] * sy
                        # Create two vertices per sample for fixed thickness
                        verts.append((x, amp, -thickness * 0.5 * sz)) # Bottom edge
                        verts.append((x, amp,  thickness * 0.5 * sz)) # Top edge

                # Create edges and faces for the ribbon
                for i in range(num_verts - 1):
                    v_idx = i * 2
                    # Edges along the waveform shape
                    edges.append((v_idx, v_idx + 2))         # Bottom edge segment
                    edges.append((v_idx + 1, v_idx + 3))     # Top edge segment
                    # Edges connecting top/bottom (for thickness) - optional visually
                    # edges.append((v_idx, v_idx + 1))
                    # edges.append((v_idx + 2, v_idx + 3))

                    # Create faces (quads)
                    faces.append((v_idx, v_idx + 2, v_idx + 3, v_idx + 1))

            elif props.vis_style == 'RADIAL':
                center_offset = 1.0 # Base radius
                for i in range(num_verts):
                    angle = (i / num_verts) * 2 * np.pi # Angle based on time (0 to 2*pi)
                    amp = sampled_data[i] * sy
                    radius = center_offset + amp # Modulate radius by amplitude

                    # Calculate base position on circle
                    base_x = np.cos(angle) * radius * sx # Apply X scale to radius calculation
                    base_y = np.sin(angle) * radius * sx # Apply X scale to radius calculation

                    # Add thickness along Z
                    z_offset = thickness * 0.5 * sz
                    verts.append((base_x, base_y, -z_offset))
                    verts.append((base_x, base_y,  z_offset))

                 # Create edges and faces for the radial ribbon (similar logic to linear, connecting pairs)
                for i in range(num_verts):
                    v_idx = i * 2
                    next_v_idx = ((i + 1) % num_verts) * 2 # Wrap around for the last segment

                    # Faces (quads connecting current pair to next pair)
                    faces.append((v_idx, next_v_idx, next_v_idx + 1, v_idx + 1))


            elif props.vis_style == 'SPIRAL':
                revolutions = 5.0 # Number of turns in the spiral
                max_radius = 1.0 * sx # Spiral max radius controlled by X scale

                for i in range(num_verts):
                    norm_time = (i / (num_verts - 1)) if num_verts > 1 else 0.5 # Normalized time (0 to 1)
                    angle = norm_time * 2 * np.pi * revolutions
                    radius = norm_time * max_radius
                    amp = sampled_data[i] * sy # Amplitude controls Z

                    x = np.cos(angle) * radius
                    y = np.sin(angle) * radius
                    z = amp * sz # Use Z scale for amplitude mapping

                    verts.append((x, y, z))

                # Create edges for the spiral line
                for i in range(num_verts - 1):
                    edges.append((i, i + 1))
                # No faces for a simple spiral line, could add thickness later

            # --- Create Blender Object ---
            mesh_name = os.path.splitext(os.path.basename(filepath))[0] + "_Waveform"
            mesh = bpy.data.meshes.new(name=mesh_name)

            if not verts:
                 self.report({'WARNING'}, "No vertices generated. Check audio file and settings.")
                 return {'CANCELLED'}

            mesh.from_pydata(verts, edges, faces)
            mesh.update() # Calculate normals, etc.

            obj_name = mesh_name
            obj = bpy.data.objects.new(obj_name, mesh)

            # Link object to the scene
            context.collection.objects.link(obj)
            # Select and make active
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj

            self.report({'INFO'}, f"Generated waveform mesh '{obj_name}'")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to process audio or generate mesh: {e}")
            import traceback
            traceback.print_exc() # Print detailed error to Blender console
            return {'CANCELLED'}


# --- Panel ---
class SOUNDWAVEFORM_PT_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Waveform Generator"
    bl_idname = "SOUNDWAVEFORM_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Sound Waveform' # Tab name in the N-Panel
    bl_context = "objectmode" # Only show in object mode

    def draw_header(self, context):
         self.layout.label(text="", icon='SPEAKER')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.soundwaveform_props # Get properties

        layout.label(text="Input Audio:")
        layout.prop(props, "filepath")

        if not LIBROSA_AVAILABLE:
             box = layout.box()
             box.label(text="Librosa library not found!", icon='ERROR')
             box.label(text="Install it via Blender Preferences > Add-ons")
             box.label(text="or manually in Blender's Python.")
             # You could add an operator button here to *try* installing it via pip
             # but that's more advanced (requires pip availability, permissions etc.)
             return # Don't draw the rest if librosa is missing

        if props.filepath == "" or not os.path.exists(bpy.path.abspath(props.filepath)):
            layout.label(text="Please select a valid audio file.", icon='INFO')
        else:
            layout.separator()
            layout.label(text="Generation Settings:")
            col = layout.column(align=True)
            col.prop(props, "resolution")
            col.prop(props, "vis_style")
            col.prop(props, "normalize_amp")

            if props.vis_style == 'LINEAR':
                 col.prop(props, "stereo_handling", text="Stereo") # Only show relevant stereo options
                 col.prop(props, "mesh_thickness", text="Z-Thickness")
            elif props.vis_style == 'RADIAL':
                 col.prop(props, "mesh_thickness", text="Z-Thickness")
            # No specific options for Spiral currently


            layout.separator()
            layout.label(text="Scaling:")
            row = layout.row(align=True)
            row.prop(props, "scale_x", text="X (Time/Shape)")
            row.prop(props, "scale_y", text="Y (Amplitude)")
            if props.vis_style != 'RADIAL': # Z scale used differently in Radial
                row.prop(props, "scale_z", text="Z (Depth/Amp)")
            else:
                row.prop(props, "scale_z", text="Z (Thickness)")


            layout.separator()
            # Use the operator's poll() method to grey out the button if conditions not met
            op_layout = layout.operator(SOUNDWAVEFORM_OT_generate.bl_idname, icon='MOD_WAVE')
            # op_layout.enabled = LIBROSA_AVAILABLE and props.filepath != "" # Redundant if poll() is used

# --- Registration ---
classes = (
    SoundWaveformProperties,
    SOUNDWAVEFORM_OT_generate,
    SOUNDWAVEFORM_PT_panel,
)

def register():
    print("Registering Sound Waveform Generator Addon")
    for cls in classes:
        bpy.utils.register_class(cls)
    # Store properties in the Scene
    bpy.types.Scene.soundwaveform_props = bpy.props.PointerProperty(type=SoundWaveformProperties)

def unregister():
    print("Unregistering Sound Waveform Generator Addon")
    # Important to delete PointerProperty before unregistering the PropertyGroup
    del bpy.types.Scene.soundwaveform_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    # Allows running the script directly in Blender Text Editor for testing
    # Unregister existing if necessary before registering
    try:
        unregister()
    except:
        pass
    register()