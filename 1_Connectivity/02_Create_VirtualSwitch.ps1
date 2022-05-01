# ------------------ Configure Networking ---------------------- #
# Create Virtual Switch
New-VMSwitch -Name "Default Switch" -SwitchType Internal

#Get Index
$InterfaceIndex = (Get-NetAdapter -Name "vEthernet (Default Switch)").ifIndex

do {
    Start-Sleep -Seconds 10
    $IPAddress = (Get-NetIPAddress -AddressFamily IPv4  -InterfaceIndex $InterfaceIndex).IPAddress
} while($null -eq $IPAddress)

# Configure other IPs
$octets = $IPAddress -split "\."
$octets[3] = 1
$GatewayIP = $octets -join "."
$octets[3] = 0
$NatIP = $octets -join "."
$octets[3] = 100
$StartIP = $octets -join "."
$octets[3] = 200
$EndIP = $octets -join "."
$InternalIPInterfaceAddressPrefix = $NatIP + "/24"

# Set Gateway IP Address
New-NetIPAddress -IPAddress $GatewayIP -PrefixLength 24 -InterfaceIndex $InterfaceIndex

# Create Nat
New-NetNat -Name "Default Switch" -InternalIPInterfaceAddressPrefix $InternalIPInterfaceAddressPrefix

# Install DHCP Server
Install-WindowsFeature -Name 'DHCP' -IncludeManagementTools

# Add
netsh dhcp add securitygroups
Restart-Service dhcpserver

# Add the DHCP Server to the default local security groups and restart the server.
Add-DhcpServerV4Scope -Name "AzureIoTEdgeScope" -StartRange $StartIP -EndRange $EndIP -SubnetMask 255.255.255.0 -State Active

# Assign the NAT and gateway IP addresses you created in the earlier section to the DHCP server, and restart the server to load the configuration.
Set-DhcpServerV4OptionValue -ScopeID $NatIP -Router $GatewayIP
Restart-service dhcpserver