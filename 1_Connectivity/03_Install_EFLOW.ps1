param(
      [string]$CONNECTION_STRING
)

# ------------------ EFLOW ---------------------- #
#Run each of the following commands to download IoT Edge for Linux on Windows
$msiPath = $([io.Path]::Combine($env:TEMP, 'AzureIoTEdge.msi'))
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest "https://aka.ms/AzEFLOWMSI-CR-X64" -OutFile $msiPath

#Install IoT Edge for Linux on Windows on your device.
Start-Process -Wait msiexec -ArgumentList "/i","$([io.Path]::Combine($env:TEMP, 'AzureIoTEdge.msi'))","/qn"

#Create Linux virtual machine and installs the IoT Edge runtime for you.
Deploy-Eflow -acceptEula yes -acceptOptionalTelemetry no

# Provision EFLOW
Provision-EflowVm -provisioningType ManualConnectionString -devConnString $CONNECTION_STRING