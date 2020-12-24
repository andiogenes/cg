package math

import kotlin.math.sqrt

/**
 * Radius-vector in two-dimensional euclidean space.
 */
data class Vec2D(var x: Int = 0, var y: Int = 0)

/**
 * Returns addition of two vectors.
 */
operator fun Vec2D.plus(other: Vec2D): Vec2D =
    Vec2D(this.x + other.x, this.y + other.y)

/**
 * Inverts vector.
 */
operator fun Vec2D.unaryMinus(): Vec2D =
    Vec2D(-x, -y)

/**
 * Returns subtraction of two vectors.
 */
operator fun Vec2D.minus(other: Vec2D): Vec2D =
    this + (-other)

/**
 * Returns vector scaled in `scale` times.
 */
operator fun Vec2D.times(scale: Int): Vec2D =
    Vec2D(x * scale, y * scale)

/**
 * Cross product of two vectors.
 */
infix fun Vec2D.cross(other: Vec2D): Int =
    this.x * other.y - this.y * other.x

/**
 * Dot product of two vectors.
 */
infix fun Vec2D.dot(other: Vec2D): Int =
    this.x * other.x + this.y + other.y

/**
 * Length of vector.
 */
val Vec2D.length: Double
    get() = sqrt((this dot this).toDouble())