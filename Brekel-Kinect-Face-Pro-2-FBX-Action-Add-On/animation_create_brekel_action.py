
# SUMMARY: Uses an imported FBX v7 binary from Brekel Kinect Face Pro
# 2 to create a Blender action and armature similar to the kind
# created by Brekel Kinect Face Pro 2 BVH export.

# COMPATABILITY: Tested with Blender v2.72 and 2.77a

# DOWNLOAD: Go to:
# https://github.com/gwbond/blender/blob/master/Brekel-Kinect-Face-Pro-2-FBX-Action-Add-On/animation_create_brekel_action.py
# and right-click on the 'Raw' button and select 'Save link as...' to
# download the file to your PC/Mac/Linux machine. Save the file as
# "animation_create_brekel_drivers.py"

# INSTALLATION: Install this add-on the usual way via User Preferences
# Addons "Install from File". Select the file you downloaded in the
# previous step. Once installed, this add-on is listed as "Create
# Brekel Kinect Face Pro 2 Action" in the "Animation" category.

# USAGE: Before using this add-on, import a Brekel Kinect Face Pro 2
# FBX v7 binary motion capture file. This will create a number of
# objects and actions. To create the new action and armature, invoke
# this add-on via the operator search dialog (press spacebar and
# search for "Create Brekel Action"). A new armature object named
# "Recording" will appear in the scene.

# BUGS/ENHANCEMENTS: Feel free report bugs, suggest enhancements or,
# even better, contribute changes to the code. It's hosted on github
# at:
# https://github.com/gwbond/blender/blob/master/Brekel-Kinect-Face-Pro-2-FBX-Action-Add-On/animation_create_brekel_actions.py

# LICENSE: GPL v2 or later

bl_info = {
    "name": "Create Brekel Kinect Face Pro 2 Action",
    "version": (1, 0),
    "location": 'Press spacebar and search for: "Create Brekel Action"',
    "category": "Animation",
}

import bpy

class CreateBrekelAction( bpy.types.Operator ):
    # Tooltip.
    """"Create Brekel Kinect Face Pro 2 Action"""
    # Unique internal identifier
    bl_idname = "object.create_brekel_action"
    # Interface display name.
    bl_label = "Create Brekel Action"
    # Enable "undo".
    bl_options = { 'REGISTER', 'UNDO' }

    def execute( self, context ):

        # Error checking.
        if not "Key|Take 001|Base Layer" in bpy.data.actions:
            self.report( { 'ERROR' },
                         "Must import an FBX v7 binary file exported by Brekel Pro Face 2." )
            return { 'CANCELLED' }

        # Create new armature similar to the kind created by Brekel
        # Pro Face 2 BVH export. Like the Brekel armature, this
        # armature includes bones for each shape key. Unlike the
        # Brekel armature, this armature excludes 'Head' and
        # 'Facejoint' bones.
        armature_data = bpy.data.armatures.new( "Recording" )
        armature_object = bpy.data.objects.new( "Recording", armature_data )

        # Link new armature into scene and select it in preparation
        # for adding bones to armature in edit mode.
        bpy.context.scene.objects.link( armature_object )
        bpy.context.scene.objects.active = armature_object
        armature_object.select = True

        # Activate edit mode in order to add bones to armature.
        bpy.ops.object.mode_set( mode = 'EDIT' )

        # Create new action for armature. 
        new_action = bpy.data.actions.new( name = "Recording" )
        new_action.id_root = 'OBJECT'
        new_action.use_fake_user = True

        # Get existing shape key f-curves from action created by
        # Brekel FBX export. F-curves for this action specify shape
        # key offset between 0 and 1.
        shape_key_fcurves = bpy.data.actions[ "Key|Take 001|Base Layer" ].fcurves

        # For each shape key, add an associated bone to the new
        # armature, and add an associated f-curve to the new armature
        # action. For each keyframe in original f-curve, create an
        # associated bone X-axis rotation keyframe in the new f-curve.
        num_shape_keys = 0
        for shape_key_fcurve in shape_key_fcurves :

            # Extract shape key name from f-curve data path e.g.,
            # shape key data path: key_blocks["Frown_L"].value
            shape_key_fcurve_data_path = shape_key_fcurve.data_path
            shape_key_name = shape_key_fcurve_data_path.split( '"' )[ 1 ]

            # Skip "Facejoint" shape keys.
            if "Facejoint" in shape_key_name:
                continue

            # Add bone to armature for the shape key. Displace new
            # bone position on X-axis so it doesn't overlap with
            # adjacent bone.
            bone = armature_data.edit_bones.new( shape_key_name )
            bone.head = ( num_shape_keys * 0.25, 0, 0 )
            bone.tail = ( num_shape_keys * 0.25, 0, 1 )

            # Specify data path for new bone rotation f-curve e.g.,
            # new f-curve data path:
            # pose.bones["Frown_L"].rotation_euler
            new_fcurve_data_path = 'pose.bones["%s"].rotation_euler' % shape_key_name

            # Create three new f-curves in new_action (X/Y/Z euler
            # bone rotation).
            new_fcurve_x = new_action.fcurves.new( data_path =
                                                   new_fcurve_data_path, index = 0 )
            new_keyframes_x = new_fcurve_x.keyframe_points
            new_fcurve_y = new_action.fcurves.new( data_path =
                                                   new_fcurve_data_path, index = 1 )
            new_keyframes_y = new_fcurve_y.keyframe_points
            new_fcurve_z = new_action.fcurves.new( data_path =
                                                   new_fcurve_data_path, index = 2 )
            new_keyframes_z = new_fcurve_z.keyframe_points

            # For each shape key keyframe in original f-curve, create
            # a bone rotation keyframe.

            shape_key_keyframes = shape_key_fcurve.keyframe_points
            for shape_key_keyframe in shape_key_keyframes :
                
                # Get frame # and associated shape key value for
                # current keyframe of original f-curve.
                frame = shape_key_keyframe.co[ 0 ]
                value = shape_key_keyframe.co[ 1 ]
                
                # Add keyframe to new f-curve at same frame # whose
                # value is bone's X-axis rotation. Map shape key value
                # between 0 and 1 to bone X-axis rotation 0-100
                # degrees (converted to radians).
                self.insert_and_init_keyframe( new_keyframes_x, frame,
                                               value * 100.0 * 0.01745329251 )
                # No rotation.
                self.insert_and_init_keyframe( new_keyframes_y, frame, 0.0 )
                # No rotation.
                self.insert_and_init_keyframe( new_keyframes_z, frame, 0.0 )

            num_shape_keys = num_shape_keys + 1
                
        # Activate object mode to force blender to update its internal
        # state.
        bpy.ops.object.mode_set( mode = 'OBJECT' )

        # Set rotation mode for the newly created bones to use same
        # mode that Brekel BVH armature bones do: Euler ZXY
        for pose_bone in armature_object.pose.bones:
            pose_bone.rotation_mode = 'ZXY'

        return { 'FINISHED' }

    def insert_and_init_keyframe( self, keyframe_points, frame, value):
        keyframe = keyframe_points.insert( frame, value )
        keyframe.interpolation = 'LINEAR'
        keyframe.handle_left_type = 'AUTO_CLAMPED'
        keyframe.handle_right_type = 'AUTO_CLAMPED'
        keyframe.select_control_point = True
        keyframe.select_left_handle = True
        keyframe.select_right_handle = True

def register():
    bpy.utils.register_class( CreateBrekelAction )

def unregister():
    bpy.utils.unregister_class( CreateBrekelAction )

# For manual testing.
if __name__ == "__main__":
    register()
