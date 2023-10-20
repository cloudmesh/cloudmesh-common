#!/bin/bash
set -e
set -u
cat << 'EOF' > convert.sh
set -x
apt-get install -y patch
conda install -y conda-build anaconda-client
conda skeleton pypi $PIP_PACKAGE
conda build -c $ANACONDA_CHANNEL --python 3.9 $PIP_PACKAGE
CONDA_OUTPUT=/opt/conda/conda-bld/linux-64
conda convert --platform all $CONDA_OUTPUT/*.tar.bz2
anaconda login --username $ANACONDA_USER --password $ANACONDA_PASSWORD
(anaconda package --create $ANACONDA_OWNER/$PIP_PACKAGE || true)
for platform in linux-32 linux-64 win-32 win-64 osx-64; do
    echo "Uploading file for $platform"
    anaconda upload --user $ANACONDA_OWNER $platform/$(ls $platform)
done
EOF
chmod a+x convert.sh
docker run --rm -v "$PWD/convert.sh":/work/convert.sh -w /work \
  -e PIP_PACKAGE=$PIP_PACKAGE \
  -e ANACONDA_USER=$ANACONDA_USER \
  -e ANACONDA_PASSWORD=$ANACONDA_PASSWORD \
  -e ANACONDA_OWNER=$ANACONDA_OWNER \
  -e ANACONDA_CHANNEL=$ANACONDA_CHANNEL \
  continuumio/miniconda3 ./convert.sh
