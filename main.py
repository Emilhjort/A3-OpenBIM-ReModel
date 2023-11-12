from pathlib import Path
import ifcopenshell

modelname = "LLYN - ARK_modified"

try:
    dir_path = Path(__file__).parent
    model_url = Path.joinpath(dir_path, 'model', modelname).with_suffix('.ifc')
    model = ifcopenshell.open(model_url)
except OSError:
    try:
        import bpy
        model_url = Path.joinpath(Path(bpy.context.space_data.text.filepath).parent, 'model', modelname).with_suffix('.ifc')
        model = ifcopenshell.open(model_url)
    except OSError:
        print(f"ERROR: please check your model folder : {model_url} does not exist")
        
        
        
def handle_model(model):
    # find all the IFC walls
    walls = model.by_type("IfcWall")

    # find the material that corresponds to concrete
    concrete_materials = model.by_type("IfcMaterial")
    concrete_material = None
    for material in concrete_materials:
        if "concrete" in material.Name.lower():
            concrete_material = material
            break

    if not concrete_material:
        print("No concrete material found")
        return

    # create a new property set and add it to the concrete material
    new_material_pset = ifcopenshell.api.run(
        "pset.add_pset", model, product=concrete_material, name="Pset_MaterialCommon"
    )

    # edit the property set by providing a dictionary with the properties to define
    ifcopenshell.api.run(
        "pset.edit_pset",
        model,
        pset=new_material_pset,
        properties={"MassDensity": 2400, "MassDensityUnit": "kg/m3"},
    )

    # apply the new property set to all IFC walls with the concrete material
    for wall in walls:
        wall_material = ifcopenshell.util.element.get_material(wall)
        if wall_material == concrete_material:
            wall_material_psets = ifcopenshell.util.element.get_psets(wall_material)
            wall_material_psets.append(new_material_pset)
            ifcopenshell.util.element.set_psets(wall_material, wall_material_psets)


model.write('C:/Users/oline/OneDrive/Dokumenter/DTU/Semester 1/41934 Advanced Building Information Modeling/Assignments/A3 - OpenBIM Change/A3 script/model/NEW_LLYN - ARK_modified.ifc')


