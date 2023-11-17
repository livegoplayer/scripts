#!/usr/bin/bash

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
create_venv=true

while [ -n "$1" ]; do
    case "$1" in
        --disable-venv)
            create_venv=false
            shift
            ;;
        *)
            shift
            ;;
    esac
done

if $create_venv; then
    echo "Creating python venv..."
    python3 -m venv venv
    source "$script_dir/venv/bin/activate"
    echo "active venv"
fi

echo "Installing torch & xformers..."

cuda_version=$(nvcc --version | grep 'release' | sed -n -e 's/^.*release \([0-9]\+\.[0-9]\+\),.*$/\1/p')
cuda_major_version=$(echo "$cuda_version" | awk -F'.' '{print $1}')
cuda_minor_version=$(echo "$cuda_version" | awk -F'.' '{print $2}')

echo "Cuda Version:$cuda_version"

if (( cuda_major_version >= 12 )) || (( cuda_major_version == 11 && cuda_minor_version >= 8 )); then
    echo "install torch 2.0.0+cu118"
    pip install torch==2.0.0+cu118 torchvision==0.15.1+cu118 --extra-index-url https://download.pytorch.org/whl/cu118
    pip install xformers==0.0.19
elif (( cuda_major_version == 11 && cuda_minor_version == 6 )); then
    echo "install torch 1.12.1+cu116"
    pip install torch==1.12.1+cu116 torchvision==0.13.1+cu116 --extra-index-url https://download.pytorch.org/whl/cu116
    pip install --upgrade git+https://github.com/facebookresearch/xformers.git@0bad001ddd56c080524d37c84ff58d9cd030ebfd
    pip install triton==2.0.0.dev20221202
else
    echo "Unsupported cuda version:$cuda_version"
    exit 1
fi

echo "Installing deps..."
cd "$script_dir/sd-scripts" || exit

pip install --upgrade -r requirements.txt
pip install --upgrade lion-pytorch lycoris-lora dadaptation fastapi uvicorn wandb

cd "$script_dir" || exit

echo "Install completed"

source venv/bin/activate

echo "°²×° bitsandbytes..."
pip install bitsandbytes==0.41.1 --no-deps --prefer-binary --extra-index-url=https://jllllll.github.io/bitsandbytes-windows-webui --force
pip install --upgrade --no-deps pytorch-optimizer prodigyopt

#git clone https://github.com/timdettmers/bitsandbytes.git

#cd bitsandbytes

# CUDA_VERSIONS in {110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 120}
# make argument in {cuda110, cuda11x, cuda12x}
# if you do not know what CUDA you have, try looking at the output of: python -m bitsandbytes
# export LD_LIBRARY_PATH=/usr/local/cuda-12.1/targets/x86_64-linux/lib
# export LD_LIBRARY_PATH=/usr/local/cuda-12.1/targets/x86_64-linux/lib/stubs:$LD_LIBRARY_PATH
# export CONDA_PREFIX=/usr/local/miniconda3
# export CUDA_HOME=/usr/local/cuda-12.1

#export PATH=/usr/local/cuda/bin:$PATH
#export LD_LIBRARY_PATH=/usr/local/cuda/targets/x86_64-linux/lib
#export CUDA_HOME=/usr/local/cuda

CUDA_VERSION=118 make cuda11x

pip install --upgrade -r requirements.txt







