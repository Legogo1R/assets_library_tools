import bpy

class SelectedAsset:  

    asset_types = (
        bpy.data.objects,
        bpy.data.collections,
        bpy.data.worlds,
        bpy.data.texts,
        bpy.data.materials
    )
    
    
    items_in_selection = []
    for item in context.selected_asset_files:
        items_in_selection.append(item.name)
    bpy.ops.asset.library_refresh() #Clears active asset (Written in Not proper way)
    
    items_in_data = []
    for asset_type in asset_types:
        for item in asset_type:
            items_in_data.append(item)
                   
    blend_file_path = bpy.path.abspath('//')
    blend_file_name = bpy.path.basename(bpy.context.blend_data.filepath).split('.')[0]
    blend_file_fullpath = blend_file_path + blend_file_name
    
    """FIXME"""
#            if bpy.data.is_saved == False:
#                raise 

    def rename(self):
        # Searches if name already exists then then +1 name's number
        counter = 1
        while counter < 10:
            if counter < 10:
                asset_number = '0' + str(counter)
            else:
                asset_number = str(counter)
            asset_new_name = f'{self.blend_file_name}_{asset_number}'
            print(asset_new_name)
            
            if any(item.name == asset_new_name for item in self.items_in_data):
                counter += 1
            else:
                break
        #Renaming selected assets
        for item in self.items_in_selection:
            for asset_type in self.asset_types:
                if item in asset_type:
                    if counter < 10:
                        asset_number = '0' + str(counter)
                    else:
                        asset_number = str(counter)
                    asset_new_name = f'{self.blend_file_name}_{asset_number}'
                    #Adding named tags from names of catalogs from file path
                    tags_names = self.blend_file_path.split('{Asset_Library')[1].split('\\')[1:-1]
                    print(tags_names)
                    for tag_name in tags_names:
                        print(tag_name)
                        if not any(
                            tag.name == tag_name
                            for tag in asset_type[item].asset_data.tags
                        ):
                            asset_type[item].asset_data.tags.new(tag_name)
                        
                    asset_type[item].name = asset_new_name
            counter += 1