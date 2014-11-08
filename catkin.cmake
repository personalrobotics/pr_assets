cmake_minimum_required(VERSION 2.8.3)
project(pr_ordata)

find_package(catkin REQUIRED COMPONENTS openrave_catkin)
catkin_package()

add_custom_target(${PROJECT_NAME}_data ALL
    COMMAND ${CMAKE_COMMAND} -E copy_directory
            "${PROJECT_SOURCE_DIR}/data"
            "${OpenRAVE_DEVEL_DIR}/${OpenRAVE_DATA_DIR}"
)

# The trailing slash is necessary to prevent CMake from creating a "data"
# directory inside DESTINATION.
# See: http://www.cmake.org/cmake/help/v3.0/command/install.html
install(DIRECTORY "${PROJECT_SOURCE_DIR}/data/"
    DESTINATION "${OpenRAVE_INSTALL_DIR}/${OpenRAVE_DATA_DIR}"
)
