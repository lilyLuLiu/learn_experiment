#macos
curl -LO "https://download.fedoraproject.org/pub/fedora/linux/releases/42/Cloud/aarch64/images/Fedora-Cloud-Base-AmazonEC2-42-1.1.aarch64.raw.xz"

vfkit \
    --cpus 2 --memory 2048 \
    --bootloader efi,variable-store=efi-variable-store,create \
    --device virtio-blk,path=Fedora-Cloud-Base-AmazonEC2-42-1.1.aarch64.raw \
    --device virtio-serial,stdio \
    --cloud-init user-data,meta-data

#macos with gui
vfkit \
    --cpus 2 --memory 2048 \
    --bootloader efi,variable-store=efi-variable-store,create \
    --device virtio-blk,path=Fedora-Cloud-Base-AmazonEC2-42-1.1.aarch64.raw \
    --cloud-init user-data,meta-data \
    --device virtio-input,keyboard --device virtio-input,pointing --device virtio-gpu,width=800,height=600 --gui





