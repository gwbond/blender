
# SUMMARY: Uses an imported BVH from Brekel Kinect Face Pro 2 to
# create drivers to link a armature bones to mesh shape keys. Each
# driver maps an armature bone rotation to a shape key value between
# 0.0 and 1.0.

# COMPATABILITY: Tested with Blender v2.72 and v2.77a

# DOWNLOAD: Go to:
# https://github.com/gwbond/blender/blob/master/Brekel-Kinect-Face-Pro-2-Drivers-Add-On/animation_create_brekel_drivers.py
# and right-click on the 'Raw' button and select 'Save link as...' to
# download the file to your PC/Mac/Linux machine. Save the file as
# "animation_create_brekel_drivers.py"

# INSTALLATION: Install this add-on the usual way via User Preferences
# Addons "Install from File". Select the file you downloaded in the
# previous step. Once installed, this add-on is listed as "Create
# Brekel Kinect Face Pro 2 Drivers" in the "Animation" category.

# USAGE: Before using this add-on, import a Brekel Kinect Face Pro 2
# BVH motion capture file. This will create an armature object. To use
# this add-on, in object mode, select a mesh object with shape keys
# you want to create Brekel drivers for (or shift-select multiple mesh
# objects with shape keys you want to create drivers for). Then,
# shift-select the armature object i.e., the last object to select
# should be the armature. Finally, to create the drivers invoke this
# add-on via the operator search dialog (press spacebar and search for
# "Create Brekel Drivers"). Drivers will only be created for shape
# keys whose name matches an armature bone name. Drivers will not be
# created for shape keys that already have drivers.

# BUGS/ENHANCEMENTS: Feel free report bugs, suggest enhancements or,
# even better, contribute changes to the code. It's hosted on github
# at:
# https://github.com/gwbond/blender/blob/master/Brekel-Kinect-Face-Pro-2-Drivers-Add-On/animation_create_brekel_drivers.py

# LICENSE: GPL v2 or later

bl_info = {
    "name": "Create Brekel Kinect Face Pro 2 Drivers",
    "version": (1, 0),
    "location": 'Press spacebar and search for: "Create Brekel Drivers"',
    "category": "Animation",
}

import bpy

class CreateBrekelDrivers( bpy.types.Operator ):
    # Tooltip.
    """"Create Brekel Kinect Face Pro 2 Drivers"""
    # Unique internal identifier
    bl_idname = "object.create_brekel_drivers"
    # Interface display name.
    bl_label = "Create Brekel Drivers"
    # Enable "undo".
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):

        # Error checking.
        
        if len( context.selected_objects ) < 2 :
            self.report( { 'ERROR' },
                         "Must select at least one mesh object and shift-select Brekel armature." )
            return { 'CANCELLED' }
        if context.active_object.type != 'ARMATURE' :
            self.report( { 'ERROR' },
                         "Must shift-select Brekel armature object last." )
            return { 'CANCELLED' }

        meshes = [ mesh for mesh in context.selected_objects \
                   if mesh != context.active_object ]
        for mesh in meshes :
            if ( 'shape_keys' not in dir( mesh.data ) ) or \
               ( mesh.data.shape_keys == None ) :
                self.report( { 'ERROR' },
                             "Selected mesh object does not contain shape keys.: %s" % mesh.name )
                return { 'CANCELLED' }

        # Set rotation mode for armature bones to use same mode that
        # Brekel BVH armature bone animation does: Euler ZXY
        brekel_armature = context.active_object
        for pose_bone in brekel_armature.pose.bones:
            pose_bone.rotation_mode = 'ZXY'
        
        # Adding drivers.

        driver_counts = []

        for mesh in meshes :
            
            driver_count = 0
            
            # Initialize list of mesh's existing driver data
            # paths. Driver's data path indicates its associated shape
            # key e.g., mesh driver data path
            # 'key_blocks["Frown_R"].value' is identified with mesh
            # shape key "Frown_R".
            mesh_driver_data_paths = []
            if mesh.data.shape_keys.animation_data != None and \
               mesh.data.shape_keys.animation_data.drivers != None:
                mesh_driver_data_paths = [ driver.data_path for driver in
                                           mesh.data.shape_keys.\
                                           animation_data.drivers ]
            for bone in brekel_armature.data.bones :
                # Don't create driver if mesh doesn't have shape key
                # for current bone or if shape key for bone already
                # has a driver.
                if not ( bone.name in mesh.data.shape_keys.key_blocks ) or \
                   ( 'key_blocks["%s"].value' % bone.name in \
                     mesh_driver_data_paths ) :
                    continue

                # Add shape key driver.
                driver_count = driver_count + 1
                new_driver = mesh.data.shape_keys.key_blocks[ bone.name ].\
                             driver_add( 'value' )
                new_driver.extrapolation = 'LINEAR'

                # Brekel armature encodes shape key values as bone
                # X-axis rotations between 0 and 100 degrees. Blender
                # drivers, however, interpret rotation value in
                # radians so the driver uses an interpolation curve to
                # map input value in interval [ 0, 1.7433 ] radians to
                # shape key value in interval [ 0, 1 ].

                # Add three no-op Bezier interpolation keyframes at
                # min (0 rad = 0 degrees), mid (0.8727 rad = 50
                # degrees), and max (1.7433 rad = 100 degrees) shape
                # key values in case interpolation control is
                # desired. NOTE: To view and manipulate keyframes,
                # select a driver in the "Graph Editor" "Drivers"
                # window, and either "mute" or delete any driver
                # modifiers that appear at the bottom of the driver
                # properties window.
                new_driver.keyframe_points.add( 3 )
                # Keyframe at min value 0.0 radians.
                new_driver.keyframe_points[0].co = ( 0.0, 0.0 )
                new_driver.keyframe_points[0].handle_right_type = 'VECTOR'
                new_driver.keyframe_points[0].handle_left_type = 'VECTOR'
                new_driver.keyframe_points[0].handle_left = ( -0.349, -0.2 )
                new_driver.keyframe_points[0].handle_right = ( 0.349, 0.2 )
                # Keyframe at mid value 0.872665 radians.
                new_driver.keyframe_points[1].co = ( 0.872665, 0.5 )
                new_driver.keyframe_points[1].handle_right_type = 'VECTOR'
                new_driver.keyframe_points[1].handle_left_type = 'VECTOR'
                new_driver.keyframe_points[1].handle_left = ( 0.524, 0.3 )
                new_driver.keyframe_points[1].handle_right = ( 1.222, 0.7 )
                # Keyframe at max value 1.74533 radians.
                new_driver.keyframe_points[2].co = ( 1.74533, 1.0 )
                new_driver.keyframe_points[2].handle_right_type = 'VECTOR'
                new_driver.keyframe_points[2].handle_left_type = 'VECTOR'
                new_driver.keyframe_points[2].handle_left = ( 1.396, 0.8 )
                new_driver.keyframe_points[2].handle_right = ( 2.094, 1.2 )

                # Remove any default modifiers that may have been
                # added to the driver because they will override the
                # interpolation keyframes added above.
                for modifier in new_driver.modifiers:
                    new_driver.modifiers.remove(modifier)

                # Link driver to bone rotation.
                new_driver.driver.type = 'AVERAGE'
                new_variable = new_driver.driver.variables.new()
                new_variable.type = 'TRANSFORMS'
                new_variable.targets[0].id = brekel_armature
                new_variable.targets[0].bone_target = bone.name
                new_variable.targets[0].transform_space = 'LOCAL_SPACE'
                new_variable.targets[0].transform_type = 'ROT_X'

            driver_counts.append( ( mesh, driver_count ) )

        # Report statistics.
        count_string = ""
        for ( mesh, count ) in driver_counts:
            count_string += "%d drivers added to %s. " % ( count, mesh.name )
        if count_string == "" :
            self.report( { 'INFO' }, "No drivers added to any objects" )
        else :
            self.report( { 'INFO' }, count_string )

        return { 'FINISHED' }

def register():
    bpy.utils.register_class( CreateBrekelDrivers )

def unregister():
    bpy.utils.unregister_class( CreateBrekelDrivers )

# For manual testing.
if __name__ == "__main__":
    register()
