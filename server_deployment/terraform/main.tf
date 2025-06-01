variable "resource_group" {}
variable "location" {}
variable "subscription_id" {
  type      = string
  sensitive = true  # Obscures value in logs/outputs
}

variable "admin_username" {
  type      = string
  sensitive = true
}

variable "admin_password" {
  type      = string
  sensitive = true
}

# main.tf
# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group
  location = var.location
  tags = {
    environment = "dev"
    source      = "Terraform"
    owner       = "Data Engineer"
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# Virtual Network
resource "azurerm_virtual_network" "ubuntu_vm_vnet" {
  name                = "${var.resource_group}-vnet"
  location            = "${var.location}"
  resource_group_name = azurerm_resource_group.rg.name
  address_space       = ["10.0.0.0/16"]
  tags = {
    environment = "dev"
    component   = "network"
  }
}

# Subnet
resource "azurerm_subnet" "ubuntu_vm_subnet" {
  name                 = "${var.resource_group}-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.ubuntu_vm_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Public IP for VM
resource "azurerm_public_ip" "ubuntu_vm_ip" {
  name                = "Ubuntu-VM-ip"
  location            = "${var.location}"
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
  tags = {
    purpose = "vm-public-access"
  }
}

# Network Security Group
resource "azurerm_network_security_group" "ubuntu_vm_nsg" {
  name                = "Ubuntu-VM-nsg"
  location            = "${var.location}"
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  
  security_rule {
    name                       = "RDP"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3389"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    security_level = "production"
  }
}

# Network Interface
resource "azurerm_network_interface" "ubuntu_vm_nic" {
  name                = "${var.resource_group}-nic"
  location            = "${var.location}"
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.ubuntu_vm_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.ubuntu_vm_ip.id
  }
}

# SSH Key
resource "tls_private_key" "ubuntu_vm_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Save private key to local file
resource "local_file" "ssh_key" {
  filename        = "azure_vm_private_key.pem"
  content         = tls_private_key.ubuntu_vm_key.private_key_pem
  file_permission = "0600" # Restrict file permissions
}

# Output the private key (for verification)
output "ssh_private_key" {
  value     = tls_private_key.ubuntu_vm_key.private_key_pem
  sensitive = true # Prevents plaintext display in logs
}

# Virtual Machine
resource "azurerm_linux_virtual_machine" "ubuntu_vm" {
  name                            = "${var.resource_group}-vm"
  location                        = "${var.location}"
  resource_group_name             = azurerm_resource_group.rg.name
  size                            = "Standard_F4s_v2" # If more CPUs needed change the Regional Cores quota. Now set to default.
  admin_username                  = "${var.admin_username}"
  disable_password_authentication = false # to use remote desktop connection like Remmina
  admin_password                  = "${var.admin_password}"

  network_interface_ids = [
    azurerm_network_interface.ubuntu_vm_nic.id,
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = tls_private_key.ubuntu_vm_key.public_key_openssh
  }

  os_disk {
    name                 = "${var.resource_group}-osdisk"
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
    disk_size_gb         = 256
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  tags = {
    os_type    = "linux"
    os_distro  = "ubuntu"
    os_version = "22.04-LTS"
  }
}

# Associate NSG with Subnet
resource "azurerm_subnet_network_security_group_association" "nsg_assoc" {
  subnet_id                 = azurerm_subnet.ubuntu_vm_subnet.id
  network_security_group_id = azurerm_network_security_group.ubuntu_vm_nsg.id
}

output "public_ip_address" {
  value = azurerm_public_ip.ubuntu_vm_ip.ip_address
}