bl_info = {
    "name": "Automatic Rename Assets",
    "author": "Oleg",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "category": "Assets",
    "description": "Addon automaticly generates names for selected assets",
}

import bpy
from bpy.types import Operator, Panel, Header

class OBJECT_OT_RenameAsset(Operator):
    "OBJECTS AND COLLECTIONS ONLY! Auto rename selected assets"
    bl_idname = "asset.rename_asset_operator"
    bl_label = "Rename Assets"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "FILE_BROWSER"
            
    def execute(self, context):
        class SelectedAsset():  

            asset_types = {
                'OBJECT' : bpy.data.objects,
                'MESH' : bpy.data.meshes,
                'LIGHT' : bpy.data.lights,
                'COLLECTION' : bpy.data.collections,
                'WORLD' : bpy.data.worlds,
                'TEXT' : bpy.data.texts,
                'MATERIAL' : bpy.data.materials,
                'NODETREE' : bpy.data.node_groups,
            }

            items_in_selection = {}
            for item in context.selected_asset_files:
                items_in_selection[item.name] = item.id_type
            bpy.ops.asset.library_refresh() #Clears active asset (Written in Not proper way)
            

            items_in_data = []
            for asset_type in asset_types.values():
                for item in asset_type:
                    items_in_data.append(item)
                            
            blend_file_path = bpy.path.abspath('//')
            blend_file_name = bpy.path.basename(bpy.context.blend_data.filepath).split('.')[0]
            blend_file_fullpath = blend_file_path + blend_file_name
            
            """FIXME"""
        #            if bpy.data.is_saved == False:
        #                raise 

            def rename(self):
                asset_types = self.asset_types
                # Searches if name already exists then then +1 name's number
                counter = 1
                while counter <= len(self.items_in_data):
                    if counter < 10:
                        asset_number = '0' + str(counter)
                    else:
                        asset_number = str(counter)
                    asset_new_name = f'{self.blend_file_name}_{asset_number}'
                    if any(item.name == asset_new_name for item in self.items_in_data):
                        counter += 1
                    else:
                        break
                #Renaming selected assets
                for selected_item_name, selected_item_type in self.items_in_selection.items():
                    # for item_name in asset_types[item_type]:
                    if counter < 10:
                        asset_number = '0' + str(counter)
                    else:
                        asset_number = str(counter)
                    asset_new_name = f'{self.blend_file_name}_{asset_number}'
                    # Adding named tags from names of catalogs from file path
                    tags_names_from_path = self.blend_file_path.split('{Asset_Library')[1].split('\\')[1:-1]
                    memory_tag = '#DO NOT DELETE THIS TAG#'
                    tags_names_to_delete = ''
                    for tag in asset_types[selected_item_type][selected_item_name].asset_data.tags:
                        if memory_tag in tag.name:
                            tags_names_to_delete = tag.name.split('\\')[1:]
                            asset_types[selected_item_type][selected_item_name].asset_data.tags.remove(tag)

                    for tag in asset_types[selected_item_type][selected_item_name].asset_data.tags:
                        for tag_name_to_delete in tags_names_to_delete:
                            try:
                                if tag.name == tag_name_to_delete:
                                    asset_types[selected_item_type][selected_item_name].asset_data.tags.remove(tag)
                            except ReferenceError:
                                break

                    for tag_name in tags_names_from_path:
                        memory_tag += f'\\{tag_name}'
                        asset_types[selected_item_type][selected_item_name].asset_data.tags.new(tag_name, skip_if_exists=True)
                    asset_types[selected_item_type][selected_item_name].asset_data.tags.new(memory_tag, skip_if_exists=True)
                    asset_types[selected_item_type][selected_item_name].name = asset_new_name #Finally assingning new name to asset
                    counter += 1
        SelectedAsset().rename()
        return {'FINISHED'}

class OBJECT_OT_BatchAddTag(Operator):
    "Adds tag to selected assets"
    bl_idname = "asset.batch_add_tag_operator"
    bl_label = "Batch Add Tag"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "FILE_BROWSER"
            
    def execute(self, context):
            
        def batch_add_tag():
            if context.scene.tag_name != '':
                for item in context.selected_asset_files:
                    item.asset_data.tags.new(context.scene.tag_name, skip_if_exists=True)
            else:
                pass
            context.scene.tag_name = '' #Clears tag name property (text box)
        batch_add_tag()
        return {'FINISHED'}

class OBJECT_OT_BatchRemoveTag(Operator):
    "Removes tag from selected assets"
    bl_idname = "asset.batch_remove_tag_operator"
    bl_label = "Batch Remove Tag"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "FILE_BROWSER"
            
    def execute(self, context):

        def batch_remove_tag():
            if context.scene.tag_name != '':
                for item in context.selected_asset_files:
                    for tag in item.asset_data.tags:
                        if context.scene.tag_name in tag.name:
                            item.asset_data.tags.remove(tag)
            else:
                pass
            context.scene.tag_name = '' #Clears tag name property (text box)
        batch_remove_tag()
        return {'FINISHED'}

class OBJECT_OT_GenerateCustomPreview(Operator):
    "Generates custom preview for selected asset"
    bl_idname = "asset.generate_cust_preview_operator"
    bl_label = "Generate custom preview"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "FILE_BROWSER"
            
    def execute(self, context):
            
        def generate_custom_preview():
            
            scene = bpy.context.scene
            node_tree = scene.node_tree
            active_obj = bpy.context.view_layer.objects.active
            active_material = active_obj.material_slots[0]

            scene.use_nodes = True

            #Clears all nodes for now
            for node in bpy.context.scene.node_tree.nodes:
                bpy.context.scene.node_tree.nodes.remove(node)

            def create_rlayer_node():
                render_layer_node = node_tree.nodes.new(type = 'CompositorNodeRLayers')
                render_layer_node.location = (0,0)
                return render_layer_node

            def create_alpha_over_node():
                alpha_over_node = node_tree.nodes.new(type = 'CompositorNodeAlphaOver')
                alpha_over_node.location = (400,0)
                return alpha_over_node
                
            def create_output_file_node():
                output_file_node = node_tree.nodes.new(type = 'CompositorNodeOutputFile')
                # output_file_node.file_slots.remove(output_node.inputs[0])
                output_file_node.base_path = '//Preview\\'
                output_file_node.file_slots[0].path = f"{active_material.name}_#"
                output_file_node.format.file_format = 'PNG'
                output_file_node.format.color_mode = 'RGBA'
                output_file_node.format.color_depth = '8'
                output_file_node.format.compression = 50
                output_file_node.location = (800,0)
                return output_file_node

            rlayer_node = create_rlayer_node()
            output_file_node = create_output_file_node()
            node_tree.links.new(rlayer_node.outputs["Image"], output_file_node.inputs[0])
            bpy.ops.render.render(use_viewport=True)

            blend_file_path = bpy.path.abspath('//')
            bpy.ops.ed.lib_id_load_custom_preview(
                        filepath=f"{blend_file_path}Preview\{active_material.name}_1.png"
                    )

        generate_custom_preview()
        return {'FINISHED'}

def draw(self, context):
    layout = self.layout
    row_1 = layout.row(align = True)
    row_2 = layout.row(align = True)
    row_1.ui_units_x = 6
    row_1.prop(context.scene, 'tag_name', text="", icon='SORTALPHA')

    row_1.operator(
        'asset.batch_add_tag_operator',
        text="",
        icon='ADD',
    )

    row_1.operator(
        'asset.batch_remove_tag_operator',
        text="",
        icon='REMOVE',
    )

    row_2.operator(
            'asset.rename_asset_operator',
            text="",
            icon='FILE_TEXT',
        )
    
    row_2.operator(
            'asset.generate_cust_preview_operator',
            text="",
            icon='RESTRICT_RENDER_OFF',
        )

classes = [
    OBJECT_OT_RenameAsset,
    OBJECT_OT_BatchAddTag,
    OBJECT_OT_BatchRemoveTag,
    OBJECT_OT_GenerateCustomPreview
]

def register():
    bpy.types.Scene.tag_name = bpy.props.StringProperty(name="Tag name",
                                        description="Name of the new tag",
                                        default="",
                                        maxlen=1024
                                        )
    for cl in classes:
        bpy.utils.register_class(cl)
    bpy.types.FILEBROWSER_HT_header.append(draw)

def unregister():
    del  bpy.types.Scene.tag_name
    for cl in classes:
        bpy.utils.unregister_class(cl)
    bpy.types.FILEBROWSER_HT_header.remove(draw)

if __name__ == '__main__':
    register()