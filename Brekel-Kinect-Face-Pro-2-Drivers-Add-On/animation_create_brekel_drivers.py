
# SUMMARY: Creates drivers to link a Brekel Kinect Face Pro 2 armature
# bones to mesh shape keys. Each driver maps an armature bone rotation
# to a shape key value between 0.0 and 1.0.

# INSTALLATION: Install this add-on the usual way via User Preferences
# Addons "Install from File". This add-on is listed as "Create Brekel
# Kinect Face Pro 2 Drivers" in the "Animation" category.

# USAGE: Before using this add-on, import a Brekel Kinect Fact Pro 2
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

        # Adding drivers.

        brekel_armature = context.active_object
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

                # Add two no-op FCurve keyframes at min (0 rad = 0
                # degrees) and max (1.7433 rad = 100 degrees) shape
                # key values in case keyrame control is desired at
                # some later time.
                new_driver.keyframe_points.add( 2 )
                # Keyframe at min value 0.0 radians / 0.0 degrees.
                new_driver.keyframe_points[0].co = ( 0.0, 0.0 )
                new_driver.keyframe_points[0].handle_right_type = 'VECTOR'
                new_driver.keyframe_points[0].handle_left_type = 'VECTOR'
                new_driver.keyframe_points[0].handle_left = ( -0.333, -0.333 )
                new_driver.keyframe_points[0].handle_right = ( 0.333, 0.333 )
                # Keyframe at max value 1.74533 radians / 100 degrees.
                new_driver.keyframe_points[1].co = ( 1.74533, 1.74533 )
                new_driver.keyframe_points[1].handle_right_type = 'VECTOR'
                new_driver.keyframe_points[1].handle_left_type = 'VECTOR'
                new_driver.keyframe_points[1].handle_left = ( 1.412, 1.412 )
                new_driver.keyframe_points[1].handle_right = ( 2.079, 2.079 )

                # Link driver to bone rotation.
                new_driver.driver.type = 'AVERAGE'
                new_variable = new_driver.driver.variables.new()
                new_variable.type = 'TRANSFORMS'
                new_variable.targets[0].id = brekel_armature
                new_variable.targets[0].bone_target = bone.name
                new_variable.targets[0].transform_space = 'LOCAL_SPACE'
                new_variable.targets[0].transform_type = 'ROT_X'

                # Brekel armature encodes shape key values as bone
                # X-axis rotations between 0 and 100 degrees. Blender
                # drivers, however, interpret rotation value in
                # radians so the driver requires a modifier to
                # translate radian value back to degrees.

                # Convert from radians to degrees, normalized to
                # interval [0.0, 1.0].

                # ( 180 degrees / Pi radians ) / 100
                new_driver.modifiers[0].coefficients[1] = 0.5729578137397766

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
