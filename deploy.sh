
# 1. Catch all the hosts
# 2. Download Blender




# 2. For each host, ssh into the host, copy the project, configure Blender
# 3. Start the master
# 4. Start the daemons for each worker node.
# 5. Install python packages




#!/bin/sh

if [[ $# -lt 1 ]] ; then
        echo ""
        echo "usage: deploy.sh [nodes]"
        echo "for example: deploy.sh node105,node106,node107"
        echo ""
        exit 1

fi
master_port=7777
worker_port=9999

echo "Deploying the blender farm cluster on ${1}"
nodes=${1}
IFS=',' read -ra node_list <<< "$nodes"; unset IFS
master=${node_list[0]}
worker=${node_list[@]:1}
echo "master is "$master
echo "worker is "$worker
blender_path="/local/$USER/blender-3.3.1-linux-x64/blender"
repo="https://github.com/BrandonKroes/DAS-BR.git"

#rm -rf /var/scratch/$USER/blender-3.3.1-linux-x64
#rm -r /home/$USER/blender; mkdir /home/$USER/blender

#wget -O /var/scratch/$USER/blender-3.3.1-linux-x64.tar.xz https://ftp.nluug.nl/pub/graphics/blender/release/Blender3.3/blender-3.3.1-linux-x64.tar.xz
#tar -xvf /var/scratch/$USER/blender-3.3.1-linux-x64.tar.xz -C /home/$USER/blender

echo "starting the master!"
# clone the project to master


# removing possible residual data
ssh -T $master "rm -r /local/$USER/; mkdir /local/$USER/ && exit"

ssh -T $master "nohup git clone https://github.com/BrandonKroes/DAS-BR.git /local/$USER/DAS-BR"
ssh -T $master "truncate -s 0 /local/$USER/DAS-BR/config/conf.yaml"
ssh -T $master 'echo $"master:" >> /local/$USER/DAS-BR/config/conf.yaml'
ssh -T $master 'echo $" host: '$master'" >> /local/$USER/DAS-BR/config/conf.yaml'

ssh -T $master 'echo $" port: '$master_port'" >> /local/$USER/DAS-BR/config/conf.yaml'

#ssh -T $master "nohup python3.6 /local/$USER/DAS-BR/test/master-test.py > master.log &"


for n in ${worker}; do

# removing possible residual data
ssh -T $n "rm -rf /local/$USER/ && exit"
# Remaking the directory
ssh -T $n "mkdir /local/$USER/ && exit"

echo "Copying blender"
ssh -T $n "cp -r -f /home/$USER/blender/. /local/$USER/ && exit"

echo "Copying the project to worker $n"
ssh -T $n "nohup git clone https://github.com/BrandonKroes/DAS-BR.git /local/$USER/DAS-BR/"

echo "writing config for worker $n"
# setting up a basic config
ssh -T $n 'echo $"worker:" >> /local/$USER/DAS-BR/config/conf.yaml'
ssh -T $n 'echo $" blender_path: '$blender_path'" >> /local/$USER/DAS-BR/config/conf.yaml'
ssh -T $n 'echo $" host: '$n'" >> /local/$USER/DAS-BR/config/conf.yaml'
ssh -T $n 'echo $" port: '$worker_port'" >> /local/$USER/DAS-BR/config/conf.yaml'
ssh -T $n 'echo $" cycles_device: 'CUDA'" >> /local/$USER/DAS-BR/config/conf.yaml'
ssh -T $n 'echo $" benchmark_score: 99" >> /local/$USER/DAS-BR/config/conf.yaml'
ssh -T $n 'echo $"master:" >> /local/$USER/DAS-BR/config/conf.yaml'
ssh -T $n 'echo $" host: '$master'" >> /local/$USER/DAS-BR/config/conf.yaml'
ssh -T $n 'echo $" port: '$master_port'" >> /local/$USER/DAS-BR/config/conf.yaml'
ssh -T $n 'module load cuda11.7/toolkit'
echo "starting node $n as worker"
#ssh -T $n "nohup python3.6 /local/$USER/DAS-BR/test/worker-test.py > debug.log &"

done



