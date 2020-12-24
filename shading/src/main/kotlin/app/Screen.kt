package app

import org.jetbrains.skija.Canvas

interface Screen {
    fun onDraw(canvas: Canvas)
    fun onMouseButton(button: Int, action: Int, mods: Int)
    fun onCursor(x: Int, y: Int)
    fun onWindowSize(width: Int, height: Int)
    fun onKey(key: Int, scancode: Int, action: Int, mods: Int)
}