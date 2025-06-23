# SmogSense Deployment and Management Guide

## Overview
Automate cloud infrastructure provisioning and application deployment for SmogSense using:
- <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/terraform/terraform-original.svg" alt="Terraform" width="20"/> [**Terraform**](https://developer.hashicorp.com/terraform): Infrastructure provisioning
- <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/ansible/ansible-original.svg" alt="Ansible" width="20"/> [**Ansible**](https://docs.ansible.com/): Configuration management

**Access deployed dashboard:**  
`<public_ip>:8090`

## ⚙️ Environment Configuration
### Prerequisites
1. Clone repository:
   ```
   cd server_deployment
   ```
2. Configure environment variables:
   ```
   set -a
   source .env
   set +a
   ```

### Environment Variables
```
# Terraform Configuration
TF_VAR_subscription_id="your-subscription-id"
TF_VAR_resource_group="your-resource-group"
TF_VAR_location="Your Azure Region"  # e.g., "Switzerland North"
TF_VAR_admin_username="admin-user"
TF_VAR_admin_password="secure-password"

# Ansible Configuration
ANSIBLE_HOST="000.000.00.000"
ANSIBLE_SSH_PRIVATE_KEY_FILE="/path/to/vm_private_key.pem"
ANSIBLE_PYTHON_INTERPRETER="/usr/bin/python3"
```

---

## 🏗️ Terraform Workflow
### Initialize Terraform
```
cd terraform/azure # or other
terraform init
```

### Validate Configuration
```
terraform validate
```

### Apply Infrastructure Changes
```
terraform apply
```

### Destroy Specific Resources
```
terraform destroy \
  -target=azurerm_linux_virtual_machine.ubuntu_vm \
  -target=tls_private_key.ubuntu_vm_key
```

---

## ⚙️ Ansible Automation
### Inventory Configuration (`ansible/inventory.yaml`)
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

### Group Variables (`ansible/group_vars/ubuntu.yml`)
```yaml
smogsense_repo: "https://github.com/Luk-kar/SmogSense"
repository_dir: "/home/{{ ansible_user }}"
smogsense_dir: "{{ repository_dir }}/SmogSense"
```

### Playbook Execution
**Full deployment (first-time setup):**
```sh
ansible-playbook -i "./ansible/inventory.yaml" "./ansible/full_setup.yml"
```
This playbook executes all roles: `common`, `docker`, `xrdp`, `app`, `config`, and `deploy`.

**Target specific components:**
```sh
ansible-playbook -i "./ansible/inventory.yaml" "./ansible/full_setup.yml" --tags docker,deploy
```
Common tags: `common`, `docker`, `xrdp`, `app`, `config`, `deploy`.

**Upload example data to Superset:**
```sh
ansible-playbook -i "./ansible/inventory.yaml" "./ansible/upload_example_data.yml" --tags upload_data
```
*This playbook is designed to upload sample datasets and dashboards to the Superset BI tool. However, due to database password restrictions or missing permissions, the automatic upload may fail. In such cases, it is recommended to upload dashboards manually through the Superset user interface.*

**Stop services:**
```sh
ansible-playbook -i "./ansible/inventory.yaml" "./ansible/services_stop.yml"
```

**Resume from task:**
```sh
ansible-playbook -i "./ansible/inventory.yaml" "./ansible/upload_example_data.yml" \
  --start-at-task "Upload dashboard_social_media.zip to Superset BI tool"
```

---

## 🔧 Role Reference
| Role | Purpose |
|------|---------|
| `common` | Install system dependencies and updates |
| `docker` | Install Docker and Docker Compose |
| `xrdp` | Configure remote desktop access |
| `app` | Clone repository and prepare scripts |
| `config` | Manage environment/config files |
| `deploy` | Build images and start services |
| `browser` | Install Chromium and set as default |

## 🔐 SSH Management
**Connect to VM:**
```
ssh -i /path_to/vm_private_key.pem user@192.0.2.0
```

**Transfer files:**
```
scp /local/file user@192.0.2.0:/remote/path
```
**Host key management:**
```
ssh-keygen -R 192.0.2.1  # Remove old key
ssh adminuser@192.0.2.2   # Add new fingerprint
```
---

## Resource Monitoring

**Disk usage:**
```sh
df --total -h | awk '/total/ {print "Disk Used: " $3 " / " $2 " (" $5 " used)"}'
```
```
Disk Used: 45G / 100G (45% used)
```
**RAM usage:**
```sh
free -h | awk '/Mem:/ {printf("RAM Used: %s / %s (%.2f%% used)\n", $3, $2, $3/$2*100)}'
```
```
RAM Used: 6.2G / 16G (38.75% used)
```
**CPU usage:**
```sh
top -bn2 | grep '%Cpu' | tail -1 | awk '{used=100-$8; printf("CPU Used: %.2f%% / 100%% (Available: %.2f%%)\n", used, 100-used)}'
```
```
CPU Used: 23.45% / 100% (Available: 76.55%)

```

## 🖥️ Remote Access
Use [Remmina](https://remmina.org/) or similar tools for graphical remote desktop access.


> **Security Best Practice:**  
> Always remove old SSH host keys when recreating VMs to prevent "host key changed" warnings and mitigate IP reuse risks.