package app

import skija.SkijaWindow
import geometry.BrokenLine
import math.Vec2D
import math.minus
import org.jetbrains.skija.*
import org.lwjgl.glfw.GLFW.*

fun runApp(bounds: IRect) {
    val windowProps = object {
        var mouseX = 0
        var mouseY = 0
        var screenWidth = bounds.width
        var screenHeight = bounds.height
    }

    val worldScreen = object : Screen {
        override fun onDraw(canvas: Canvas) {
            //TODO("Not yet implemented")
        }

        override fun onMouseButton(button: Int, action: Int, mods: Int) {
            //TODO("Not yet implemented")
        }

        override fun onCursor(x: Int, y: Int) {
            //TODO("Not yet implemented")
        }

        override fun onWindowSize(width: Int, height: Int) {
            //TODO("Not yet implemented")
        }

        override fun onKey(key: Int, scancode: Int, action: Int, mods: Int) {
            //TODO("Not yet implemented")
        }
    }

    SkijaWindow(
        title = "Лабораторная работа 3",
        windowSizeCallback = { w, h ->
            worldScreen.onWindowSize(w, h)
            windowProps.screenWidth = w
            windowProps.screenHeight = h
        },
        cursorPosCallback = { x, y -> windowProps.mouseX = x; windowProps.mouseY = y; worldScreen.onCursor(x, y) },
        mouseButtonCallback = { button, action, mods -> worldScreen.onMouseButton(button, action, mods) },
        keyCallback = { key, scancode, action, mods -> worldScreen.onKey(key, scancode, action, mods) }
    ).run(bounds) {
        clear(0xFF000000.toInt())
        worldScreen.onDraw(this)
    }
}