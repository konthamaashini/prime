import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # Set GAZEBO_PLUGIN_PATH to include your package's lib directory

    # Define package and file paths
    package_name = 'fish_hpurv'
    xacro_file = 'urdf/fish_robot.urdf'
    world_file = 'worlds/hotel.world'

    # Paths to model and world files
    model_file_path = os.path.join(get_package_share_directory(package_name), xacro_file)
    world_file_path = os.path.join(get_package_share_directory('fish_hpurv'), world_file)

    # Process the xacro file to generate the robot description (URDF)
    robot_description = xacro.process_file(model_file_path).toxml()

    # Include the Gazebo launch file from gazebo_ros with necessary plugins
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ]),
        launch_arguments={
            'world': world_file_path,
            'extra_gazebo_args': '--verbose -s libgazebo_ros_init.so -s libgazebo_ros_factory.so'
        }.items()
    )

    # Robot State Publisher Node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    # Spawn the robot in Gazebo
    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'robot', '-topic', 'robot_description'],
        output='screen'
    )

    # Suppress ALSA warnings by redirecting stderr (optional)
    suppress_alsa_warnings = SetEnvironmentVariable(
        name='ALSA_CONFIG_PATH',
        value='/etc/alsa/alsa.conf'
    )

    # Create the launch description and add all actions
    launch_description = LaunchDescription()
    launch_description.add_action(suppress_alsa_warnings)
    launch_description.add_action(gazebo_launch)
    launch_description.add_action(robot_state_publisher_node)
    launch_description.add_action(spawn_entity_node)

    return launch_description