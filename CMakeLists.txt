cmake_minimum_required(VERSION 3.10)
project(JobShopGeneticOptimizer)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Dodaj katalog z nagłówkami
include_directories(include)

# Zbierz wszystkie pliki źródłowe
file(GLOB_RECURSE SOURCES
    src/*.cpp
)

add_executable(jobshop_test ${SOURCES})
