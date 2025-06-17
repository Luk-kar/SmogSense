# SmogSense Deployment and Management Guide

This guide provides a concise overview for setting up, deploying, and managing the SmogSense project using Terraform and Ansible. It is designed to streamline infrastructure provisioning and application deployment.


## Environment Setup

Load environment variables for deployment:

```sh
cd server_deployment
set -a
source .env
set +a
```

Ensure all required variables are set in `.env` (see `.env.example` for reference):

```sh
# Terraform Configuration
TF_VAR_subscription_id=your-subscription-id-here
TF_VAR_resource_group=your-resource-group-name-here
TF_VAR_location="Your Azure Region Here" # e.g., "Switzerland North"
TF_VAR_admin_username="your-admin-username-here"
TF_VAR_admin_password="your-secure-password-here"

# Ansible Configuration
ANSIBLE_HOST=000.000.00.000
ANSIBLE_SSH_PRIVATE_KEY_FILE="/some_path/.ssh/vm_private_key.pem"
ANSIBLE_PYTHON_INTERPRETER="/usr/bin/python3"
```
---

## Terraform Commands

Terraform automates cloud infrastructure provisioning.

**Initialize Terraform:**
```sh
cd terraform/azure  # or terraform/aws  or /gcp or /any_other_cloud_service, depending on your target
terraform init
```

**Validate configuration:**
```sh
terraform validate
```

**Apply infrastructure changes:**
```sh
terraform apply
```

**Destroy specific resources (e.g., only VMs and keys):**
```sh
terraform destroy \
  -target=azurerm_linux_virtual_machine.ubuntu_vm \
  -target=tls_private_key.ubuntu_vm_key
```
---

## Ansible Automation

Ansible manages server configuration and application deployment.

**Inventory and Variables**

- **Hosts and credentials:** Managed via `ansible/inventory.yaml` and group variables in `ansible/group_vars/ubuntu.yml`.
- **Environment variables:** Loaded from `server_deployment/.env`.

**Example inventory.yaml:**
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

**Example group_vars/ubuntu.yml:**
```yaml
smogsense_repo: "https://github.com/Luk-kar/SmogSense"
repository_dir: "/home/{{ ansible_user }}"
smogsense_dir: "{{ repository_dir }}/SmogSense"
```

### Ansible Workflow

**1. Load environment variables:**
```sh
cd server_deployment
set -a
source .env
set +a
```

**2. Run full setup (recommended for first-time deployment):**
```sh
ansible-playbook -i "./ansible/inventory.yaml" "./ansible/full_setup.yml"
```
This playbook executes all roles: `common`, `docker`, `xrdp`, `app`, `config`, and `deploy`.

**3. Run specific roles using tags:**
```sh
ansible-playbook -i "./ansible/inventory.yaml" "./ansible/full_setup.yml" --tags docker,deploy
```
Common tags: `common`, `docker`, `xrdp`, `app`, `config`, `deploy`.

**4. Upload example data to Superset BI tool:**
```sh
ansible-playbook -i "./ansible/inventory.yaml" "./ansible/upload_example_data.yml" --tags upload_data
```
*This playbook is designed to upload sample datasets and dashboards to the Superset BI tool. However, due to database password restrictions or missing permissions, the automatic upload may fail. In such cases, it is recommended to upload dashboards manually through the Superset user interface.*

**5. Stop all services:**
```sh
ansible-playbook -i "./ansible/inventory.yaml" "./ansible/services_stop.yml"
```

**6. Start from a specific task:**
```sh
ansible-playbook -i "./ansible/inventory.yaml" "./ansible/upload_example_data.yml" \
  --start-at-task "Upload dashboard_social_media.zip to Superset BI tool"
```

---

## Role Overview

- **common:** Installs system dependencies and updates packages.
- **docker:** Installs Docker and Docker Compose, configures user groups, and starts Docker.
- **xrdp:** Installs XFCE and XRDP for remote desktop access.
- **app:** Clones the SmogSense repository and prepares application scripts.
- **config:** Copies environment and configuration files.
- **deploy:** Runs tests, builds Docker images, and starts services via Docker Compose.
- **browser:** Updates the package index, installs the Chromium browser, and sets Chromium as the default browser for all users.

---

## SSH and File Transfer

**SSH to your VM:**
```sh
ssh -i /path_to/cloud_provider/vm_private_key.pem user@198.51.100.1
```

**Copy files to your VM:**
```sh
scp /path_to/file username@198.51.100.1:/path/to/destination
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
---

## Remote Desktop Access

For graphical remote desktop, use [Remmina](https://remmina.org/) or any other dedicated tool.

## Adding SSH Host Key Fingerprint

When recreating virtual machines with new IP addresses, always remove old SSH host keys using `ssh-keygen -R`. This practice:
- Prevents "host key changed" warnings that could mask genuine security threats
- Mitigates risks from IP address reuse in cloud environments (common with ephemeral instances)
- Maintains a clean `known_hosts` file by eliminating obsolete entries

**Remove old key:**
```sh
ssh-keygen -R 172.161.000.01
```

**Add new key fingerprint:**
```sh
ssh adminuser@172.161.000.02
# When prompted, accept the fingerprint with 'yes'
```