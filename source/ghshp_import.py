# -*- coding: utf-8 -*-

# Source code available at https://github.com/hiteca

"""
Component to import geometry and data from ESRI Shapefile.

    Args:
        path: Path to .shp file
        read_geometry: [bool, optional] Toggle to read geometry.
                        Default - True.
        read_records: [bool, optional] Toggle to read data.
                        Default - True.
        field_ids: List of data column to read. 
                    Default - read all columns.
        enc: File encoding. 
                Default - utf-8
    Returns:
        shape_type: pyShp shape type (1 - point, 3 - polyline, 5 - polygon...). See full list at https://github.com/GeospatialPython/pyshp
        geometry: Imported geometry from shp. Each shape is in own branch
        fields: List of fields (format - "name|type|length")
        field_names: List of field names
        records: Data rows. Each row in own branch
"""
ghenv.Component.Name = "Shapefile Import"
ghenv.Component.NickName = 'Shp Import'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.icon
ghenv.Component.Category = "Extra"
ghenv.Component.SubCategory = "Hiteca"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import System
import clr
clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree

import Grasshopper.Kernel as gh

we = gh.GH_RuntimeMessageLevel.Error
ww = gh.GH_RuntimeMessageLevel.Warning

try:
    import shapefile
except:
    message = "Python module 'pyshp' not found. Please download it and install to Rhino IronPython folder using manual at https://github.com/hiteca/ghshp"
    ghenv.Component.AddRuntimeMessage(we, message)
    message = "https://github.com/hiteca/ghshp#install-pyshp"
    ghenv.Component.AddRuntimeMessage(we, message)

import Rhino as rc

def list2branch(source_tree,data,item_index,data_path):
    _p = GH_Path(data_path).AppendElement(item_index)
    for i in range(len(data)):
        _data = data[i]
        if type(_data) == list:
            soruce_tree = v2branch(source_tree,_data,i,_p)
        else:
            source_tree.AddRange([_data],GH_Path(_p))
    return source_tree
    

def py_tree(source_tree, reverse=False, default=None):
    if not reverse:
        result = {}
        for i in range(len(source_tree.Branches)):
            d = source_tree.Branches[i]
            p = GH_Path(source_tree.Paths[i])
            
            result[p] = list(d)
        if len(result.keys())==0:
            result[GH_Path(0)] = [default]
    else:
        result = DataTree[System.Object]()
        for p in source_tree.keys():
            d = source_tree[p]
            _d = []
            for j in range(len(d)):
                data = d[j]
                if type(data) == list:
                    result = list2branch(result,data,j,p)
                else:
                    _d.append(data)
            if len(_d) > 0:
                result.AddRange(_d,p)
                
    return result

def repeat_latest(data,length):
    if len(data) > length:
        return data[:length]
    else:
        return data + ([data[-1]] * (length - len(data)))

def graft_tree(t):
    r = {}
    for k,v in t.items():
        for i in range(len(v)):
            r[GH_Path(k).AppendElement(i)] = [v[i]]
    return r
    
def longest_list(t_a,t_b):
    r_b = {}
    r_a = {}
    prev_a = t_a.items()[0][1]
    prev_b = t_b.items()[0][1]
    
    if len(t_a) >= len(t_b):
        keys = t_a.keys()
    else:
        keys = t_b.keys()

    keys = sorted(keys, key=lambda x: str(GH_Path(x)))

    for k in keys:
        try:
            branch_a = t_a[k]
            prev_a = t_a[k]
        except:
            branch_a = prev_a
        try:
            branch_b = t_b[k]
            prev_b = t_b[k]
        except:
            branch_b = prev_b
        max_len = max(len(branch_b),len(branch_a))
        if len(branch_b) >= len(branch_a):
            branch_a = repeat_latest(branch_a, len(branch_b))
        else:
            branch_b = repeat_latest(branch_b, len(branch_a))
        r_a[k] = branch_a
        r_b[k] = branch_b
        
    return(r_a,r_b)


shape_types = {
    "point" : [
        1, #POINT
        8, #MULTIPOINT
        11, #POINTZ
        18, #MULTIPOINTZ
        21, #POINTM
        28, #MULTIPOINTM
    ],
    "polyline": [
        3, #POLYLINE
        5, #POLYGON
        13, #POLYLINEZ
        15, #POLYGONZ
        23, #POLYLINEM
        25, #POLYGONM
        31, #MULTIPATCH
    ]
}

def find_type(t):
    for k in shape_types.keys():        
        if t in shape_types[k]:
            return k
            

def list2point(pt):
    pt = list(pt)
    if len(pt)==2:
        pt.append(0)
    return rc.Geometry.Point3d(pt[0],pt[1],pt[2])
    
def read_shapefile(file_path, read_data=True, read_geom=True, enc="utf-8"):
    result_geom = []
    result_fields = []
    result_field_names = []
    result_records = []
    if read_data or read_geom:
        sf = shapefile.Reader(file_path)
        sf_type = find_type(sf.shapeType)
        # вывод полей
        if read_data:
            shpfields = sf.fields
            shprecords = sf.records()
            f = 0
            if str(sf.fields[0][0]).startswith("DeletionFlag"):
                shpfields.pop(0) # remove DeletionFlag field

            for i in range(len(shpfields)):
                _shpfields = shpfields[i]
                _field = _shpfields[0]
                _field_type = _shpfields[1]
                _field_len = _shpfields[2]
                _field_len2 = _shpfields[3]
                _field = _field.decode(enc, errors="replace")
                
                result_field_names.append(_field)
                field = "%s;%s;%d;%d" % (_field,_field_type,_field_len,_field_len2)
                result_fields.append(field)
                
        #вывод полилиний и данных
        shapes = sf.shapes()
        

        for i in range(len(shapes)):
            path = GH_Path(i)

            #считывание геометрии
            if read_geom:
                shape = shapes[i]
                #разделение на части
    
                if sf_type == "point":
                    parts = shape.points
                    pt_list = []
                    for p in range(len(parts)):
                        pt = list(parts[p])
                        pt_list.append(list2point(pt))
                    result_geom.append(pt_list)
                else:
                    parts = shape.parts
                    parts2 = parts[:] # copy
                    parts2.append(len(shape.points))
                    part = []
                    for p in range(len(parts)):
                        points = []
                        _p = p + 1
                        for n in range(len(shape.points)):
                            if(n<parts2[_p] and n>=parts2[p]):
                                pt = shape.points[n]
                                points.append(list2point(pt))
                        
                        polylinecurve = rc.Geometry.PolylineCurve(points)
                        part.append(polylinecurve)
                    result_geom.append(part)
            
            if read_records:
                rec = shprecords[i]
                _result_records = []
                for r in range(len(sf.fields)):
                    if str(sf.fields[0][0]).startswith("DeletionFlag") and r==0:
                        continue
                    record = rec[r]
                    if(isinstance(record, str)):
                        record = record.decode(enc, errors="replace")
                    _result_records.append(record)
                result_records.append(_result_records)
                    
    return [sf.shapeType], result_geom, result_fields, result_field_names, result_records


path =py_tree(path)
if len(path.keys())==0:
    message = "Specify .shp file path"
    ghenv.Component.AddRuntimeMessage(ww, message)
else:
    read_geometry =py_tree(read_geometry, default=True)
    read_records =py_tree(read_records, default=True)
    enc =py_tree(enc, default="utf-8")
    
    _path, read_geometry = longest_list(path,read_geometry)
    _path, read_records = longest_list(path,read_records)
    _path, enc = longest_list(path,enc)
    
    path = graft_tree(path)
    read_geometry = graft_tree(read_geometry)
    read_records = graft_tree(read_records)
    enc = graft_tree(enc)
    
    out_shapeType = {}
    out_geometry = {}
    out_fields = {}
    out_field_names = {}
    out_records = {}
    
    for p,file_path in path.items():
    #    print(GH_Path(p), file_path[0],read_geometry[p][0],read_records[p][0],enc[p][0])
        _sf_type, _geom, _fields, _field_names, _records = read_shapefile(file_path[0],
                                                             read_geometry[p][0],
                                                             read_records[p][0],
                                                             enc[p][0])
        out_shapeType[p] = _sf_type
        out_geometry[p] = _geom
        out_fields[p] = _fields
        out_field_names[p] = _field_names
        out_records[p] = _records
    
    shape_type = py_tree(out_shapeType, reverse = True)
    geometry = py_tree(out_geometry, True)
    fields = py_tree(out_fields, True)
    field_names = py_tree(out_field_names, True)
    records = py_tree(out_records, True)
    
