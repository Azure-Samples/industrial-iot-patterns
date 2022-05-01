# Copy pn.json file to EFLOW VM
Invoke-EflowVmCommand "mkdir -p opcconfig"
Copy-EflowVMFile -fromFile "opcconfig.json" -toFile ~\opcconfig\opcconfig.json -pushFile
