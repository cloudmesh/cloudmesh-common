#cd cloudmesh-common
#pip install -e .
#cd ..
pip install -r requirements-dev.txt
cd ../cloudmesh-common; make dist; make local
cd ../cloudmesh-cmd5; make dist; make local
cd ../cloudmesh-sys; make dist; make local
cd ../cloudmesh-bar; make dist; make local
cd ../cloudmesh-bumpversion; make dist; make local
cd ../cloudmesh-vpn; make dist; make local
cd ../cloudmesh-gpu; make dist; make local
cd ../cloudmesh-rivanna; make dist; make local
#cd ../cloudmesh-catalog; make dist; make local
#cd ../cloudmesh-configuration; make dist; make local
cd ../cloudmesh-common
#cms info
#cms info path
#cms info commands
cms banner ERRORS
cms info errors
cms banner DONE
cms version
cms help
