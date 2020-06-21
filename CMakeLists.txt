# - CMake build/bundle script for Boost Libraries
#   Automates build of Boost, allowing optional builds of library
#   components plus CMake/pkg-config support files

#-----------------------------------------------------------------------
# Copyright (c) 2012-2013, Ben Morgan <bmorgan.warwick@gmail.com>
# Copyright (c) 2012-2013, University of Warwick
#
# Distributed under the OSI-approved BSD 3-Clause License (the "License");
# see accompanying file License.txt for details.
#
# This software is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the License for more information.
#-----------------------------------------------------------------------

cmake_minimum_required(VERSION 3.17)
project(BoostBuilder)

#-----------------------------------------------------------------------
# CORE CONFIGURE/BUILD OPTIONS
#-----------------------------------------------------------------------
# - CMake utilities
include(BoostBuildUtility.cmake)
include(GNUInstallDirs)

# - List libraries to always build.
# We will construct the final list in the setup phase because bootstrap
# is pernickety about the --with/without-libraries being called more
# than once...
# The complete list of libraries provided by Boost can be found by
# running the bootstrap.sh script supplied with Boost as:
#   ./bootstrap.sh --with-libraries=all --show-libraries
set(Boost_with_libraries
  serialization
  system
  CACHE
  STRING
  "List of libraries to be built. Split libraries with ';'."
  )
set(Boost_layout
  system
  CACHE
  STRING
  "naming of the library files (versioned/tagged/system)."
  )
set(Boost_CONFIGURE_ARGS )
set(Boost_BUILD_ARGS )

#-----------------------------------------------------------------------
# - Threading model
option(boost.singlethread "Build Boost single threaded library variants" OFF)
if(boost.singlethread)
  list(APPEND Boost_BUILD_ARGS "threading=multi,single")
else()
  list(APPEND Boost_BUILD_ARGS "threading=multi")
endif()

#-----------------------------------------------------------------------
# - Static libraries
option(boost.staticlibs "Build Boost static library variants" OFF)
if(boost.staticlibs)
  list(APPEND Boost_BUILD_ARGS "link=shared,static")
else()
  list(APPEND Boost_BUILD_ARGS "link=shared")
endif()

#-----------------------------------------------------------------------
# - Release/Debug/Profile libraries
# NB... To support profile libs, need to patch Boost's
# tools/build/src/tools/common.jam
# to add an entry in `local rule runtime-tag` to add a letter
# tag for profiling. Not yet clear if this rule can be overidden
# without patching
set(__boost.buildmodes "variant=release")

option(boost.debuglibs "Build Boost debug library variants" OFF)
if(boost.debuglibs)
  set(__boost.buildmodes "${__boost.buildmodes},debug")
endif()

#option(boost.profilelibs "Build boost profile library variants" OFF)
#if(boost.profilelibs)
#  set(__boost.buildmodes "${__boost.buildmodes},profile")
#endif()

list(APPEND Boost_BUILD_ARGS "${__boost.buildmodes}")

#-----------------------------------------------------------------------
# - Prebuild setup
# Determine the toolset in use by CMake and create needed configure/build
# arguments and custom user-config.jam file as needed
include(${PROJECT_SOURCE_DIR}/BoostToolsetId.cmake)
Boost_Get_ToolsetId(_boost_toolset)

# Need to find out how to add flags on a per variant mode
# ... e.g. "gdwarf" etc as per
#https://cdcvs.fnal.gov/redmine/projects/build-framework/repository/boost-ssi-build/revisions/master/entry/build_boost.sh

# For GCC/Clang (could also add logic for 1y/14)
if (NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD "11" CACHE STRING "C++ standard to be passed to the compiler.")
endif (NOT CMAKE_CXX_STANDARD)
#
set(Boost_CXX_STANDARD_FLAGS "-std=c++${CMAKE_CXX_STANDARD}")

if(CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang")
    set(Boost_CXX_FLAGS_DEFAULT "-isysroot \"${CMAKE_OSX_SYSROOT}\"")
else()
endif()
set(Boost_CXX_FLAGS "${Boost_CXX_FLAGS_DEFAULT}" CACHE STRING "Pass to Boost Build as cxxflags. The C++ standard s.a. c++11 should be passed separately through CMAKE_CXX_STANDARD.")

if(_boost_toolset)
  list(APPEND Boost_CONFIGURE_ARGS "toolset=${_boost_toolset}")
  list(APPEND Boost_BUILD_ARGS     "toolset=${_boost_toolset}")

  set(Boost_USER_CONFIG_JAMFILE "${PROJECT_BINARY_DIR}/user-config.jam")
  file(WRITE "${Boost_USER_CONFIG_JAMFILE}" "using ${_boost_toolset} : : ${CMAKE_CXX_COMPILER} : <cxxflags>\"${Boost_CXX_STANDARD_FLAGS} ${Boost_CXX_FLAGS}\" <linkflags>\"${Boost_CXX_STANDARD_FLAGS} ${Boost_CXX_FLAGS}\" ;")
  set(Boost_BUILD_USER_CONFIG_ARGS "--user-config=${PROJECT_BINARY_DIR}/user-config.jam")
  list(APPEND Boost_BUILD_ARGS     "${Boost_BUILD_USER_CONFIG_ARGS}")
else()
    message(FATAL_ERROR "Failed to detect the toolset")
endif()

# Construct the final library list to install
join_list(Boost_with_libraries "," Boost_WITHLIBRARY_LIST)
list(APPEND Boost_CONFIGURE_ARGS --with-libraries=${Boost_WITHLIBRARY_LIST})

# Parallelize build if possible
include(ProcessorCount)
ProcessorCount(NJOBS)
if(NJOBS EQUAL 0)
  set(NJOBS 1)
endif()

set(b2_commmand 
    ./b2
    -d2 -q -j${NJOBS} install
    --layout=${Boost_layout}
    --debug-configuration # Show which configuration files are actually loaded
    ${Boost_BUILD_ARGS}
    )

# Install the path (Somehow Boost Build doesn't do this propertly on macOS Catalina)
if (APPLE)
    set(b2_command
        ${b2_command}
        && "${CMAKE_CURRENT_SOURCE_DIR}/install_path.sh" "${CMAKE_INSTALL_FULL_LIBDIR}"
        )
endif (APPLE)

#-----------------------------------------------------------------------
# Build Boost
#
include(ExternalProject)
ExternalProject_Add(boost

  SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/boost-source/boost-vcs"

  BUILD_IN_SOURCE     1
  CONFIGURE_COMMAND   <SOURCE_DIR>/bootstrap.sh
                      --prefix=${CMAKE_INSTALL_PREFIX}
                      --libdir=${CMAKE_INSTALL_FULL_LIBDIR}
                      --includedir=${CMAKE_INSTALL_FULL_INCDIR}
                      ${Boost_CONFIGURE_ARGS}
  # All in one build/install step is slightly faster
  BUILD_COMMAND       ""
  INSTALL_COMMAND     ${b2_commmand}
  )
