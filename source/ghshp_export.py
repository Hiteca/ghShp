Category = "Extra"
ghenv.Component.SubCategory = "Hiteca"
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass


import sys

import System
import clr
import os
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

import rhinoscriptsyntax as rs

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
    if len(pt)==2:
        pt.append(0)
    return rc.Geometry.Point3d(pt[0],pt[1],pt[2])


def write_shapefile(file_path, st, geom, fields, data, enc):
    w = shapefile.Writer(shapeType=st)
    sf_type = find_type(st)

    records_dict = {}
    # create fields
    for f in fields:
        f_name, f_type, f_len = f.split(";")
        w.field(f_name, f_type, int(f_len))
    
    # generate geometry
    for geom_branch in geom:
        parts = []
        if sf_type == "point":
            for point in geom_branch:
                parts.append(list(point))
            parts = [parts]
        else:
            for polyline in geom_branch:
                parts_p = []
                points = rs.CurvePoints(polyline)
                for p in points:
                    parts_p.append(list(p))
                parts.append(parts_p)
        w.poly(parts=parts,shapeType=st)
    
    for record in data:
        # TEMP
        # encode strings to ASCII with ignore
        # to prevent the same exception in pyshp
        r = [r.encode("ascii", 'ignore') if type(r) in [str, unicode] else r for r in record]
        w.record(*r)
    
    try:
        w.save(file_path)
        print("Write successful - %s" % file_path)
    except Exception as e:
        print(isinstance(e,UnicodeEncodeError))
        print("Error with writing %s" % file_path,e)
    

path = py_tree(path)
geometry = py_tree(geometry)
shape_type = py_tree(shape_type)
fields = py_tree(fields)
records = py_tree(records)
enc = py_tree(enc, default="utf-8")

def shift_path(d):
    new_dict = {}
    for k,v in d.items():
        _k = k.CullElement()
        if _k not in new_dict.keys():
            new_dict[_k] = []
        new_dict[_k].append(v)
    return new_dict


def write_many(path, shape_type, geometry, fields, records, enc):
    for k,v in path.items():
        
        _geometry = geometry[k]
        write_shapefile(path[k][0], shape_type[k][0], geometry[k], fields[k], 
                        records[k], enc[k][0])


if write == True:
    _path, geometry = longest_list(path,geometry)
    _path, shape_type = longest_list(path,shape_type)
    _path, fields = longest_list(path,fields)
    _path, records = longest_list(path,records)
    _path, enc = longest_list(path,enc)

    geometry = shift_path(geometry)
    records = shift_path(records)

    write_many(path, shape_type, geometry, fields, records, enc)