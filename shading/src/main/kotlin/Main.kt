import app.runApp
import org.jetbrains.skija.IRect
import org.lwjgl.glfw.GLFW.*
import org.lwjgl.glfw.GLFWErrorCallback


fun main() {
    prepareGLFW()

    val bounds = prepareBounds()
    runApp(bounds)
}

fun prepareGLFW() {
    GLFWErrorCallback.createPrint(System.err).set()
    if (!glfwInit()) {
        throw IllegalStateException("Unable to initialize GLFW")
    }
}

fun prepareBounds(): IRect {
    val vidMode = glfwGetVideoMode(glfwGetPrimaryMonitor())!!

    val width = (vidMode.width() * 0.75).toInt()
    val height = (vidMode.height() * 0.75).toInt()

    return IRect.makeXYWH(
        maxOf(0, (vidMode.width() - width) / 2),
        maxOf(0, (vidMode.height() - height) / 2),
        width,
        height
    )!!
}