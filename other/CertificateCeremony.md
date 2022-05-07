# Generating Certs for Edge/Device

### Root Cert VM

- Create new Ubuntu LTS VM named "certrootvm"

### Root CA

- Setup using existing openssl config

    - wget https://raw.githubusercontent.com/Azure/iotedge/main/tools/CACertificates/openssl_root_ca.cnf -O openssl.cnf 

    - mkdir -p certs/csr
    - mkdir -p certs/private
    - mkdir -p certs/certs
    - mkdir -p certs/newcerts
    - touch certs/index.txt
    - echo 1000 > certs/serial
    - export CERTIFICATE_OUTPUT_DIR=certs    
 
- Generate the Root CA Private Key

    - openssl genrsa -out rootCAPrivateKey.pem 4096
 
- Generate the Root CA Public Key

    - openssl req -new -x509 -config openssl.cnf -nodes -days 3650 -key rootCAPrivateKey.pem -out rootCAPublicKey.pem -subj "/CN=Root CA for IoT Edge" -extensions "v3_ca"

### Issuing CA

- Generate the Issuing CA Private Key and CSR

    - openssl req -newkey rsa:4096 -nodes -keyout issuingCAPrivateKey.pem -out issuingCertificateRequest.csr -subj "/CN=Issuing CA for IoT Edge"
 
- Generate the Issuing CA Public Key by signing the CSR from the Root CA

    - openssl ca -batch -config openssl.cnf -in issuingCertificateRequest.csr -days 180 -cert rootCAPublicKey.pem -keyfile rootCAPrivateKey.pem -keyform PEM -out issuingCAPublicKey.pem -extensions v3_intermediate_ca

### Generate Edge and Device CA

- Generate the Certificate Request for Edge CA and the Private Key.  Notes to be an Edge CA, it needs the extensions: CA and digitalSignature

    - openssl req -newkey rsa:4096 -nodes -keyout IoTEdgeCAPrivateKey.pem -out certificateRequest.csr -subj "/CN=IoT Edge Root CA certedgevm" --addext basicConstraints=critical,CA:TRUE,pathlen:2 --addext keyUsage=keyCertSign,digitalSignature --extensions v3_ca
 
- Sign the Certificate Request, insert a random Serial Number and Create the Public Key

    - openssl ca -batch -config openssl.cnf -in certificateRequest.csr -days 180 -cert issuingCAPublicKey.pem  -keyfile issuingCAPrivateKey.pem -keyform PEM -out IoTEdgeCAPublicKey.pem -extensions v3_intermediate_ca
 
- Create Chain
    - rm *.csr
    - cat IoTEdgeCAPublicKey.pem issuingCAPublicKey.pem rootCAPublicKey.pem  > IoTEdgeCAPublicKeyChain.pem

### Get thumbprint

- openssl x509 -in IoTEdgeCAPublicKey.pem -text -fingerprint

### Create IoT Edge Device

- Create another Ubuntu 20.04 VM named "certedgevm"

- Create new IoT Edge device in IoT Hub named "certedgevm"

- Copy cert files from "certrootvm" to "certedgevm"

    - scp ./IoTEdgeCAPublicKeyChain.pem jomit@10.0.0.7:/home/jomit
    - scp ./IoTEdgeCAPrivateKey.pem jomit@10.0.0.7:/home/jomit

### Install IoT Edge on "certedgevm"

- https://docs.microsoft.com/en-us/azure/iot-edge/how-to-provision-single-device-linux-x509?view=iotedge-2020-11&tabs=azure-portal%2Cubuntu#install-iot-edge

    - wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
    - sudo dpkg -i packages-microsoft-prod.deb
    - rm packages-microsoft-prod.deb

    - sudo apt-get update;
    - sudo apt-get install moby-engine

    - Update /etc/docker/daemon.json log file

    - sudo apt-get update;
    - sudo apt-get install aziot-edge


### Configure Certificates

- Edge CA
    - sudo cp /etc/aziot/config.toml.edge.template /etc/aziot/config.toml

    - sudo mkdir /etc/aziot/certificates
    - sudo cp IoTEdgeCAPublicKeyChain.pem /etc/aziot/certificates
    - sudo cp IoTEdgeCAPrivateKey.pem /etc/aziot/certificates
    - sudo chown aziotcs:aziotcs /etc/aziot/certificates/IoTEdgeCAPublicKeyChain.pem
    - sudo chown aziotks:aziotks /etc/aziot/certificates/IoTEdgeCAPrivateKey.pem
    - sudo chmod 660 /etc/aziot/certificates/IoTEdgeCAP*.pem
    - sudo nano /etc/aziot/config.toml

    - "Update the file as below"
        
            echo 'hostname = "EdgeHubHA"' > config.toml
            echo '[provisioning]' >> config.toml
            echo '  source = "manual"' >> config.toml
            echo '  connection_string = "HostName=youriothub.azure-devices.net;DeviceId=hostname;SharedAccessKey=+fdwfYOURKEYHEREwM="' >> config.toml
            echo '[edge_ca]' >> config.toml
            echo '  cert = "file:///etc/aziot/certificates/IoTEdgeCAPublicKeyChain.pem"' >> config.toml
            echo '  pk   = "file:///etc/aziot/certificates/IoTEdgeCAPrivateKey.pem"' >> config.toml


    - sudo rm /var/lib/aziot/edged/cache/provisioning_state
    - sudo iotedge config apply

    - sudo iotedge system status
    - sudo iotedge system logs
    - sudo iotedge check

    - openssl s_client -showcerts -servername 127.0.0.1 -connect 127.0.0.1:443 < /dev/null | grep CN
    