#cd cloudmesh-common
#pip install -e .
#cd ..
cd ../cloudmesh-common; make dist; make local
cd ../cloudmesh-cmd5; make dist; make local
cd ../cloudmesh-bumpversion; make dist; make local
cd ../cloudmesh-common
cms help
#cms info
#cms info path
#cms info commands
cms banner ERRORS
cms info errors
cms banner DONE
cms version
