i# Infrastructure Setup Guide  
This project uses **Terraform** for infrastructure provisioning and **Ansible** for configuration management.

---

## Requirements

Ensure you have the following tools installed:

- **Terraform**: [Installation Guide](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- **Ansible**: [Installation Guide](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

---

## Run Terraform

Terraform manages infrastructure as code. Follow these steps to initialize, plan, and apply changes:

```bash
terraform init    # Initialize the working directory and download necessary providers
terraform plan    # Preview the infrastructure changes
terraform apply   # Apply the changes to provision infrastructure
```

# Run Ansible Manually
```bash
ansible-playbook -i hackathon, ansible_common/setup.yaml
```

