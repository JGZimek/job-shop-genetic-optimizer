cmake_minimum_required(VERSION 3.10)
project(JobShopSchedulingTransportOptimizer)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# --- Static linking dla MinGW ---
if(MINGW)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -static-libgcc -static-libstdc++")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -static-libgcc")
endif()

include_directories(include)

# --- PYBIND11 DISCOVERY ---
find_package(pybind11 CONFIG QUIET)

if(NOT pybind11_FOUND)
    if(WIN32)
        find_package(pybind11 CONFIG PATHS
            "${CMAKE_CURRENT_SOURCE_DIR}/.venv/Lib/site-packages/pybind11/share/cmake/pybind11"
            QUIET
        )
    endif()
endif()

if(NOT pybind11_FOUND)
    message(FATAL_ERROR "pybind11 not found!")
endif()

message(STATUS "pybind11 found at: ${pybind11_DIR}")

# Zbierz źródła
file(GLOB_RECURSE CORE_SOURCES
    src/core/*.cpp
    src/genetic/*.cpp
    src/greedy/*.cpp
    src/exact/*.cpp
    src/io/*.cpp
)

# --- MODUŁ PYTHON ---
pybind11_add_module(jobshop_bindings 
    bindings/jobshop_bindings.cpp
    ${CORE_SOURCES}
)

# --- CLI executable ---
add_executable(jobshop_optimizer_cli 
    src/main.cpp
    ${CORE_SOURCES}
)
