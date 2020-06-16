# -*- mode: ruby -*-
# vi: set ft=ruby :

# # Install these plugins into vagrant
# required_plugins = %w(vagrant-docker-compose)
# #
# plugins_to_install = required_plugins.select { |plugin| not Vagrant.has_plugin? plugin }
# if not plugins_to_install.empty?
#   puts "Installing plugins: #{plugins_to_install.join(' ')}"
#   if system "vagrant plugin install #{plugins_to_install.join(' ')}"
#     exec "vagrant #{ARGV.join(' ')}"
#   else
#     abort "Installation of one or more plugins has failed. Aborting."
#   end
# end

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "opensuse/Tumbleweed.x86_64"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  #config.vm.network "forwarded_port", guest: 80, host: 80
  #config.vm.network "forwarded_port", guest: 3336, host: 3336 # forward the port of the SQL database

  # ssh port of the localhost
  # config.vm.network :forwarded_port, guest: 22, host: 2222, id: "ssh"

  # Virtualbox specific settings (s.a. resource allocation)
  config.vm.provider "virtualbox" do |v|
      v.memory = 1024
  end

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access
  # config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  # config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
  #   vb.memory = "1024"
  # end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Enable provisioning with a shell script. Additional provisioners such as
  # Ansible, Chef, Docker, Puppet and Salt are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL

    # Install some packages
    sudo zypper -n refresh

    # On Ubuntu this is...
    # $ sudo echo grub-pc hold | dpkg --set-selections # Don't upgrade GRUB because it requires manual intervention during upgrade...
    # $ sudo apt-get update
    # and optionally
    # $ sudo apt-get full-upgrade -y # time-consuming


    # (On Ubuntu this is sudo apt-get install -y some_package)
    sudo zypper -n install zsh git tmux
    sudo zypper -n install python-curses # for ranger


    # Development tools
    sudo zypper -n install cmake
    sudo zypper -n install gcc-c++

    # login shell: zsh
    usermod -s /bin/zsh vagrant
  SHELL

  config.vm.provision "shell", privileged: false, inline: <<-SHELL

    # Install dot_baby
    git clone https://gitlab.com/dsakurai/dot_baby.git /home/vagrant/.dot_baby
    /home/vagrant/.dot_baby/details/setup/setup.sh

    # Build Boost
    mkdir /home/vagrant/build
    cd /home/vagrant/build
    cmake /vagrant -DCMAKE_INSTALL_PREFIX=/home/vagrant/local
    make

    # and test
    mkdir /home/vagrant/build-test
    cd    /home/vagrant/build-test
    cmake -DBOOST_ROOT=/home/vagrant/local -DBoost_ARCHITECTURE=-x64 /vagrant/test
    make

    ./test
    if [ $? = 0 ]; then
      echo "Linking to boost succeeded"
    else
      echo "Linking to boost from a test executable failed"
    fi

  SHELL

#  config.vm.synced_folder ".", "/vagrant", disabled: true

end
