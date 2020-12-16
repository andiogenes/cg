cmake_minimum_required(VERSION 3.17)
project(scene)

find_package(raylib 2.5.0 REQUIRED)

set(CMAKE_C_STANDARD 11)

add_executable(scene main.c)

target_link_libraries(scene raylib)