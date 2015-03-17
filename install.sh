pip install wget
python -m wget https://raw.githubusercontent.com/mjirik/lisa/master/requirements_pip.txt
python -m wget https://raw.githubusercontent.com/mjirik/lisa/master/requirements_conda.txt


conda install --yes --file requirements_conda.txt

# 2. easy_install requirements simpleITK  
easy_install -U --user SimpleITK mahotas

# 3. pip install our packages pyseg_base and dicom2fem
pip install -r requirements_pip.txt --user

mkdir projects

# 4. install gco_python

cd projects
# mkdir gco_python
# cd gco_python
git clone https://github.com/mjirik/gco_python.git 
cd gco_python
# echo `pwd`
make
python setup.py install --user
cd ..
cd ..


# 5. skelet3d - optional for Histology Analyser
# sudo -u $USER cd ~/projects
# mkdir ~/projects/skelet3d
# mkdir /projects/skelet3d
git clone https://github.com/mjirik/skelet3d.git 
cd skelet3d
mkdir build
cmake ..
make