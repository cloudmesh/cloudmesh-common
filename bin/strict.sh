#cd cloudmesh-common
#pip install -e .
#cd ..
cd ../cloudmesh-common; pip install -e . --config-settings editable_mode=strict
cd ../cloudmesh-cmd5; pip install -e . --config-settings editable_mode=strict
cd ../cloudmesh-sys; pip install -e . --config-settings editable_mode=strict
cd ../cloudmesh-bar; pip install -e . --config-settings editable_mode=strict
cd ../cloudmesh-bumpversion; pip install -e . --config-settings editable_mode=strict
cd ../cloudmesh-vpn; pip install -e . --config-settings editable_mode=strict
cd ../cloudmesh-gpu; pip install -e . --config-settings editable_mode=strict
cd ../cloudmesh-rivanna; pip install -e . --config-settings editable_mode=strict
#cd ../cloudmesh-catalog; pip install -e .
#cd ../cloudmesh-configuration; pip install -e .
cd ../cloudmesh-common
#cms info
#cms info path
#cms info commands
cms banner ERRORS
cms info errors
cms banner DONE
cms version
cms help
