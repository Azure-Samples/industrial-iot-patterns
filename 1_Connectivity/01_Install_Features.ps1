Install-WindowsFeature -Name Hyper-V -IncludeManagementTools 
Enable-WindowsOptionalFeature -Online -FeatureName "VirtualMachinePlatform" -NoRestart
Restart-Computer