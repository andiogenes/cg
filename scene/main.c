#include "raylib.h"

int main()
{
    const int screenWidth = 1280;
    const int screenHeight = 768;

    SetConfigFlags(FLAG_MSAA_4X_HINT);
    InitWindow(screenWidth, screenHeight, "Simplest realistic scene with OpenGL");

    // Камера
    // ----------------------------------------------------------------------------------
    Camera camera = {
            { -2.0f, 1.5f, -0.0f },
            { 0.0f, 1.8f, 0.0f },
            { 0.0f, 1.0f, 0.0f },
            60.0f,
            CAMERA_PERSPECTIVE
    };
    // ----------------------------------------------------------------------------------

    // Скайбокс
    // ----------------------------------------------------------------------------------
    Mesh skyCube = GenMeshCube(100.0f, 100.0f, 100.0f);
    Model skybox = LoadModelFromMesh(skyCube);

    skybox.materials[0].shader = LoadShader("resources/shaders/glsl330/skybox.vs", "resources/shaders/glsl330/skybox.fs");
    SetShaderValue(skybox.materials[0].shader, GetShaderLocation(skybox.materials[0].shader, "environmentMap"), (int[1]){ MAP_CUBEMAP }, UNIFORM_INT);
    SetShaderValue(skybox.materials[0].shader, GetShaderLocation(skybox.materials[0].shader, "vflipped"), (int[1]){ 1 }, UNIFORM_INT);

    Shader shdrCubemap = LoadShader("resources/shaders/glsl330/cubemap.vs", "resources/shaders/glsl330/cubemap.fs");
    SetShaderValue(shdrCubemap, GetShaderLocation(shdrCubemap, "equirectangularMap"), (int[1]){ 0 }, UNIFORM_INT);

    Texture2D panorama = LoadTexture("resources/evening_road_01_2k.hdr");

    skybox.materials[0].maps[MAP_CUBEMAP].texture = GenTextureCubemap(shdrCubemap, panorama, 1024, UNCOMPRESSED_R8G8B8A8);

    UnloadTexture(panorama);
    // ----------------------------------------------------------------------------------

    // Ленин
    // ----------------------------------------------------------------------------------
    Model lenin = LoadModel("resources/lenin.obj");
    // ----------------------------------------------------------------------------------

    // Гранитный монумент
    // ----------------------------------------------------------------------------------
    Model monument = LoadModel("resources/monument.obj");
    // ----------------------------------------------------------------------------------

    // Платформа
    // ----------------------------------------------------------------------------------
    Model platform = LoadModel("resources/platform.obj");
    // ----------------------------------------------------------------------------------

    // Правительство Алтайского края
    // ----------------------------------------------------------------------------------
    Model government = LoadModel("resources/govt.obj");
    // ----------------------------------------------------------------------------------

    // Земля
    // ----------------------------------------------------------------------------------
    Model ground_1 = LoadModel("resources/ground_1.obj");
    Model ground_2 = LoadModel("resources/ground_2.obj");
    // ----------------------------------------------------------------------------------

    // Бордюр
    // ----------------------------------------------------------------------------------
    Model border = LoadModel("resources/border.obj");
    // ----------------------------------------------------------------------------------

    // Трава
    // ----------------------------------------------------------------------------------
    Model grass = LoadModel("resources/grass.obj");
    // ----------------------------------------------------------------------------------

    // Пихтовое дерево
    // ----------------------------------------------------------------------------------
    Model tree = LoadModel("resources/cedar_tree_model.obj");
    Model bark = LoadModel("resources/bark.obj");

    Vector3 treeCoordinates[] = {
            {1.75f, 0, 4.5f},
            {0.5f, 0, 4.5f},
            {-0.75f, 0, 4.5f},
            {5.25f, 0, 3.65f},
            {5.25f, 0, 4.65f},
            {5.25f, 0, 5.65f},
            {4.5f, 0, 1.65f},
            {6.0f, 0, 1.65f},
            {12.5f, -0.5f, 1.65f},
            {14.0f, -0.5f, 1.65f},
    };
    // ----------------------------------------------------------------------------------


    SetCameraMode(camera, CAMERA_FIRST_PERSON);

    SetTargetFPS(60);

    while (!WindowShouldClose())
    {
        UpdateCamera(&camera);

        BeginDrawing();

            ClearBackground(RAYWHITE);

            BeginMode3D(camera);
                DrawModel(skybox, (Vector3){0, 0, 0}, 1.0f, WHITE);
                DrawModel(lenin, (Vector3){0, 0, 0}, 0.1f, WHITE);
                DrawModel(monument, (Vector3){0, 0, 0}, 0.1f, WHITE);
                DrawModel(platform, (Vector3){0, 0, 0}, 1.0f, WHITE);
                DrawModel(government, (Vector3){0, 0, 0}, 1.0f, WHITE);
                DrawModel(ground_1, (Vector3){0, 0, 0}, 1.0f, WHITE);
                DrawModel(ground_2, (Vector3){0, 0, 0}, 1.0f, WHITE);
                DrawModel(border, (Vector3){0, 0, 0}, 1.0f, WHITE);
                DrawModel(grass, (Vector3){0, 0, 0}, 1.0f, WHITE);
                for (int i = 0; i < sizeof(treeCoordinates)/sizeof(Vector3); i++) {
                    DrawModel(bark, treeCoordinates[i], 0.2f, WHITE);
                    DrawModel(tree, treeCoordinates[i], 0.2f, WHITE);
                    Vector3 inverted = treeCoordinates[i];
                    inverted.z = -inverted.z;
                    DrawModel(bark, inverted, 0.2f, WHITE);
                    DrawModel(tree, inverted, 0.2f, WHITE);
                }
            EndMode3D();

        EndDrawing();
    }

    UnloadShader(skybox.materials[0].shader);
    UnloadTexture(skybox.materials[0].maps[MAP_CUBEMAP].texture);

    UnloadModel(skybox);

    UnloadModel(lenin);
    UnloadModel(monument);
    UnloadModel(platform);
    UnloadModel(government);
    UnloadModel(ground_1);
    UnloadModel(ground_2);
    UnloadModel(border);
    UnloadModel(grass);
    UnloadModel(tree);
    UnloadModel(bark);

    CloseWindow();

    return 0;
}