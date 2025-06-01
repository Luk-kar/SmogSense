
# SmogSense Deployment and Management Guide
Provides a consolidated overview of the necessary commands and steps for setting up, deploying, and maintaining the SmogSense project. It aims to streamline operations by offering quick access to essential procedures for infrastructure management and application deployment.

## environments

- load environment variables at ``server_deployment/.env`:
```
cd server_deployment
set -a
source .env
set +a
```

## terraform usefull commands:
Terraform is an infrastructure-as-code tool that allows you to provision, validate, and manage cloud infrastructure in automated way.

Use these commands to: 

- load environment variables at ``server_deployment/.env`:

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
## ansible useful commands

Ansible is an automation tool for configuring servers, deploying applications, and orchestrating complex workflows.

The main playbook, `ansible/full_setup.yml`, orchestrates the entire setup process, including system preparation, application deployment, configuration, and service startup. The roles are modular and reusable.

### **Inventory and Variables**

- Hosts and credentials are managed via `ansible/inventory.yaml` and group variables in `ansible/group_vars/ubuntu.yml`.
- Environment variables (such as host, username, password, and SSH key) are loaded from `server_deployment/.env`.

### **Basic Workflow**

1. **Load environment variables:**
   ```sh
   cd server_deployment
   set -a
   source .env
   set +a
   ```

2. **Run the full setup (recommended for first-time deployment or full re-provisioning):**
   ```sh
   ansible-playbook -i "./ansible/inventory.yaml" "./ansible/full_setup.yml"
   ```

   This playbook will:
   - Set up the base system (`common`, `docker`, `xrdp` roles)
   - Deploy the application code (`app` role)
   - Configure environment and application files (`config` role)
   - Deploy and start all services (`deploy` role)

3. **Run Individual Steps Using Tags, or Stop Services**

- **To run only a specific part of the setup, use Ansible tags with the `full_setup.yml` playbook.**  
  For example, to run only the Docker installation tasks (assuming those tasks are tagged `docker`):

  ```sh
  ansible-playbook -i "./ansible/inventory.yaml" "./ansible/full_setup.yml" --tags docker
  ```

- **Common tags you might use:**  
  (Replace with your actual tag names as defined in your playbook)
  - `common`
  - `docker`
  - `xrdp`
  - `app`
  - `config`
  - `deploy`

  Example to run only the deploy step:
  ```sh
  ansible-playbook -i "./ansible/inventory.yaml" "./ansible/full_setup.yml" --tags deploy
  ```

- **To stop all services:**  
  Use the provided `services_stop.yml` playbook:

  ```sh
  ansible-playbook -i "./ansible/inventory.yaml" "./ansible/services_stop.yml"
  ```

---

**Tip:**  
You can combine multiple tags with a comma:  
```sh
ansible-playbook -i "./ansible/inventory.yaml" "./ansible/full_setup.yml" --tags "docker,deploy"
```

### **Role Overview**

- **common**: Installs system dependencies and updates the package cache.
- **docker**: Installs Docker and Docker Compose, ensures the user is in the docker group, and starts the Docker service.
- **xrdp**: Installs and configures the XFCE desktop environment and XRDP for remote desktop access.
- **app**: Clones the SmogSense repository and prepares application scripts.
- **config**: Copies example environment and configuration files into place.
- **deploy**: Runs tests, builds Docker images, and starts all services via Docker Compose.

### **Inventory Example (`ansible/inventory.yaml`):**
```yaml
all:
  children:
    ubuntu:
      hosts:
        vm-ubuntu-smogsense:
          ansible_host: "{{ lookup('env', 'ANSIBLE_HOST') }}"
          ansible_user: "{{ lookup('env', 'TF_VAR_admin_username') }}"
          ansible_password: "{{ lookup('env', 'TF_VAR_admin_password') }}"
          ansible_ssh_private_key_file: "{{ lookup('env', 'ANSIBLE_SSH_PRIVATE_KEY_FILE') }}"
```

### **Group Variables Example (`ansible/group_vars/ubuntu.yml`):**
```yaml
smogsense_repo: "https://github.com/Luk-kar/SmogSense"
repository_dir: "/home/{{ ansible_user }}/smogsense-server"
smogsense_dir: "{{ repository_dir }}/SmogSense"
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