#windows
#New-VMSwitch -Name "FedoraSwitch" -SwitchType Internal
#Go to Control Panel > Network Connections
#Right-click your physical adapter (e.g. Wi-Fi or Ethernet)
#Enable Internet Connection Sharing (ICS)
#Share it with the new vEthernet (FedoraSwitch) adapter

param(
    [string]$User = "fedora",
    [string]$Password = "fedora"
)

wsl genisoimage -output cidata.iso -volid cidata -joliet -rock cidata/
#wsl genisoimage -output cidata.iso -volid cidata -joliet -rock user-data meta-data
$source = ""
$generation = 1

if ($imageType = "vhdfixed") {
    $IMAGE = "https://ohioix.mm.fcix.net/fedora/linux/releases/41/Cloud/x86_64/images/Fedora-Cloud-Base-Azure-41-1.4.x86_64.vhdfixed.xz"
    #$IMAGE = "https://download.fedoraproject.org/pub/fedora/linux/releases/42/Cloud/x86_64/images/Fedora-Cloud-Base-Azure-42-1.1.x86_64.vhdfixed.xz"
    curl -LO $IMAGE
    wsl xz -d Fedora-*.vhdfixed.xz
    wsl mv Fedora-*.vhdfixed Fedora-Cloud-Base.vhd
    $source = "Fedora-Cloud-Base.vhd"
} else {
    $IMAGE = "https://download.fedoraproject.org/pub/fedora/linux/releases/42/Cloud/x86_64/images/Fedora-Cloud-Base-Generic-42-1.1.x86_64.qcow2"
    wsl qemu-img convert -f qcow2 Fedora-Cloud-Base-Generic-42-1.1.x86_64.qcow2 -O vhdx fedora-42.vhdx
    cp fedora-42.vhdx fedora.vhdx  
    $source = "fedora.vhdx"
    $generation = 2
} 





$current = (Get-Location).Path

$vmName = "FedoraVM"
New-VM -Name $vmName `
    -MemoryStartupBytes 2GB `
    -VHDPath "$current\$source" `
    -Generation $generation `
    -SwitchName "Default Switch"

Write-Output "Attach iso driver"
Add-VMDvdDrive -VMName $vmName -Path "$current\cidata.iso"
Set-VMFirmware -VMName $VMName -SecureBootTemplate MicrosoftUEFICertificateAuthority

Start-VM -Name $vmName
while ((Get-VM -Name $vmName).State -ne 'Running') {
    Write-Host "Waiting for VM $vmName to start..."
    Start-Sleep -Seconds 2
}
Start-Sleep -Seconds 20
$IP = (Get-VMNetworkAdapter -VMName $vmName).IPAddresses[0]
Write-Output "VM IP: $IP, User: $User, Password: $Password"
