cmake_minimum_required(VERSION 3.16)
project(test)

find_package(Boost REQUIRED
    COMPONENTS
        serialization
)

set(CMAKE_CXX_STANDARD 11)

add_executable(test main.cpp)

target_include_directories(test
        PUBLIC
        "${Boost_INCLUDE_DIRS}"
        )

target_link_libraries(test
        PUBLIC
        "${Boost_LIBRARIES}"
        )
