cmake_minimum_required(VERSION 3.16)
project(JobShopSchedulingTransportOptimizer 
    VERSION 1.0.0 
    DESCRIPTION "Job Shop Scheduling with Transport Times Optimizer"
    LANGUAGES CXX
)

# ===== CMAKE SETTINGS =====
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# ===== COMPILER FLAGS =====
if(MSVC)
    add_compile_options(/W4 /WX /permissive-)
    set(CMAKE_CXX_FLAGS_RELEASE "/O2 /DNDEBUG")
    set(CMAKE_CXX_FLAGS_DEBUG "/Zi /Od /RTC1")
elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra -Wpedantic -Wconversion)
    if(MINGW)
        # ✅ Usunąłem -static-libwinpthread (nie istnieje w UCRT64)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -static-libgcc -static-libstdc++")
    endif()
    set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
    set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")
endif()

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Compiler: ${CMAKE_CXX_COMPILER_ID}")

# ===== INCLUDE DIRECTORIES =====
include_directories(include)

# ===== SOURCE FILES =====
file(GLOB_RECURSE CORE_SOURCES
    src/core/*.cpp
    src/genetic/*.cpp
    src/greedy/*.cpp
    src/exact/*.cpp
    src/io/*.cpp
)

message(STATUS "Found core sources: ${CORE_SOURCES}")

# ===== PYBIND11 DISCOVERY =====
message(STATUS "Searching for pybind11...")

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG QUIET)

if(NOT pybind11_FOUND)
    if(WIN32)
        find_package(pybind11 CONFIG PATHS
            "${CMAKE_CURRENT_SOURCE_DIR}/.venv/Lib/site-packages/pybind11/share/cmake"
            "${CMAKE_CURRENT_SOURCE_DIR}/.venv/Lib/site-packages/pybind11/share/cmake/pybind11"
            QUIET
        )
    elseif(APPLE)
        find_package(pybind11 CONFIG PATHS
            "${CMAKE_CURRENT_SOURCE_DIR}/.venv/lib/python*/site-packages/pybind11/share/cmake"
            QUIET
        )
    else()
        find_package(pybind11 CONFIG PATHS
            "${CMAKE_CURRENT_SOURCE_DIR}/.venv/lib/python*/site-packages/pybind11/share/cmake"
            QUIET
        )
    endif()
endif()

if(NOT pybind11_FOUND)
    message(FATAL_ERROR "pybind11 not found! Install via: pip install pybind11")
endif()

message(STATUS "✓ pybind11 found at: ${pybind11_DIR}")

# ===== PYTHON BINDINGS MODULE =====
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/bindings/bindings.cpp")
    set(BINDING_FILE "bindings/bindings.cpp")
elseif(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/bindings/jobshop_bindings.cpp")
    set(BINDING_FILE "bindings/jobshop_bindings.cpp")
else()
    message(FATAL_ERROR "Cannot find bindings file in bindings/ directory!")
endif()

message(STATUS "Using binding file: ${BINDING_FILE}")

pybind11_add_module(jobshop_bindings 
    ${BINDING_FILE}
    ${CORE_SOURCES}
)

target_include_directories(jobshop_bindings PRIVATE include)

set_target_properties(jobshop_bindings PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/python_module"
)

if(MINGW)
    set_target_properties(jobshop_bindings PROPERTIES
        INTERPROCEDURAL_OPTIMIZATION OFF
    )
endif()

message(STATUS "✓ Python module: ${CMAKE_BINARY_DIR}/python_module")

# ===== CLI EXECUTABLE =====
add_executable(jobshop_optimizer 
    src/main.cpp
    ${CORE_SOURCES}
)

target_include_directories(jobshop_optimizer PRIVATE include)

set_target_properties(jobshop_optimizer PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

message(STATUS "✓ CLI executable: ${CMAKE_BINARY_DIR}/bin")

# ===== SUMMARY =====
message(STATUS "")
message(STATUS "=== Build Configuration ===")
message(STATUS "Project: ${PROJECT_NAME} v${PROJECT_VERSION}")
message(STATUS "C++ Standard: C++${CMAKE_CXX_STANDARD}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Compiler: ${CMAKE_CXX_COMPILER_ID}")
message(STATUS "pybind11: ${pybind11_VERSION}")
message(STATUS "")
message(STATUS "Targets to build:")
message(STATUS "  • Python Module: jobshop_bindings")
message(STATUS "  • CLI Executable: jobshop_optimizer")
message(STATUS "")
