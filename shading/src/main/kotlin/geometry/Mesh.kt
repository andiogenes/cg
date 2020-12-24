package geometry

import math.Vec3D

typealias Triangle = Triple<Int, Int, Int>

class Mesh(
    val vertices: Array<Vec3D>,
    val vertexNormals: Array<Vec3D>,

    val triangles: Array<Triangle>,
    val triangleNormals: Array<Vec3D>,
)