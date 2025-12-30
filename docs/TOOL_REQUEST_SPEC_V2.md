BATCH P0 - TRANSFORMATIONS AVANCÉES (Tests réels Blender 5.0.0)
Tool 1/7 - blender-object-scale

A

blender-dev-exec-python


✅ SPEC TOOL 1 - blender-object-scale
yaml
* Identité
  * name: blender-object-scale
  * Description: Scale object avec facteurs X/Y/Z indépendants
  * Catégorie: object
  * Tags: [transform, scale, resize]

* Contexte
  * Mode requis: OBJECT
  * Sélection requise: Non (utilise name)
  * API: bpy.data.objects[name].scale (DATA-FIRST)

* Entrées
{
  "type": "object",
  "properties": {
    "name": {"type": "string", "description": "Nom objet"},
    "sx": {"type": "number", "minimum": 0.001, "maximum": 1000, "description": "Scale X"},
    "sy": {"type": "number", "minimum": 0.001, "maximum": 1000, "description": "Scale Y"},
    "sz": {"type": "number", "minimum": 0.001, "maximum": 1000, "description": "Scale Z"},
    "uniform": {"type": "boolean", "default": false, "description": "Si true, sx appliqué à XYZ"}
  },
  "required": ["name", "sx"],
  "additionalProperties": false
}

* Sortie
{
  "name": "Cube",
  "scale": [2.0, 3.0, 1.5],
  "dimensions": [2.0, 3.0, 1.5]
}

* Garde-fous
  * Objet existe et type MESH
  * Clamp scale: 0.001 ≤ value ≤ 1000
  * Si uniform=true: sy/sz optionnels, utilise sx
  * Error: "Object not found" / "Invalid scale value"

* Tests
  # Prep: Cube défaut
  blender-object-scale(name="Cube", sx=2, sy=3, sz=1.5)
  # → scale=[2,3,1.5], dimensions=[2,3,1.5]
  
  blender-object-scale(name="Cube", sx=0.5, uniform=true)
  # → scale=[0.5,0.5,0.5]
Tool 2/7 - blender-object-apply-transform

A

blender-dev-exec-python


✅ SPEC TOOL 2 - blender-object-apply-transform
yaml
* Identité
  * name: blender-object-apply-transform
  * Description: Apply transformations (location/rotation/scale) to object data
  * Catégorie: object
  * Tags: [transform, apply, data]

* Contexte
  * Mode requis: OBJECT
  * Sélection requise: Non (utilise name, devient active)
  * API: bpy.ops.object.transform_apply (avec context override)

* Entrées
{
  "type": "object",
  "properties": {
    "name": {"type": "string", "description": "Nom objet"},
    "location": {"type": "boolean", "default": false, "description": "Apply location"},
    "rotation": {"type": "boolean", "default": false, "description": "Apply rotation"},
    "scale": {"type": "boolean", "default": false, "description": "Apply scale"},
    "properties": {"type": "boolean", "default": false, "description": "Apply properties"}
  },
  "required": ["name"],
  "additionalProperties": false
}

* Sortie
{
  "name": "Cube",
  "applied": {
    "location": true,
    "rotation": false,
    "scale": true
  },
  "final_transform": {
    "location": [0.0, 0.0, 0.0],
    "rotation": [0.5, 0.3, 0.1],
    "scale": [1.0, 1.0, 1.0]
  }
}

* Garde-fous
  * Objet existe et type MESH/CURVE/SURFACE
  * Au moins un paramètre (location/rotation/scale) = true
  * Mode OBJECT obligatoire
  * Error: "Object not found" / "No transform to apply" / "Invalid object type"

* Tests
  # Prep: Cube à (5,3,2), scale(2,1.5,3), rot(0.5,0.3,0.1)
  blender-object-apply-transform(name="Cube", location=true)
  # → location=[0,0,0], mesh vertices déplacés
  
  blender-object-apply-transform(name="Cube", scale=true, rotation=true)
  # → scale=[1,1,1], rotation=[0,0,0], geometry modifiée
Tool 3/7 - blender-object-origin-set

A

blender-dev-exec-python


✅ SPEC TOOL 3 - blender-object-origin-set
yaml
* Identité
  * name: blender-object-origin-set
  * Description: Set object origin to geometry/cursor/center
  * Catégorie: object
  * Tags: [origin, pivot, transform]

* Contexte
  * Mode requis: OBJECT
  * Sélection requise: Non (utilise name, devient active)
  * API: bpy.ops.object.origin_set

* Entrées
{
  "type": "object",
  "properties": {
    "name": {"type": "string", "description": "Nom objet"},
    "type": {
      "type": "string",
      "enum": ["GEOMETRY", "CURSOR", "CENTER_MASS", "CENTER_VOLUME", "GEOMETRY_ORIGIN"],
      "description": "Type: GEOMETRY=géométrie median, CURSOR=3D cursor, CENTER_MASS=surface, CENTER_VOLUME=volume, GEOMETRY_ORIGIN=déplace mesh à origin"
    },
    "center": {
      "type": "string",
      "enum": ["MEDIAN", "BOUNDS"],
      "default": "MEDIAN",
      "description": "Center type pour GEOMETRY (MEDIAN ou BOUNDS)"
    }
  },
  "required": ["name", "type"],
  "additionalProperties": false
}

* Sortie
{
  "name": "Cube",
  "origin_type": "GEOMETRY",
  "new_location": [7.0, 5.0, 4.0],
  "center": "MEDIAN"
}

* Garde-fous
  * Objet existe et type MESH/CURVE/SURFACE
  * Mode OBJECT obligatoire
  * Pour CURSOR: vérifier cursor.location valide
  * Error: "Object not found" / "Invalid origin type" / "Wrong mode"

* Tests
  # Prep: Cube, mesh déplacé +2,+2,+2 en edit
  blender-object-origin-set(name="Cube", type="GEOMETRY", center="MEDIAN")
  # → Origin suit le centre géométrique du mesh
  
  # Cursor à (10,10,10)
  blender-object-origin-set(name="Cube", type="CURSOR")
  # → Origin déplacé à (10,10,10)
  
  blender-object-origin-set(name="Cube", type="GEOMETRY_ORIGIN")
  # → Mesh déplacé pour que origin soit à (0,0,0)
Tool 4/7 - blender-object-parent

A

blender-dev-exec-python


✅ SPEC TOOL 4 - blender-object-parent
yaml
* Identité
  * name: blender-object-parent
  * Description: Set/clear parent-child relationship between objects
  * Catégorie: object
  * Tags: [parent, hierarchy, relationship]

* Contexte
  * Mode requis: OBJECT
  * Sélection requise: Non (utilise child_name + parent_name)
  * API: bpy.ops.object.parent_set / parent_clear

* Entrées
{
  "type": "object",
  "properties": {
    "child_name": {"type": "string", "description": "Nom objet enfant"},
    "parent_name": {
      "anyOf": [{"type": "string"}, {"type": "null"}],
      "description": "Nom objet parent (null pour clear)"
    },
    "keep_transform": {
      "type": "boolean",
      "default": true,
      "description": "Conserver world transform"
    },
    "type": {
      "type": "string",
      "enum": ["OBJECT", "BONE", "VERTEX", "VERTEX_TRI"],
      "default": "OBJECT",
      "description": "Type de parent"
    }
  },
  "required": ["child_name"],
  "additionalProperties": false
}

* Sortie
{
  "child": "Child",
  "parent": "Parent",
  "keep_transform": true,
  "child_location": [3.0, 0.0, 0.0],
  "relationship": "set"
}
// OU pour clear:
{
  "child": "Child",
  "parent": null,
  "relationship": "cleared",
  "child_location": [3.0, 0.0, 0.0]
}

* Garde-fous
  * Child et parent existent (si parent_name fourni)
  * Child != Parent (pas de cycle)
  * Mode OBJECT obligatoire
  * Si parent_name=null: clear parent
  * Error: "Object not found" / "Cannot parent to self" / "Parent loop detected"

* Tests
  # Prep: Parent à (0,0,0), Child à (3,0,0)
  blender-object-parent(child_name="Child", parent_name="Parent", keep_transform=true)
  # → Child.parent="Parent", location inchangée (3,0,0)
  
  blender-object-parent(child_name="Child", parent_name="Parent", keep_transform=false)
  # → Child location relative: (3,0,0) local au parent
  
  blender-object-parent(child_name="Child", parent_name=null, keep_transform=true)
  # → Clear parent, location monde préservée
Tool 5/7 - blender-object-clear-transform

A

blender-dev-exec-python


✅ SPEC TOOL 5 - blender-object-clear-transform
yaml
* Identité
  * name: blender-object-clear-transform
  * Description: Reset location/rotation/scale to defaults (0,0,0 / 1,1,1)
  * Catégorie: object
  * Tags: [transform, reset, clear]

* Contexte
  * Mode requis: OBJECT
  * Sélection requise: Non (utilise name, devient active)
  * API: bpy.data.objects[name] direct (DATA-FIRST)

* Entrées
{
  "type": "object",
  "properties": {
    "name": {"type": "string", "description": "Nom objet"},
    "location": {"type": "boolean", "default": false, "description": "Clear location → (0,0,0)"},
    "rotation": {"type": "boolean", "default": false, "description": "Clear rotation → (0,0,0)"},
    "scale": {"type": "boolean", "default": false, "description": "Clear scale → (1,1,1)"},
    "delta": {"type": "boolean", "default": false, "description": "Clear delta transforms aussi"}
  },
  "required": ["name"],
  "additionalProperties": false
}

* Sortie
{
  "name": "Cube",
  "cleared": {
    "location": true,
    "rotation": false,
    "scale": true,
    "delta": false
  },
  "final_transform": {
    "location": [0.0, 0.0, 0.0],
    "rotation": [0.5, 0.3, 0.1],
    "scale": [1.0, 1.0, 1.0]
  }
}

* Garde-fous
  * Objet existe
  * Au moins un paramètre (location/rotation/scale) = true
  * Mode OBJECT obligatoire
  * Error: "Object not found" / "No transform to clear"

* Tests
  # Prep: Cube à (5,3,2), scale(2,1.5,3), rot(0.5,0.3,0.1)
  blender-object-clear-transform(name="Cube", location=true)
  # → location=[0,0,0]
  
  blender-object-clear-transform(name="Cube", rotation=true, scale=true)
  # → rotation=[0,0,0], scale=[1,1,1]
  
  blender-object-clear-transform(name="Cube", location=true, rotation=true, scale=true, delta=true)
  # → Tous transforms réinitialisés
Tool 6/7 - blender-mesh-rotate-selection

1 étape
A


blender-dev-exec-python


A


blender-dev-exec-python


✅ SPEC TOOL 6 - blender-mesh-rotate-selection
yaml
* Identité
  * name: blender-mesh-rotate-selection
  * Description: Rotate selected vertices around axis and pivot
  * Catégorie: mesh
  * Tags: [transform, rotate, edit, bmesh]

* Contexte
  * Mode requis: EDIT
  * Sélection requise: Oui (vertices)
  * API: bmesh + Matrix.Rotation (SAFE-FIRST)

* Entrées
{
  "type": "object",
  "properties": {
    "name": {"type": "string", "description": "Nom objet"},
    "angle": {
      "type": "number",
      "minimum": -360,
      "maximum": 360,
      "description": "Angle en degrés"
    },
    "axis": {
      "type": "string",
      "enum": ["X", "Y", "Z"],
      "description": "Axe de rotation"
    },
    "pivot": {
      "anyOf": [
        {"items": {"type": "number"}, "minItems": 3, "maxItems": 3, "type": "array"},
        {"type": "null"}
      ],
      "default": null,
      "description": "Pivot custom [x,y,z] en local, null=centre sélection"
    },
    "euler_xyz": {
      "anyOf": [
        {"items": {"type": "number"}, "minItems": 3, "maxItems": 3, "type": "array"},
        {"type": "null"}
      ],
      "default": null,
      "description": "Rotation Euler [x°,y°,z°] multi-axes (override angle+axis)"
    }
  },
  "required": ["name"],
  "additionalProperties": false
}

* Sortie
{
  "name": "Cube",
  "rotated_verts": 4,
  "angle": 45,
  "axis": "Z",
  "pivot": [0.0, 0.0, 1.0],
  "euler_xyz": null
}

* Garde-fous
  * Objet existe, type MESH
  * Mode EDIT obligatoire
  * Sélection non vide (verts)
  * Clamp angle: -360 ≤ angle ≤ 360
  * Si euler_xyz fourni: ignore angle+axis
  * Si pivot=null: calcule centre bbox sélection
  * Error: "No selection" / "Wrong mode" / "Invalid angle"

* Tests
  # Prep: Cube, top 4 verts sélectionnés
  blender-mesh-rotate-selection(name="Cube", angle=45, axis="Z")
  # → Top face tournée 45° autour centre
  
  blender-mesh-rotate-selection(name="Cube", angle=90, axis="Y", pivot=[0,0,0])
  # → Rotation autour origin local
  
  blender-mesh-rotate-selection(name="Cube", euler_xyz=[30,45,60])
  # → Rotation combinée XYZ
Tool 7/7 - blender-object-duplicate

A

blender-dev-exec-python


✅ SPEC TOOL 7 - blender-object-duplicate
yaml
* Identité
  * name: blender-object-duplicate
  * Description: Duplicate object with optional linked data and transform offset
  * Catégorie: object
  * Tags: [duplicate, copy, array]

* Contexte
  * Mode requis: OBJECT
  * Sélection requise: Non (utilise name)
  * API: bpy.data.objects[].copy() + data.copy() (DATA-FIRST)

* Entrées
{
  "type": "object",
  "properties": {
    "name": {"type": "string", "description": "Nom objet source"},
    "new_name": {
      "anyOf": [{"type": "string"}, {"type": "null"}],
      "default": null,
      "description": "Nom du duplicate (auto si null)"
    },
    "linked": {
      "type": "boolean",
      "default": false,
      "description": "Partager mesh data (true) ou copier (false)"
    },
    "offset": {
      "items": {"type": "number"},
      "minItems": 3,
      "maxItems": 3,
      "default": [0, 0, 0],
      "description": "Offset position [x,y,z]"
    },
    "collection": {
      "anyOf": [{"type": "string"}, {"type": "null"}],
      "default": null,
      "description": "Collection target (null=même que source)"
    }
  },
  "required": ["name"],
  "additionalProperties": false
}

* Sortie
{
  "source": "Original",
  "duplicate": "Original.001",
  "linked": false,
  "location": [3.0, 0.0, 0.0],
  "collection": "Collection",
  "data_shared": false
}

* Garde-fous
  * Objet source existe
  * Mode OBJECT obligatoire
  * Si linked=false: copie mesh data (indépendant)
  * Si linked=true: partage mesh data
  * new_name unique (ajoute .001 si existe)
  * Collection existe si fournie
  * Error: "Object not found" / "Invalid collection" / "Name conflict"

* Tests
  # Prep: Cube "Original" scale(2,1,1)
  blender-object-duplicate(name="Original", offset=[3,0,0], linked=false)
  # → "Original.001" à (3,0,0), data indépendant
  
  blender-object-duplicate(name="Original", new_name="Copy", offset=[6,0,0], linked=true)
  # → "Copy" partage mesh avec Original
  
  # Array:
  for i in range(5):
    blender-object-duplicate(name="Base", offset=[i*3,0,0])
  # → 5 copies espacées de 3 unités
📊 RÉSUMÉ BATCH P0 - TRANSFORMATIONS AVANCÉES
✅ 7/7 tools testés et spécifiés:

blender-object-scale - Scale X/Y/Z indépendants
blender-object-apply-transform - Apply loc/rot/scale to data
blender-object-origin-set - Set origin (geometry/cursor/center)
blender-object-parent - Parent-child relationships
blender-object-clear-transform - Reset transforms
blender-mesh-rotate-selection - Rotate verts avec pivot
blender-object-duplicate - Duplicate avec linked/offset
Approche DATA-FIRST validée sur Blender 5.0.0 avec bmesh + bpy.data prioritaires.

Prêt pour implémentation MCP. Continuer avec BATCH P0 - MODIFIERS ?

oui continue

16:34
BATCH P0 - MODIFIERS ESSENTIELS (Tests réels Blender 5.0.0)
Tool 8 - blender-modifier-add
A


blender-dev-exec-python


A


blender-dev-exec-python


✅ SPEC TOOL 8 - blender-modifier-add
yaml
* Identité
  * name: blender-modifier-add
  * Description: Add modifier to object (Array/Mirror/Solidify/Boolean/Bevel/Subsurf/etc)
  * Catégorie: modifier
  * Tags: [modifier, add, generate, deform]

* Contexte
  * Mode requis: OBJECT
  * Sélection requise: Non (utilise name)
  * API: bpy.data.objects[name].modifiers.new() (DATA-FIRST)

* Entrées
{
  "type": "object",
  "properties": {
    "name": {"type": "string", "description": "Nom objet"},
    "modifier_name": {"type": "string", "description": "Nom du modifier"},
    "modifier_type": {
      "type": "string",
      "enum": [
        "ARRAY", "BEVEL", "BOOLEAN", "BUILD", "DECIMATE", "EDGE_SPLIT",
        "MASK", "MIRROR", "MULTIRES", "REMESH", "SCREW", "SKIN",
        "SOLIDIFY", "SUBSURF", "TRIANGULATE", "WELD",
        "ARMATURE", "CAST", "CURVE", "DISPLACE", "HOOK", "LAPLACIANDEFORM",
        "LATTICE", "MESH_DEFORM", "SHRINKWRAP", "SIMPLE_DEFORM",
        "SMOOTH", "CORRECTIVE_SMOOTH", "LAPLACIANSMOOTH",
        "SURFACE_DEFORM", "WARP", "WAVE",
        "CLOTH", "COLLISION", "DYNAMIC_PAINT", "EXPLODE", "FLUID",
        "OCEAN", "PARTICLE_INSTANCE", "PARTICLE_SYSTEM", "SOFT_BODY",
        "NODES"
      ],
      "description": "Type de modifier"
    }
  },
  "required": ["name", "modifier_name", "modifier_type"],
  "additionalProperties": false
}

* Sortie
{
  "name": "Cube",
  "modifier": "MyArray",
  "type": "ARRAY",
  "index": 0
}

* Garde-fous
  * Objet existe, type MESH/CURVE/LATTICE/etc
  * Mode OBJECT obligatoire
  * modifier_name unique pour cet objet
  * modifier_type valide (enum)
  * Error: "Object not found" / "Invalid modifier type" / "Modifier name exists"

* Tests
  # Prep: Cube
  blender-modifier-add(name="Cube", modifier_name="MyArray", modifier_type="ARRAY")
  # → Modifier Array ajouté, index 0
  
  blender-modifier-add(name="Cube", modifier_name="MyMirror", modifier_type="MIRROR")
  # → Modifier Mirror ajouté, index 1
Tool 9 - blender-modifier-configure

A

blender-dev-exec-python


✅ SPEC TOOL 9 - blender-modifier-configure
yaml
* Identité
  * name: blender-modifier-configure
  * Description: Configure modifier parameters with type-specific settings
  * Catégorie: modifier
  * Tags: [modifier, configure, parameters]

* Contexte
  * Mode requis: OBJECT
  * Sélection requise: Non (utilise name + modifier_name)
  * API: bpy.data.objects[name].modifiers[modifier_name] (DATA-FIRST)

* Entrées
{
  "type": "object",
  "properties": {
    "name": {"type": "string", "description": "Nom objet"},
    "modifier_name": {"type": "string", "description": "Nom du modifier"},
    "params": {
      "type": "object",
      "description": "Dict params spécifiques au type de modifier",
      "additionalProperties": true
    }
  },
  "required": ["name", "modifier_name", "params"],
  "additionalProperties": false
}

* Paramètres par type de modifier:

ARRAY:
  - count (int, 1-10000): nombre copies
  - relative_offset_displace (array[3], float): offset relatif
  - constant_offset_displace (array[3], float): offset constant
  - use_constant_offset (bool): utiliser constant offset
  - use_merge_vertices (bool): merge verts
  - merge_threshold (float, 0-1): distance merge

MIRROR:
  - use_axis (array[3], bool): axes [X,Y,Z]
  - use_bisect_axis (array[3], bool): bisect axes
  - use_clip (bool): clip
  - use_mirror_merge (bool): merge
  - merge_threshold (float, 0-1): distance merge
  - mirror_object (string): nom objet mirror (optionnel)

SOLIDIFY:
  - thickness (float, -10 to 10): épaisseur
  - offset (float, -1 to 1): offset (-1=inside, 0=center, 1=outside)
  - use_even_offset (bool): even offset
  - use_quality_normals (bool): high quality normals
  - use_rim (bool): fill rim
  - use_rim_only (bool): rim only

BOOLEAN:
  - operation (enum): DIFFERENCE, UNION, INTERSECT
  - solver (enum): EXACT, FLOAT, MANIFOLD
  - object (string): nom objet cible
  - use_self (bool): self intersection
  - use_hole_tolerant (bool): hole tolerant

SUBSURF:
  - levels (int, 0-6): viewport subdivisions
  - render_levels (int, 0-6): render subdivisions
  - subdivision_type (enum): CATMULL_CLARK, SIMPLE
  - use_creases (bool): use creases
  - quality (int, 1-6): quality

BEVEL:
  - width (float, 0-1000): width
  - segments (int, 1-100): segments
  - profile (float, 0-1): profile shape
  - limit_method (enum): NONE, ANGLE, WEIGHT, VGROUP
  - angle_limit (float, 0-3.14159): angle limit (radians)
  - use_clamp_overlap (bool): clamp overlap
  - offset_type (enum): OFFSET, WIDTH, DEPTH, PERCENT

SCREW:
  - angle (float, -1000 to 1000): angle (radians)
  - steps (int, 2-512): steps
  - render_steps (int, 2-512): render steps
  - iterations (int, 1-100): iterations
  - screw_offset (float, -1000 to 1000): offset along axis
  - use_smooth_shade (bool): smooth shading
  - use_merge_vertices (bool): merge verts
  - merge_threshold (float, 0-1): merge distance

SIMPLE_DEFORM:
  - deform_method (enum): TWIST, BEND, TAPER, STRETCH
  - angle (float, -6.28 to 6.28): angle/factor
  - deform_axis (enum): X, Y, Z
  - lock_x (bool): lock X
  - lock_y (bool): lock Y
  - origin (string): nom objet origin (optionnel)

* Sortie
{
  "name": "Cube",
  "modifier": "MyArray",
  "type": "ARRAY",
  "configured_params": {
    "count": 8,
    "relative_offset_displace": [3.0, 0.5, 0.0],
    "use_merge_vertices": true
  }
}

* Garde-fous
  * Objet existe
  * Modifier existe sur cet objet
  * Paramètres valides pour le type de modifier
  * Clamp valeurs numériques dans ranges
  * Vérifier objets référencés existent (mirror_object, boolean object, etc)
  * Error: "Object not found" / "Modifier not found" / "Invalid parameter" / "Referenced object not found"

* Tests
  # Prep: Cube avec Array modifier "MyArray"
  blender-modifier-configure(name="Cube", modifier_name="MyArray", 
    params={count: 8, relative_offset_displace: [3,0.5,0]})
  # → Array configuré: 8 copies, offset (3, 0.5, 0)
  
  # Mirror
  blender-modifier-configure(name="MirrorObj", modifier_name="Mirror",
    params={use_axis: [true,true,false], use_clip: true})
  # → Mirror X+Y avec clipping
  
  # Boolean
  blender-modifier-configure(name="BoolA", modifier_name="Boolean",
    params={operation: "UNION", solver: "EXACT", object: "BoolB"})
  # → Boolean union avec BoolB
Tool 10 - blender-modifier-configure-array (SHORTCUT spécialisé)

A

blender-dev-exec-python


✅ SPEC TOOL 10 - blender-modifier-configure-array
Note: Ce tool est un wrapper spécialisé qui simplifie les patterns Array courants. Alternative à blender-modifier-configure avec preset modes.

yaml
* Identité
  * name: blender-modifier-configure-array
  * Description: Configure Array modifier avec patterns prédéfinis (linear/circular/grid)
  * Catégorie: modifier
  * Tags: [array, modifier, pattern, duplicate]

* Contexte
  * Mode requis: OBJECT
  * Sélection requise: Non
  * API: bpy.data.objects[name].modifiers[modifier_name]

* Entrées
{
  "type": "object",
  "properties": {
    "name": {"type": "string", "description": "Nom objet"},
    "modifier_name": {"type": "string", "description": "Nom du Array modifier"},
    "pattern": {
      "type": "string",
      "enum": ["LINEAR", "CIRCULAR", "GRID", "CURVE_FIT", "CUSTOM"],
      "default": "LINEAR",
      "description": "Pattern prédéfini"
    },
    "count": {"type": "integer", "minimum": 1, "maximum": 10000, "default": 5},
    "offset": {
      "items": {"type": "number"},
      "minItems": 3,
      "maxItems": 3,
      "default": [1.2, 0, 0],
      "description": "Offset relatif pour LINEAR/GRID"
    },
    "grid_counts": {
      "items": {"type": "integer"},
      "minItems": 2,
      "maxItems": 2,
      "description": "Pour GRID: [count_x, count_y]"
    },
    "use_merge": {"type": "boolean", "default": false},
    "merge_threshold": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.01},
    "offset_object": {
      "anyOf": [{"type": "string"}, {"type": "null"}],
      "description": "Pour CIRCULAR: nom objet offset (empty)"
    },
    "curve_object": {
      "anyOf": [{"type": "string"}, {"type": "null"}],
      "description": "Pour CURVE_FIT: nom courbe"
    }
  },
  "required": ["name", "modifier_name"],
  "additionalProperties": false
}

* Sortie
{
  "name": "Cube",
  "modifier": "MyArray",
  "pattern": "LINEAR",
  "count": 10,
  "offset": [1.2, 0.0, 0.0],
  "configuration": "success"
}

* Patterns prédéfinis:

LINEAR:
  - count copies espacées de offset
  - relative_offset_displace = offset
  
CIRCULAR:
  - count copies autour offset_object (empty)
  - use_object_offset = true
  - rotation de l'empty = 360/count
  
GRID:
  - 2 Array modifiers: X puis Y
  - grid_counts = [nx, ny]
  - offsets calculés
  
CURVE_FIT:
  - fit_type = FIT_CURVE
  - curve = curve_object
  - ajuste count selon longueur

CUSTOM:
  - Utilise params fournis directement
  - Pas de preset

* Garde-fous
  * Objet existe
  * Modifier existe (type ARRAY)
  * Pour CIRCULAR: offset_object existe et type EMPTY
  * Pour CURVE_FIT: curve_object existe et type CURVE
  * Pour GRID: créer 2 modifiers si nécessaire
  * Error: "Modifier not ARRAY type" / "Offset object not found" / "Curve object not found"

* Tests
  # Linear
  blender-modifier-configure-array(name="Cube", modifier_name="Array", 
    pattern="LINEAR", count=10, offset=[1.5,0,0])
  # → 10 copies, espacées de 1.5 unités sur X
  
  # Circular (avec empty "Center" pré-créé)
  blender-modifier-configure-array(name="Cube", modifier_name="Array",
    pattern="CIRCULAR", count=12, offset_object="Center")
  # → 12 copies en cercle autour de Center
  
  # Grid
  blender-modifier-configure-array(name="Cube", modifier_name="Array",
    pattern="GRID", grid_counts=[5,4], offset=[1.5,1.5,0])
  # → Grille 5x4
Continuer avec Tool 11 - blender-modifier-configure-mirror ?

