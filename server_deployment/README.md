
# SmogSense Deployment and Management Guide
provides a consolidated overview of the necessary commands and steps for setting up, deploying, and maintaining the SmogSense project. It aims to streamline operations by offering quick access to essential procedures for infrastructure management and application deployment.

## terraform usefull commands:
Terraform is an infrastructure-as-code tool that allows you to provision, validate, and manage cloud infrastructure in automated way.

Use these commands to: 

- initialize your Terraform environment:
```
terraform init
```
- check your configuration:
```
terraform validate
```
- apply infrastructure changes:
```
terraform apply
```
---
destroying the virtual machines instead of the all resourcess:
```
terraform destroy \
  -target=azurerm_linux_virtual_machine.ubuntu_vm \
  -target=tls_private_key.ubuntu_vm_key
```
## ansible usefull commands:
Ansible is an automation tool for configuring servers, deploying applications, and orchestrating complex workflows.

The following commands help you:

- load environment variables:
```
cd server_deployment
set -a
source .env
set +a
```
- server os setup:
```
ansible-playbook -i "./ansible/inventory.yaml" "./ansible/base_install.yml"
```
- create example configuration files:
```
ansible-playbook -i "./ansible/inventory.yaml" "./ansible/init_example_env_configs.yml"
```
- run services:
```
ansible-playbook -i "./ansible/inventory.yaml" "./ansible/services_deploy.yml"
```

## shh connection:
SSH (Secure Shell) is a cryptographic protocol that enables secure remote login and command execution on remote servers over an unsecured network.

Use the following command to securely connect to your remote virtual machine using your private SSH key:
```
cd server_deployment
ssh -i ./terraform/vm_private_key.pem user@198.51.100.1
```

## resource usage (RAM/CPU/DISK)
```
# Disk usage (used / total and percent used)
df --total -h | awk '/total/ {print "Disk Used: " $3 " / " $2 " (" $5 " used)"}'

# RAM usage (used / total and percent used)
free -h | awk '/Mem:/ {printf("RAM Used: %s / %s (%.2f%% used)\n", $3, $2, $3/$2*100)}'

# CPU usage (used / total and percent available)
top -bn2 | grep '%Cpu' | tail -1 | awk '{used=100-$8; printf("CPU Used: %.2f%% / 100%% (Available: %.2f%%)\n", used, 100-used)}'
```

## remote desktop connection
For a graphical remote desktop connection, you can use Remmina, a versatile remote desktop client.
https://remmina.org/